"""
Main module that contains HDNode class
"""

import base58
from pyhdutils import hashutils
from pyhdutils.networks import ALL_NETWORKS
from pyhdutils import ecutils

BITCOIN_SEED = "Bitcoin seed".encode()
HARDENED_BIT = 0x80000000


class ECPair:
    """
    Elliptic Curve Cryptography key pair
    """
    def __init__(self, privkey_buffer, pubkey_buffer=None, network=None):
        """
        Creates a new ECPair object

        :param privkey_buffer: bytes obj. with the private key (32 bytes)
        :param pubkey_buffer: bytes obj. the compressed public key (33 bytes)
        :param network: Network object (e.g. bitcoin mainnet)
        """
        self.__privkey_buf = None
        self.__pubkey_buf = None
        if not network:
            raise ValueError("Unspecified network")
        if privkey_buffer:
            if not isinstance(privkey_buffer, bytes) or \
                    len(privkey_buffer) != 32:
                raise ValueError("Invalid private key")
            self.__privkey_buf = privkey_buffer
        if pubkey_buffer:
            if ecutils.is_valid_pubkey(pubkey_buffer):
                raise ValueError("Invalid format of public key")
            self.__pubkey_buf = pubkey_buffer
        self.__network = network

    @property
    def pubkey_buffer(self):
        """
        Returns the compressed public key (33 bytes)
        :return: bytes object representing the public key
        """
        if self.__pubkey_buf is None:
            self.__pubkey_buf = ecutils.get_pubkey_from_privkey(self.privkey)
        return self.__pubkey_buf

    @property
    def privkey_buffer(self):
        """
        Returns the private key as bytes
        :return: bytes object representing the private key
        """
        return self.__privkey_buf

    @property
    def privkey(self):
        """
        Returns the private key as a 256 bit integer
        :return: 256 bit int representing private key
        """
        if self.__privkey_buf:
            return int.from_bytes(self.__privkey_buf, "big")
        return None

    @property
    def network(self):
        """
        Returns the network associated with this key pair
        :return: Network object
        """
        return self.__network

    @classmethod
    def from_wif(cls, string, network):
        """
        Import keys from WIF format.

        :param string:
        :param network:
        :return: New object containing the imported private key
        """
        raise NotImplementedError

    def to_wif(self):
        """
        Export private key to WIF (Wallet Export Format)
        :return:
        """
        if self.__privkey_buf is None:
            raise ValueError("No private key")
        raise NotImplementedError

    def get_address(self):
        """
        Converts the public key to a bitcoin address (P2PKH address)
        :return: Address as string (P2PKH address)
        """
        return base58.b58encode_check(
            self.network.pub_key_hash +
            hashutils.hash160(self.pubkey_buffer)).decode()

    def __eq__(self, other):
        return self.privkey == other.privkey and \
               self.pubkey_buffer == other.pubkey_buffer and \
               self.network == other.network

    def __str__(self):
        return "{} (privKey={}, pubKey={}, network={})" \
            .format(self.__class__.__name__, self.privkey,
                    self.pubkey_buffer, self.__network)


class HDNode:
    """
    A node from Hierarchical Deterministic (HD) tree.

    Each node has extended keys allowing derivation of children nodes
    """

    SUPPORTED_NETWORKS = ALL_NETWORKS[:]

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
        new_ecpair = ECPair(None, pub_key_buffer, self.keypair.network)
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
                raise ValueError("Neutered node cannot derive hardnened child")
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
                              index=self.index,
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

    @classmethod
    def from_seed(cls, seed_bytes, network):
        """
        Creates a new HDNode from a bip39 seed

        :param seed_bytes: binary bip39 seed
        :param network:
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
        n = [x for x in cls.SUPPORTED_NETWORKS if
             version in [x.version_pub, x.version_priv]]
        if not n:
            raise Exception("Network not supported")
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
