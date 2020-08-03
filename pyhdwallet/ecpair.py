""" Elliptic Curve Cryptography module """

import base58
from pyhdwallet import hashutils
from pyhdwallet import ecutils
from pyhdwallet.networks import Network

DEFAULT_NETWORK = Network.get_supported_networks()[0]


class ECPair:
    """
    Elliptic Curve Cryptography key pair
    """

    def __init__(self, privkey, pubkey_buffer=None, compressed=True,
                 network=DEFAULT_NETWORK):
        """
        Creates a new ECPair object.

        You should pass either public or private key.

        :param privkey: 32-byte secret as int, bytes or hex string
        :param pubkey_buffer: pubkey as bytes object (33 bytes for compressed
                              public key, 65 bytes for uncompressed public key)
        :param compressed When passing privkey, it indicates whether
                          compressed or uncompressed pubkeys will be used.
                          This arg is ignored when passing public key, because
                          the public key itself already tells that.
        :param network: Network object (e.g. bitcoin mainnet)
        """
        self.__compressed = compressed
        self.__privkey_buf = None
        self.__pubkey_buf = None

        # basic validations
        if not (privkey is None) ^ (pubkey_buffer is None):
            raise ValueError("Pass public key or private key, not both")
        if not network or network not in Network.get_supported_networks():
            raise ValueError("None or unsupported network")
        if compressed is not None and not isinstance(compressed, bool):
            raise ValueError("Compressed parameter should be bool or None")
        if pubkey_buffer is not None and not isinstance(pubkey_buffer, bytes):
            raise ValueError("pubkey should be bytes or None")

        if privkey is not None:
            if isinstance(privkey, str):
                privkey = int(privkey, 16)
            if isinstance(privkey, int):
                privkey = privkey.to_bytes(32, "big")
            if not isinstance(privkey, bytes) or \
                    len(privkey) != 32:
                raise ValueError("Invalid private key")
            self.__privkey_buf = privkey
            if compressed is None:
                self.__compressed = True

        if pubkey_buffer is not None:
            self.__compressed = ecutils.is_compressed_key(pubkey_buffer)
            self.__pubkey_buf = pubkey_buffer
        self.__network = network


    @property
    def pubkey_buffer(self):
        """
        Returns the public key (33 or 65 bytes)

        :return: bytes object representing the public key
        """
        if self.__pubkey_buf is None:
            self.__pubkey_buf = ecutils.get_pubkey_from_privkey(
                self.privkey, self.__compressed)
        return self.__pubkey_buf

    @property
    def privkey_buffer(self):
        """
        Returns the private key as bytes.

        :return: bytes object representing the private key
        """
        return self.__privkey_buf

    @property
    def privkey(self):
        """
        Returns the private key as a 256 bit integer.

        :return: 256 bit int secret
        """
        if self.__privkey_buf:
            return int.from_bytes(self.__privkey_buf, "big")
        return None

    @property
    def network(self):
        """
        Returns the network associated with this key pair.

        :return: Network object
        """
        return self.__network

    @property
    def compressed(self):
        """
        Returns whether or not the public key is in compressed format.

        :return: True for compressed; False otherwise
        """
        return self.__compressed

    @classmethod
    def from_wif(cls, wif):
        """
        Imports the private key from WIF format.

        :param wif: private key as WIF (Wallet Import Format)
        :return: New object containing the imported private key
        """
        buffer = base58.b58decode_check(wif)
        if len(buffer) != 34 and len(buffer) != 33:
            raise ValueError("invalid data")
        version = buffer[0:1]
        compressed = False
        if len(buffer) == 34:
            if buffer[-1:] != b'\x01':
                raise ValueError("invalid data")
            compressed = True

        if compressed:
            privkey = buffer[1:-1]
        else:
            privkey = buffer[1:]
        n = [x for x in Network.get_supported_networks() if version in [x.wif]]
        if not n:
            raise ValueError("Network not supported")

        return cls(privkey, pubkey_buffer=None,
                   compressed=compressed, network=n[0])

    def to_wif(self):
        """
        Exports the private key as WIF (Wallet Import Format)

        :return: string corresponding to the private Key as WIF
        """
        # WIF = base58check encode ([version byte][private key][checksum])
        if self.__privkey_buf is None:
            raise RuntimeError("No private key")
        buffer = b''
        buffer += self.network.wif
        buffer += self.privkey_buffer
        if self.__compressed:
            buffer += b'\x01'
        return base58.b58encode_check(buffer).decode()

    def get_address(self):
        """
        Converts the public key to a bitcoin address (P2PKH address)

        :return: Address as string (P2PKH address)
        """
        return base58.b58encode_check(
            self.network.pub_key_hash +
            hashutils.hash160(self.pubkey_buffer)).decode()

    def sign(self, hash_buffer):
        """
        Sign a 32 byte hash and returns a signature

        :param buffer: 32 byte buffer (as bytes)
        :return: ECSignature object
        """
        if self.privkey is None:
            raise RuntimeError("A private key is needed for this operation")
        ec_sig = ecutils.ECSignature.sign(self.privkey, hash_buffer)
        return ec_sig

    def verify(self, buffer, ec_signature):
        """
        Verify signature of a 32 byte buffer (as bytes)

        :param buffer: 32 byte buffer (as bytes)
        :param ec_signature: ECSignature object
        :return: True if this signature is valid
        """
        return ec_signature.verify(self.pubkey_buffer, buffer)

    def __eq__(self, other):
        return self.privkey == other.privkey and \
               self.pubkey_buffer == other.pubkey_buffer and \
               self.compressed == other.compressed and \
               self.network == other.network

    def __str__(self):
        return "{} (privKey={}, pubKey={}, compressed={}, network={})" \
            .format(self.__class__.__name__, self.privkey,
                    self.pubkey_buffer, self.__compressed, self.__network)
