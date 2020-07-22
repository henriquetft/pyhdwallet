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


def _pubkey_point_to_bytes(public_key_point, compressed=True):
    """
    Converts public key point to bytes (compressed format)
    :param public_key_point:
    :return: public key in compressed format
    """
    arg_compr = 'compressed' if compressed else 'uncompressed'
    pki = VerifyingKey.from_public_point(public_key_point, curve=SECP256k1)
    pub_key = pki.to_string(encoding=arg_compr)
    return pub_key


def _pubkey_point_from_bytes(pubkey_buffer):
    """
    Returns the public key point from public key in compressed format
    :param pub_key: public key as bytes
    :return:
    """
    assert isinstance(pubkey_buffer, bytes)
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
    assert isinstance(pubkey_buffer, bytes)
    point_pubkey = _pubkey_point_from_bytes(pubkey_buffer)
    k = _point(secret) + point_pubkey
    if k is ellipticcurve.INFINITY:
        raise ValueError("Point at infinity")
    return _pubkey_point_to_bytes(k)


def get_pubkey_from_privkey(secret, compressed=True):
    """
    Returns a compressed public key from a private key
    :param secret: private key (32-bytes int)
    :return: public key as bytes
    """
    assert isinstance(secret, int)
    return _pubkey_point_to_bytes(_point(secret), compressed)


def is_compressed_key(pubkey_buffer):
    """
    Checks whether or not a public key is compressed
    :param pubkey_buffer: public keys as bytes obj.
    :return:
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
    return True if length == 33 else False
