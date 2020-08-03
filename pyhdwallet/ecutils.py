""" Low level Elliptic Curve Functions """

from random import SystemRandom
from ecdsa import SECP256k1, VerifyingKey, ellipticcurve
from ecdsa.ecdsa import Public_key, Private_key, Signature

# domain parameters of the curve (SECP256k1)
CURVE = SECP256k1
ORDER = CURVE.order
g = CURVE.generator


def _point(secret):
    """
    Returns the public key point from private key.

    :param secret: private key number (32-byte int)
    :return: public key point
    """
    assert isinstance(secret, int)
    public_key_point = secret * g
    return public_key_point


def _pubkey_point_to_bytes(public_key_point, compressed=True):
    """
    Converts public key point to bytes (compressed format).

    :param public_key_point:
    :return: public key in compressed format
    """
    arg_compr = 'compressed' if compressed else 'uncompressed'
    pki = VerifyingKey.from_public_point(public_key_point, curve=CURVE)
    pub_key = pki.to_string(encoding=arg_compr)
    return pub_key

def _pubkey_point_from_bytes(pubkey_buffer):
    """
    Returns the public key point from public key in compressed format.

    :param pub_key: public key as bytes
    :return:
    """
    assert isinstance(pubkey_buffer, bytes)
    vk_obj = VerifyingKey.from_string(pubkey_buffer, curve=CURVE)
    point_pk = vk_obj.pubkey.point
    return point_pk

def _hash_to_int(buffer):
    barr = bytearray(buffer)
    hexa = ''.join(['%02x' % b for b in barr])
    return int(hexa, 16)



def combine_pubkeys(secret, pubkey_buffer):
    """
    Combines the public keys.

    :param secret: private key (32-bytes int)
    :param pubkey_buffer: public key compressed
    :return: bytes of compressed public key
    """
    assert isinstance(secret, int)
    assert isinstance(pubkey_buffer, bytes)
    point_pubkey = _pubkey_point_from_bytes(pubkey_buffer)
    k = _point(secret) + point_pubkey
    if k is ellipticcurve.INFINITY:
        raise ValueError("Point at infinity")
    return _pubkey_point_to_bytes(k)


def get_pubkey_from_privkey(secret, compressed=True):
    """
    Returns a compressed public key from a private key.

    :param secret: private key (32-bytes int)
    :param compressed: get a compressed public key if true
    :return: public key as bytes
    """
    assert isinstance(secret, int)
    return _pubkey_point_to_bytes(_point(secret), compressed)


def is_compressed_key(pubkey_buffer):
    """
    Checks whether or not a public key is compressed.

    :param pubkey_buffer: public keys as bytes obj.
    :return: true if public key is compressed; false otherwise
    """
    if not isinstance(pubkey_buffer, bytes):
        raise ValueError
    length = len(pubkey_buffer)
    if length not in [33, 65]:
        raise ValueError("Invalid public key")
    if length == 33:
        if pubkey_buffer[0:1] not in [b"\x02", b"\x03"]:
            raise ValueError("Invalid public key")
    if length == 65:
        if pubkey_buffer[0:1] != b"\x04":
            raise ValueError("Invalid public key")
    return length == 33


class ECSignature:
    """ EC Signature """
    def __init__(self, r, s):
        assert isinstance(r, int)
        assert isinstance(s, int)
        self.r = r
        self.s = s

    def verify(self, pubkey_buffer, hash_buffer):
        """
        Verify a digital signature.

        :param pubkey_buffer: Public key as bytes
        :param hash_buffer: hash of the message
        :return: True if this signature is valid
        """
        assert isinstance(hash_buffer, bytes)
        assert isinstance(pubkey_buffer, bytes)
        hash_int = _hash_to_int(hash_buffer)
        point = _pubkey_point_from_bytes(pubkey_buffer)
        pk = Public_key(g, point)
        obj = Signature(self.r, self.s)
        return pk.verifies(hash_int, obj)

    @classmethod
    def sign(cls, secret, hash_buffer):
        """
        Sign a message (hash) with the provided private key and returns the
        signature.

        :param secret: private key as 32-byte int
        :param hash_buffer: Hash of the message as bytes
        :return: ECSignature object
        """
        assert isinstance(secret, int)
        assert isinstance(hash_buffer, bytes)
        hash_int = _hash_to_int(hash_buffer)
        pubkey = Public_key(g, g * secret)
        privkey = Private_key(pubkey, secret)
        random = SystemRandom().randrange(1, ORDER - 1)
        signature = privkey.sign(hash_int, random)
        return cls(signature.r, signature.s)
