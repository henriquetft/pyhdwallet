"""
Module to deal with Hierarchical Deterministic (HD) tree according to BIP32
specification (https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)
"""

import base58
from pyhdwallet import hashutils
from pyhdwallet import ecutils
from pyhdwallet.networks import Network
from pyhdwallet.ecpair import ECPair

# basic definitions
DEFAULT_NETWORK = Network.get_supported_networks()[0]
BITCOIN_SEED = b"Bitcoin seed"
HARDENED_BIT = 0x80000000


class HDNode:
    """
    A node from Hierarchical Deterministic (HD) tree.

    Each node has extended keys allowing derivation of children nodes
    """

    def __init__(self, keypair, chaincode, depth=0, index=0,
                 parent_fingerprint=0x00000000):
        self.keypair = keypair
        self.chain_code = chaincode
        self.depth = depth
        self.index = index
        self.parent_fingerprint = parent_fingerprint
        if depth == 0:
            if parent_fingerprint != 0x00000000:
                raise ValueError(
                    "Master node fingerprint should be 0x00000000")

    def neutered(self):
        """
        Returns a new node without the private key. (Removes the privkey)

        :return: a neutered HDNode
        """
        pub_key_buffer = self.keypair.pubkey_buffer
        # removing private key
        new_ecpair = ECPair(None, pub_key_buffer, network=self.keypair.network)
        return self.__class__(new_ecpair, self.chain_code, self.depth,
                              self.index, self.parent_fingerprint)

    def is_neutered(self):
        """
        Returns true if this object is neutered.

        :return: true if this object is neutered; false otherwise
        """
        return self.keypair.privkey is None


    def to_base58(self):
        """
        Returns the extended key (xpriv or xpub) as a Base58Check string.
        (xpub if neutered; xpriv otherwise)

        :return: Extended key as Base58Check string
        """
        net = self.keypair.network
        version = net.version_pub if self.is_neutered() else net.version_priv
        buffer = version.to_bytes(4, "big")
        buffer += self.depth.to_bytes(1, "big")
        buffer += self.parent_fingerprint.to_bytes(4, "big")
        buffer += self.index.to_bytes(4, "big")
        buffer += self.chain_code
        if self.is_neutered():  # public
            buffer += self.keypair.pubkey_buffer
        else:                   # private
            buffer += b'\x00'
            buffer += self.keypair.privkey_buffer
        assert len(buffer) == 78
        return base58.b58encode_check(buffer).decode()

    def get_keypair(self):
        """ Returns the keypair """
        return self.keypair

    def get_address(self):
        """
        Returns a P2PKH address

        :return: Address as string (P2PKH address)
        """
        return self.keypair.get_address()

    def get_identifier(self):
        """ Returns the identifier.
        Extended keys can be identified by the Hash160 (RIPEMD160 after
        SHA256) of the serialized ECDSA public key K.

        :return: identifier
         """
        return hashutils.hash160(self.keypair.pubkey_buffer)

    def get_fingerprint(self):
        """ Returns the fingerprint.
        The first 32 bits of the identifier are called the key fingerprint.

        :return: the fingerprint
        """
        return self.get_identifier()[:4]

    def derive(self, index):
        """
        Child Extended Key Derivation.
        Given the parent extended key and an index, computes the corresponding
        child extended key.

        :param index: index for derivation
        :return: HDNode child
        """
        buffer = b""
        network = self.keypair.network
        hardened = index >= HARDENED_BIT

        if hardened:
            # hardened derivation
            if self.is_neutered():
                raise RuntimeError(
                    "Neutered node cannot derive hardnened child")
            buffer += b"\x00"
            buffer += self.keypair.privkey_buffer
            buffer += index.to_bytes(4, "big")
        else:
            # normal derivation
            buffer += self.keypair.pubkey_buffer
            buffer += index.to_bytes(4, "big")

        i = hashutils.hmac_sha512(self.chain_code, buffer)
        il = i[:32]  # key
        ir = i[32:]  # chaincode
        parse256_il = int.from_bytes(il, "big")  # parse256(IL)

        # In case parse256(IL) >= n
        if parse256_il >= ecutils.ORDER:
            return self.derive(index+1)

        if self.is_neutered():
            # Public parent key ---> public child key
            try:
                pubkey_buf = ecutils.combine_pubkeys(
                    parse256_il, self.keypair.pubkey_buffer)
            except ValueError:  # POINT AT INFINITY
                return self.derive(index + 1)
            derived = ECPair(None, pubkey_buf, network=network)
        else:
            # private parent key ---> private child key
            new_key = (parse256_il + self.keypair.privkey) % ecutils.ORDER
            if new_key == 0:
                return self.derive(index + 1)
            derived = ECPair(new_key.to_bytes(32, "big"), None,
                             network=network)

        return self.__class__(derived, chaincode=ir, depth=self.depth + 1,
                              index=index,
                              parent_fingerprint=int.from_bytes(
                                  self.get_fingerprint(), "big"))

    def derive_hardened(self, index):
        """
        Child Extended Key Derivation. (hardened version)
        Given the parent extended key and an index, computes the corresponding
        child extended key.

        :param index: index for derivation
        :return: HDNode child
        """
        return self.derive(index + HARDENED_BIT)

    def derive_path(self, path):
        """ Child Extended Key Derivation.
        Given the derivation path in the format m/x/x' (e.g. m/0/1'/0) computes
        the corresponding child extended key.

        :param index: derivation path as string (e.g. m/0/1'/0)
        :return: HDNode child
        """
        obj = self
        indexes = path.split("/")[1:]
        for i in indexes:
            if i[-1:] in ["'", 'H', 'h']:
                num = int(i[:-1])
                obj = obj.derive_hardened(num)
            else:
                num = int(i)
                obj = obj.derive(num)
        return obj

    @classmethod
    def from_seed(cls, seed_bytes, network=DEFAULT_NETWORK):
        """
        Creates a new HDNode from a bip39 seed

        :param seed_bytes: binary bip39 seed
        :param network: Network object
        :return: new HDNode object
        """
        h = hashutils.hmac_sha512(BITCOIN_SEED, seed_bytes)
        privkey = h[:32]    # left
        chaincode = h[32:]  # right
        return cls(ECPair(privkey, network=network), chaincode)

    @classmethod
    def from_base58(cls, encoded):
        """
        Creates a new HDNode from a extended key (xpub/xpriv)

        :param encoded: a base58check string
        :return: a new HDNode object
        """
        buffer = base58.b58decode_check(encoded)
        if len(buffer) != 78:
            raise ValueError("Invalid argument")
        version = int.from_bytes(buffer[:4], "big")
        n = [x for x in Network.get_supported_networks() if
             version in [x.version_pub, x.version_priv]]
        if not n:
            raise ValueError("Network not supported")
        network = n[0]
        depth = buffer[4]
        parent_fingerprint = int.from_bytes(buffer[5:9], "big")
        index = int.from_bytes(buffer[9:13], "big")
        chain_code = buffer[13:45]
        key = buffer[45:]

        if version == network.version_pub:
            key_pair = ECPair(None, pubkey_buffer=key, network=network)
        else:
            #validate key[0] == 0x00
            key_pair = ECPair(key[1:], None, network=network)
        return cls(key_pair, chain_code, depth=depth, index=index,
                   parent_fingerprint=parent_fingerprint)

    def __eq__(self, other):
        return self.keypair == other.keypair \
               and self.chain_code == other.chain_code \
               and self.depth == other.depth \
               and self.index == other.index \
               and self.parent_fingerprint == other.parent_fingerprint

    def __str__(self):
        return f"{self.__class__.__name__} (keyPair={self.keypair}, "\
               f"chainCode={self.chain_code}," \
               f"depth={self.depth}, index={self.index}," \
               f"parentFingerprint={self.parent_fingerprint})"
