""" ECDSA functions """
from ecdsa import SECP256k1, VerifyingKey, ellipticcurve

# domain parameters of the curve
ORDER = SECP256k1.order


def _point(secret):
    """
    Returns the public key point from private key
    :param secret: private key number (32-byte int)
    :return: public key point
    """
    assert isinstance(secret, int)
    public_key_point = secret * SECP256k1.generator
    return public_key_point


def _pubkey_point_to_bytes(public_key_point):
    """
    Converts public key point to bytes (compressed format)
    :param public_key_point:
    :return: public key in compressed format
    """
    pki = VerifyingKey.from_public_point(public_key_point, curve=SECP256k1)
    pub_key = pki.to_string(encoding='compressed')
    return pub_key


def _pubkey_point_from_bytes(pubkey_buffer):
    """
    Returns the public key point from public key in compressed format
    :param pub_key: public key in compressed format
    :return:
    """
    assert isinstance(pubkey_buffer, bytes) and len(pubkey_buffer) == 33
    vk_obj = VerifyingKey.from_string(pubkey_buffer, curve=SECP256k1)
    point_pk = vk_obj.pubkey.point
    return point_pk


def combine_pubkeys(secret, pubkey_buffer):
    """
    Combines the public keys.

    :param secret: private key (32-bytes int)
    :param pubkey_buffer: public key compressed
    :return: bytes of compressed public key
    """
    assert isinstance(secret, int)
    assert isinstance(pubkey_buffer, bytes) and len(pubkey_buffer) == 33
    point_pubkey = _pubkey_point_from_bytes(pubkey_buffer)
    k = _point(secret) + point_pubkey
    if k is ellipticcurve.INFINITY:
        raise ValueError("Point at infinity")
    return _pubkey_point_to_bytes(k)


def get_pubkey_from_privkey(secret):
    """
    Returns a compressed public key from a private key
    :param secret: private key (32-bytes int)
    :return: compressed public key
    """
    assert isinstance(secret, int)
    return _pubkey_point_to_bytes(_point(secret))


def is_valid_pubkey(pubkey_buffer):
    """
    Validate public key
    :param pubkey_buffer:
    :return:
    """
    return not isinstance(pubkey_buffer, bytes) or \
           len(pubkey_buffer) != 33 or \
           pubkey_buffer[0:1] not in [b"\x02", b"\x03"]
