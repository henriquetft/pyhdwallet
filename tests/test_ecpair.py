import unittest
import random
import base58
from pyhdwallet.ecpair import ECPair
from pyhdwallet.hashutils import sha256
from pyhdwallet.networks import Network, BITCOIN_TESTNET

unittest.TestLoader.sortTestMethodsUsing = None

COMPRESSED_PUBKEY = b"\x02" + bytes(random.getrandbits(8) for _ in range(32))
UNCOMPRESSED_PUBKEY = b"\x04" + bytes(random.getrandbits(8) for _ in range(64))
PRIVKEY_HEXA = "4ccbf2a1c6ee9a5106cb19c6be343947701a4e4acb2c4311f5a10836109711a1"


class TestConstructor(unittest.TestCase):
    def test_create_from_hexa(self):
        ecpair = ECPair(PRIVKEY_HEXA)
        self.assertEqual(ecpair.privkey_buffer, int(PRIVKEY_HEXA, 16).to_bytes(32, "big"))
        self.assertTrue(ecpair.compressed)

    def test_create_from_int(self):
        number = int(PRIVKEY_HEXA, 16)
        ecpair = ECPair(number)
        self.assertEqual(ecpair.privkey_buffer, number.to_bytes(32, "big"))

    def test_create_bytes(self):
        number = int(PRIVKEY_HEXA, 16)
        b = number.to_bytes(32, "big")
        self.assertEqual(ECPair(b).privkey_buffer, b)

    def test_privkey_compressed_none(self):
        ecpair = ECPair(PRIVKEY_HEXA, compressed=None)
        self.assertTrue(ecpair.compressed)

    def test_create_pass_both_keys(self):
        number = int(PRIVKEY_HEXA, 16)
        b = number.to_bytes(32, "big")
        with self.assertRaises(ValueError):
            ECPair(b, COMPRESSED_PUBKEY)

    def test_no_network(self):
        with self.assertRaises(ValueError):
            ECPair(PRIVKEY_HEXA, network=None)

    def test_unsupported_network(self):
        with self.assertRaises(ValueError):
            ECPair(PRIVKEY_HEXA, network=Network('a', 'b', 'c', 'd', 'e'))

    def test_no_keys(self):
        with self.assertRaises(ValueError):
            ECPair(None, pubkey_buffer=None)

    def test_pubkey_compressed(self):
        ecpair = ECPair(None, pubkey_buffer=COMPRESSED_PUBKEY)
        self.assertIsNotNone(ecpair)
        self.assertTrue(ecpair.compressed)

    def test_pubkey_ignore_compressed_passed(self):
        ecpair2 = ECPair(None, pubkey_buffer=COMPRESSED_PUBKEY,
                         compressed=False)
        self.assertIsNotNone(ecpair2)
        self.assertTrue(ecpair2.compressed)

    def test_pubkey_invalid_type(self):
        with self.assertRaises(ValueError):
            ECPair(None, pubkey_buffer='a')

    def test_pubkey_uncompressed(self):
        ecpair = ECPair(None, pubkey_buffer=UNCOMPRESSED_PUBKEY)
        self.assertIsNotNone(ecpair)
        self.assertFalse(ecpair.compressed)

    def test_arg_compressed_invalid(self):
        with self.assertRaises(ValueError):
            ecpair = ECPair(PRIVKEY_HEXA, compressed=1)

    def test_arg_invalid_privkey(self):
        with self.assertRaises(ValueError):
            ecpair = ECPair([], compressed=True)
        with self.assertRaises(ValueError):
            ecpair = ECPair(bytes(random.getrandbits(8) for _ in range(35)),
                            compressed=True)

    def test_arg_compressed_false(self):
        ecpair = ECPair(True, compressed=False)
        self.assertIsNotNone(ecpair)

    def test_arg_compressed_true(self):
        ecpair = ECPair(PRIVKEY_HEXA, compressed=True)
        self.assertIsNotNone(ecpair)

    def test_to_str(self):
        ecpair = ECPair(PRIVKEY_HEXA, compressed=True)
        a = "{}".format(ecpair)



class TestWIF(unittest.TestCase):
    def test_to_wif_compressed(self):
        ecpair = ECPair('ba8c65b5e47143979b3506a742b4bd95c1ddb419195915c3679e38e9bffbeb45')
        self.assertEqual(ecpair.to_wif(), 'L3ULUjNr4gfjcxFEJVo6bETbDvY6Z3wwU5oribqt692o9a5SHV2R')

    def test_to_wif_uncompressed(self):
        ecpair_uncomp = ECPair('ba8c65b5e47143979b3506a742b4bd95c1ddb419195915c3679e38e9bffbeb45', compressed=False)
        self.assertEqual(ecpair_uncomp.to_wif(), '5KESiB48wksvA4141nwrJGjjC5szu81fd3T2J8SaKqVW2zmxdCr')

    def test_to_wif_compressed_testnet(self):
        ecpair = ECPair('ba8c65b5e47143979b3506a742b4bd95c1ddb419195915c3679e38e9bffbeb45', network=BITCOIN_TESTNET)
        self.assertEqual(ecpair.to_wif(), 'cTqKweNhVkMznPiVgucDxYxer9qWDW3dY7xKq2JPbFgoQK8xhYqi')

    def test_to_wif_uncompressed_testnet(self):
        ecpair_uncomp = ECPair('ba8c65b5e47143979b3506a742b4bd95c1ddb419195915c3679e38e9bffbeb45', network=BITCOIN_TESTNET, compressed=False)
        self.assertEqual(ecpair_uncomp.to_wif(), '9315HusgXyx487WLe8qmAsHgqkEi4HYrxzJyNko5faEYp1dL1wL')

    def test_from_wif_compressed(self):
        ecpair = ECPair.from_wif('L3ULUjNr4gfjcxFEJVo6bETbDvY6Z3wwU5oribqt692o9a5SHV2R')
        self.assertEqual(ecpair.privkey, int('ba8c65b5e47143979b3506a742b4bd95c1ddb419195915c3679e38e9bffbeb45', 16))
        self.assertTrue(ecpair.compressed)

    def test_from_wif_uncompressed(self):
        ecpair = ECPair.from_wif('5KESiB48wksvA4141nwrJGjjC5szu81fd3T2J8SaKqVW2zmxdCr')
        self.assertEqual(ecpair.privkey, int('ba8c65b5e47143979b3506a742b4bd95c1ddb419195915c3679e38e9bffbeb45', 16))
        self.assertFalse(ecpair.compressed)

    def test_from_wif_invalid(self):
        # 32 bytes
        with self.assertRaises(ValueError):
            ECPair.from_wif('mdWSTVi6STwH9sLTF2zhRAg7AJUMKQsDgMeDc6sjaTgV7miXA')
        # 35 bytes
        with self.assertRaises(ValueError):
            ECPair.from_wif('3Yi64vA349642Ch7sPXUcpdDNmmfQg7XAw3bx1mVNL6hCQrFV4XQgy')
        # 34 bytes not started with \x01
        with self.assertRaises(ValueError):
            ECPair.from_wif('LWjVhLCGgaLZ3stB33SWvSFAvtkKWjsqET84r9Se5E96smt318gK')

    def test_from_wif_network_not_supported(self):
        b = b"\x00" + bytes(random.getrandbits(8) for _ in range(32))
        s = base58.b58encode_check(b)
        with self.assertRaises(Exception):
            ECPair.from_wif(s)

    def test_to_wif_no_privkey(self):
        ecpair = ECPair(None, pubkey_buffer=COMPRESSED_PUBKEY)
        with self.assertRaises(RuntimeError):
            ecpair.to_wif()


class TestSignatures(unittest.TestCase):
    def test_sign_verify_comp_mainnet(self):
        wif = 'KzHvGCQJWGr3NT8L83Kpj6KK245QTKeXPy1jGV14LRWd1XA74Ngy'
        self.assert_sign_verify(wif, b"I am Satoshi Nakamoto")

    def test_sign_verify_comp_testnet(self):
        wif = 'cRU6iqi2znWzj8Bo6onFqwBpSFJVm86ZH5onxaz7xAgJoJcaGJj4'
        self.assert_sign_verify(wif, b"I am Satoshi Nakamoto")

    def test_sign_verify_uncomp_mainnet(self):
        wif = '5K7PxxsDjJFCwAVkMHfpyQjXR4PbeNbJWY6b2EgfMzymhVj6k1q'
        self.assert_sign_verify(wif, b"I am Satoshi Nakamoto")

    def test_sign_verify_uncomp_testnet(self):
        wif = '92mz92fpCkevs6pK68N3Scf3gd5NHrnorE1YFLCk4LNVdpqA77j'
        self.assert_sign_verify(wif, b"I am Satoshi Nakamoto")

    def test_sign_verify_fail(self):
        wif = 'L3ULUjNr4gfjcxFEJVo6bETbDvY6Z3wwU5oribqt692o9a5SHV2R'
        wif2 = 'L3tJ46CAEaWr7YF5CZ6a1qg1cuhpeJEak5cr3esiVWA3To9PjWvn'
        ecpair = ECPair.from_wif(wif)
        ecpair2 = ECPair.from_wif(wif2)
        buffer = sha256(b"I am Satoshi Nakamoto")
        signature = ecpair.sign(buffer)
        self.assertFalse(ecpair2.verify(buffer, signature))

    def test_sign_no_privkey(self):
        wif = 'KzHvGCQJWGr3NT8L83Kpj6KK245QTKeXPy1jGV14LRWd1XA74Ngy'
        ecpair = ECPair.from_wif(wif)
        neutered_ecpair = ECPair(None, ecpair.pubkey_buffer)
        with self.assertRaises(RuntimeError):
            neutered_ecpair.sign(sha256(b'test'))


    def assert_sign_verify(self, wif, message):
        ecpair = ECPair.from_wif(wif)
        buffer = sha256(message)
        wrong_message = message[1:]
        signature = ecpair.sign(buffer)
        self.assertTrue(ecpair.verify(buffer, signature))
        self.assertFalse(ecpair.verify(sha256(wrong_message), signature))


if __name__ == '__main__':
    unittest.main()
