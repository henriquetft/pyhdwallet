"""
Hash functions
"""
import hashlib
import hmac

def ripemd160(data):
    """
    RIPEMD-160 hash function.

    :param data:
    :return:
    """
    return hashlib.new('ripemd160', data).digest()


def sha256(data):
    """
    SHA-256 hash function.

    :param data:
    :return:
    """
    return hashlib.sha256(data).digest()


def hash160(data):
    """
    RIPEMD-160 after SHA-256.

    :param data:
    :return: ripemd160(sha256(data))
    """
    return ripemd160(sha256(data))


def hmac_sha512(key, msg):
    """
    HMAC using SHA-512.

    :param key:
    :param msg:
    :return:
    """
    return hmac.new(key, msg, hashlib.sha512).digest()
