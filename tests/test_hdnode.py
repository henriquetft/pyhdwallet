import unittest
from binascii import unhexlify
from pyhdwallet.hdnode import HDNode
from pyhdwallet.ecpair import ECPair
from pyhdwallet.networks import BITCOIN_MAINNET
from unittest import mock
import random
from pyhdwallet import ecutils
from pyhdwallet import hashutils


unittest.TestLoader.sortTestMethodsUsing = None


# https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#test-vectors
TEST_VECTOR_1 = {
    "m": {
        "xpub": "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8",
        "xpriv": "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi"
    },
    "m/0H": {
        "xpub": "xpub68Gmy5EdvgibQVfPdqkBBCHxA5htiqg55crXYuXoQRKfDBFA1WEjWgP6LHhwBZeNK1VTsfTFUHCdrfp1bgwQ9xv5ski8PX9rL2dZXvgGDnw",
        "xpriv": "xprv9uHRZZhk6KAJC1avXpDAp4MDc3sQKNxDiPvvkX8Br5ngLNv1TxvUxt4cV1rGL5hj6KCesnDYUhd7oWgT11eZG7XnxHrnYeSvkzY7d2bhkJ7"
    },
    "m/0H/1": {
        "xpub": "xpub6ASuArnXKPbfEwhqN6e3mwBcDTgzisQN1wXN9BJcM47sSikHjJf3UFHKkNAWbWMiGj7Wf5uMash7SyYq527Hqck2AxYysAA7xmALppuCkwQ",
        "xpriv": "xprv9wTYmMFdV23N2TdNG573QoEsfRrWKQgWeibmLntzniatZvR9BmLnvSxqu53Kw1UmYPxLgboyZQaXwTCg8MSY3H2EU4pWcQDnRnrVA1xe8fs"
    },
    "m/0H/1/2H": {
        "xpub": "xpub6D4BDPcP2GT577Vvch3R8wDkScZWzQzMMUm3PWbmWvVJrZwQY4VUNgqFJPMM3No2dFDFGTsxxpG5uJh7n7epu4trkrX7x7DogT5Uv6fcLW5",
        "xpriv": "xprv9z4pot5VBttmtdRTWfWQmoH1taj2axGVzFqSb8C9xaxKymcFzXBDptWmT7FwuEzG3ryjH4ktypQSAewRiNMjANTtpgP4mLTj34bhnZX7UiM"
    },
    "m/0H/1/2H/2": {
        "xpub": "xpub6FHa3pjLCk84BayeJxFW2SP4XRrFd1JYnxeLeU8EqN3vDfZmbqBqaGJAyiLjTAwm6ZLRQUMv1ZACTj37sR62cfN7fe5JnJ7dh8zL4fiyLHV",
        "xpriv": "xprvA2JDeKCSNNZky6uBCviVfJSKyQ1mDYahRjijr5idH2WwLsEd4Hsb2Tyh8RfQMuPh7f7RtyzTtdrbdqqsunu5Mm3wDvUAKRHSC34sJ7in334"
    },
    "m/0H/1/2H/2/1000000000": {
        "xpub": "xpub6H1LXWLaKsWFhvm6RVpEL9P4KfRZSW7abD2ttkWP3SSQvnyA8FSVqNTEcYFgJS2UaFcxupHiYkro49S8yGasTvXEYBVPamhGW6cFJodrTHy",
        "xpriv": "xprvA41z7zogVVwxVSgdKUHDy1SKmdb533PjDz7J6N6mV6uS3ze1ai8FHa8kmHScGpWmj4WggLyQjgPie1rFSruoUihUZREPSL39UNdE3BBDu76"
    }
}

TEST_VECTOR_2 = {
    "m": {
        "xpub": "xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB",
        "xpriv": "xprv9s21ZrQH143K31xYSDQpPDxsXRTUcvj2iNHm5NUtrGiGG5e2DtALGdso3pGz6ssrdK4PFmM8NSpSBHNqPqm55Qn3LqFtT2emdEXVYsCzC2U"
    },
    "m/0": {
        "xpub": "xpub69H7F5d8KSRgmmdJg2KhpAK8SR3DjMwAdkxj3ZuxV27CprR9LgpeyGmXUbC6wb7ERfvrnKZjXoUmmDznezpbZb7ap6r1D3tgFxHmwMkQTPH",
        "xpriv": "xprv9vHkqa6EV4sPZHYqZznhT2NPtPCjKuDKGY38FBWLvgaDx45zo9WQRUT3dKYnjwih2yJD9mkrocEZXo1ex8G81dwSM1fwqWpWkeS3v86pgKt"
    },
    "m/0/2147483647H": {
        "xpub": "xpub6ASAVgeehLbnwdqV6UKMHVzgqAG8Gr6riv3Fxxpj8ksbH9ebxaEyBLZ85ySDhKiLDBrQSARLq1uNRts8RuJiHjaDMBU4Zn9h8LZNnBC5y4a",
        "xpriv": "xprv9wSp6B7kry3Vj9m1zSnLvN3xH8RdsPP1Mh7fAaR7aRLcQMKTR2vidYEeEg2mUCTAwCd6vnxVrcjfy2kRgVsFawNzmjuHc2YmYRmagcEPdU9"
    },
    "m/0/2147483647H/1": {
        "xpub": "xpub6DF8uhdarytz3FWdA8TvFSvvAh8dP3283MY7p2V4SeE2wyWmG5mg5EwVvmdMVCQcoNJxGoWaU9DCWh89LojfZ537wTfunKau47EL2dhHKon",
        "xpriv": "xprv9zFnWC6h2cLgpmSA46vutJzBcfJ8yaJGg8cX1e5StJh45BBciYTRXSd25UEPVuesF9yog62tGAQtHjXajPPdbRCHuWS6T8XA2ECKADdw4Ef"
    },
    "m/0/2147483647H/1/2147483646H": {
        "xpub": "xpub6ERApfZwUNrhLCkDtcHTcxd75RbzS1ed54G1LkBUHQVHQKqhMkhgbmJbZRkrgZw4koxb5JaHWkY4ALHY2grBGRjaDMzQLcgJvLJuZZvRcEL",
        "xpriv": "xprvA1RpRA33e1JQ7ifknakTFpgNXPmW2YvmhqLQYMmrj4xJXXWYpDPS3xz7iAxn8L39njGVyuoseXzU6rcxFLJ8HFsTjSyQbLYnMpCqE2VbFWc"
    },
    "m/0/2147483647H/1/2147483646H/2": {
        "xpub": "xpub6FnCn6nSzZAw5Tw7cgR9bi15UV96gLZhjDstkXXxvCLsUXBGXPdSnLFbdpq8p9HmGsApME5hQTZ3emM2rnY5agb9rXpVGyy3bdW6EEgAtqt",
        "xpriv": "xprvA2nrNbFZABcdryreWet9Ea4LvTJcGsqrMzxHx98MMrotbir7yrKCEXw7nadnHM8Dq38EGfSh6dqA9QWTyefMLEcBYJUuekgW4BYPJcr9E7j"
    }
}

TEST_VECTOR_3 = {
    "m": {
        "xpub": "xpub661MyMwAqRbcEZVB4dScxMAdx6d4nFc9nvyvH3v4gJL378CSRZiYmhRoP7mBy6gSPSCYk6SzXPTf3ND1cZAceL7SfJ1Z3GC8vBgp2epUt13",
        "xpriv": "xprv9s21ZrQH143K25QhxbucbDDuQ4naNntJRi4KUfWT7xo4EKsHt2QJDu7KXp1A3u7Bi1j8ph3EGsZ9Xvz9dGuVrtHHs7pXeTzjuxBrCmmhgC6"
    },
    "m/0H": {
        "xpub": "xpub68NZiKmJWnxxS6aaHmn81bvJeTESw724CRDs6HbuccFQN9Ku14VQrADWgqbhhTHBaohPX4CjNLf9fq9MYo6oDaPPLPxSb7gwQN3ih19Zm4Y",
        "xpriv": "xprv9uPDJpEQgRQfDcW7BkF7eTya6RPxXeJCqCJGHuCJ4GiRVLzkTXBAJMu2qaMWPrS7AANYqdq6vcBcBUdJCVVFceUvJFjaPdGZ2y9WACViL4L"
    }
}

class TestVector(unittest.TestCase):
    """ Base class to test BIP32 test vectors """
    LOG = False
    def execute_test(self, cases, path, node):
        expected_xpub = cases[path]["xpub"]
        expected_xpriv = cases[path]["xpriv"]
        child = node if path is None else node.derive_path(path)
        xpub = child.neutered().to_base58()
        xpriv = child.to_base58()
        self.assertEqual(expected_xpub, xpub)
        self.assertEqual(expected_xpriv, xpriv)
        if self.LOG:
            print("Chain", path, "(" + self.__class__.__name__+")")
            print("\text xpub: ", xpub)
            print("\text xpriv: ", xpriv)


class TestHDNode(unittest.TestCase):
    def setUp(self):
        seed = b'5636fa7760cca11a5ef1212c56fe0f5e576004e371b88a53780994ece7b6fe8f6923bd5ba3ab0688b0dbb865dbfef37894a39bf2ce9b11315c5413d510a1eee1'
        seed_buffer = unhexlify(seed)
        self.hdnode_from_seed = HDNode.from_seed(seed_buffer, BITCOIN_MAINNET)
        self.hdnode_from_base58 = HDNode.from_base58("xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")

    def test_creation(self):
        self.assertEqual(self.hdnode_from_seed, self.hdnode_from_base58)

    def test_creation_xpub(self):
        hdnode = HDNode.from_base58("xpub6DF8uhdarytz3FWdA8TvFSvvAh8dP3283MY7p2V4SeE2wyWmG5mg5EwVvmdMVCQcoNJxGoWaU9DCWh89LojfZ537wTfunKau47EL2dhHKon")
        self.assertIsInstance(hdnode, HDNode)

    def test_fromSeed(self):
        self.assertIsNotNone(self.hdnode_from_seed)
        self.assertEqual(self.hdnode_from_seed.get_address(), "17avao5dfvwuq1ugvo5wN7sUSNUjMa93BX")
        self.assertEqual(self.hdnode_from_seed.to_base58(), "xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")

    def test_address(self):
        self.assertEqual(self.hdnode_from_base58.get_address(), '17avao5dfvwuq1ugvo5wN7sUSNUjMa93BX')

    def test_keypair(self):
        self.assertIsInstance(self.hdnode_from_base58.get_keypair().privkey, int)
        self.assertIsInstance(self.hdnode_from_base58.get_keypair().pubkey_buffer, bytes)

    def test_abc(self):
        with self.assertRaises(ValueError):
            HDNode.from_base58("4Q1JnNwEpCghKERZ8esUgQxtMpncJ5YUBJx75PGQ2nCJNGXGVEN1Me6KJ6zaXcczxWSg9DmyzLxXFkXSSwMSPY4WL4sDAer2Cifdhum6LCsHjRxm")

    def test_string(self):
        self.assertIsInstance(str(self.hdnode_from_base58), str)

    def test_derive(self):
        path1 = self.hdnode_from_seed.derive(0).derive(1).to_base58()
        path2 = self.hdnode_from_seed.derive_path("m/0/1").to_base58()
        self.assertEqual(path1, path2)
        path1 = self.hdnode_from_seed.derive(0).derive_hardened(1).to_base58()
        path2 = self.hdnode_from_seed.derive_path("m/0/1'").to_base58()
        self.assertEqual(path1, path2)
        path1 = self.hdnode_from_seed.derive(0).derive_hardened(1).derive(
            0).to_base58()
        path2 = self.hdnode_from_seed.derive_path("m/0/1'/0").to_base58()
        self.assertEqual(path1, path2)

    def test_derive_neutered(self):
        path1 = self.hdnode_from_seed.derive(0).neutered().derive(1).to_base58()
        path2 = self.hdnode_from_seed.derive_path("m/0/1").neutered().to_base58()
        self.assertEqual(path1, path2)

    def test_from_base58_invalid_arg(self):
        with self.assertRaises(ValueError):
            self.hdnode_from_base58 = HDNode.from_base58("5FQT7TdYBPPpYJVsyfmdBw2e9wf8GtJnMToZf7Pun6LH5EAaa8KkQXGQQFygE2qWAdYzRiD7GPf8n1BmPGPVshLUazWMoacKhwaXH87u11ZfwM9TG")

    def test_derive_neutered_from_hardened(self):
        with self.assertRaises(RuntimeError):
            self.hdnode_from_seed.derive(0).neutered().derive_hardened(1)

    def test_constructor_invalid_fingerprint(self):
        privkey_hexa = "4ccbf2a1c6ee9a5106cb19c6be343947701a4e4acb2c4311f5"\
                       "a10836109711a1"
        number = int(privkey_hexa, 16)
        ecpair = ECPair(number)
        with self.assertRaises(ValueError):
            HDNode(ecpair, chaincode=b'\x1a\xbe\xc1YTQ\xa3\xe7\xb5\xfet'
                                     b'\xad5)\x06\x99\x81x,R\xd7L\x1e$\x10'
                                     b'\xc4\xf5\x1e\xa2\x08oO',
                   depth=0, index=0, parent_fingerprint=123)



class TestHDNodeVector1(TestVector):
    def setUp(self):
        seed = '000102030405060708090a0b0c0d0e0f'
        seed_buffer = unhexlify(seed)
        self.node = HDNode.from_seed(seed_buffer, BITCOIN_MAINNET)

    def test_chain_m(self):
        """ Test Chain m """
        self.execute_test(TEST_VECTOR_1, "m", self.node)

    def test_m_0h(self):
        """ Test Chain m/0H """
        self.execute_test(TEST_VECTOR_1, "m/0H", self.node)

    def test_m_0h_1(self):
        """ Chain m/0H/1 """
        self.execute_test(TEST_VECTOR_1, "m/0H/1", self.node)

    def test_m_0H_1_2H(self):
        """ Chain m/0H/1/2H """
        self.execute_test(TEST_VECTOR_1, "m/0H/1/2H", self.node)

    def test_m_0H_1_2H_2(self):
        """ Chain m/0H/1/2H/2 """
        self.execute_test(TEST_VECTOR_1, "m/0H/1/2H/2", self.node)

    def test_m_0H_1_2H_2_1000000000(self):
        """ Chain m/0H/1/2H/2/1000000000 """
        self.execute_test(TEST_VECTOR_1, "m/0H/1/2H/2/1000000000", self.node)


class TestHDNodeVector2(TestVector):
    def setUp(self):
        seed = 'fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542'
        seed_buffer = unhexlify(seed)
        self.node = HDNode.from_seed(seed_buffer, BITCOIN_MAINNET)

    def test_m(self):
        """ Test Chain m """
        self.execute_test(TEST_VECTOR_2, "m", self.node)

    def test_m_0(self):
        """ Test Chain m/0 """
        self.execute_test(TEST_VECTOR_2, "m/0", self.node)

    def test_m_0_2147483647H(self):
        """ Chain m/0/2147483647H """
        self.execute_test(TEST_VECTOR_2, "m/0/2147483647H", self.node)

    def test_m_0_2147483647H_1(self):
        """ Chain m/0/2147483647H/1 """
        self.execute_test(TEST_VECTOR_2, "m/0/2147483647H/1", self.node)

    def test_m_0_2147483647H_1_2147483646H(self):
        """ Chain m/0/2147483647H/1/2147483646H """
        self.execute_test(TEST_VECTOR_2, "m/0/2147483647H/1/2147483646H",
                          self.node)

    def test_m_0_2147483647H_1_2147483646H_2(self):
        """ Chain m/0/2147483647H/1/2147483646H/2 """
        self.execute_test(TEST_VECTOR_2, "m/0/2147483647H/1/2147483646H/2",
                          self.node)

class TestHDNodeVector3(TestVector):
    def setUp(self):
        seed = '4b381541583be4423346c643850da4b320e46a87ae3d2a4e6da11eba819cd4acba45d239319ac14f863b8d5ab5a0d0c64d2e8a1e7d1457df2e5a3c51c73235be'
        seed_buffer = unhexlify(seed)
        self.node = HDNode.from_seed(seed_buffer, BITCOIN_MAINNET)

    def test_chain_m(self):
        """ Test Chain m """
        self.execute_test(TEST_VECTOR_3, "m", self.node)

    def test_chain_m_0H(self):
        """ Test Chain m/0H """
        self.execute_test(TEST_VECTOR_3, "m/0H", self.node)


class TestHDNodeEdgeCases(TestVector):
    def setUp(self):
        self.orig = hashutils.hmac_sha512
        self.orig3 = ecutils.combine_pubkeys
        seed = b'5636fa7760cca11a5ef1212c56fe0f5e576004e371b88a53780994ece7b6fe8f6923bd5ba3ab0688b0dbb865dbfef37894a39bf2ce9b11315c5413d510a1eee1'
        seed_buffer = unhexlify(seed)
        self.hdnode_from_seed = HDNode.from_seed(seed_buffer, BITCOIN_MAINNET)
        self.hdnode_from_base58 = HDNode.from_base58("xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")

    def test_parse256_il_greater_order(self):
        hdnode = self.hdnode_from_seed.derive_path("m/0")
        with mock.patch('pyhdwallet.hashutils.hmac_sha512', self.__hmac_sha512_mock_parse256_il_order):
            hdnode = hdnode.derive(1)
        self.assertEqual(hdnode.index, 2)

    def test_privkey_equals_zero(self):
        hdnode = self.hdnode_from_seed.derive_path("m/0")
        with mock.patch('pyhdwallet.hashutils.hmac_sha512', self.__hmac_sha512_mock_privkey_equals_zero):
            hdnode = hdnode.derive(1)
        self.assertEqual(hdnode.index, 2)

    def test_combine_keys_point_infinity(self):
        hdnode = self.hdnode_from_seed.derive_path("m/0").neutered()
        with mock.patch('pyhdwallet.ecutils.combine_pubkeys', self.__combine_pubkeys_mock_point_infinity):
            hdnode = hdnode.derive(1)
        self.assertEqual(hdnode.index, 2)

    def __combine_pubkeys_mock_point_infinity(self, secret, pubkey_buffer):
        if secret == 43115047873401602166199352462699611922976203555531369294588215819284489537671:
            raise ValueError("Point at infinity")
        return self.orig3(secret, pubkey_buffer)

    def __hmac_sha512_mock_parse256_il_order(self, key, msg):
        if msg == b'\x02\x01W\xa6\xe8_\xf3\xd9\xd1\x913\xbbb\x88"\xa5\xf9\x7f\x1b\xb2\xc7\xeb\xe9K\xa5\x17\xff\x12\xa9\xe9e\x1f\x10\x00\x00\x00\x01':
            ppp = ecutils.ORDER.to_bytes(32, "big")
            ppp += bytes(random.getrandbits(8) for _ in range(32))
            return ppp
        return self.orig(key, msg)

    def __hmac_sha512_mock_privkey_equals_zero(self, key, msg):
        if msg == b'\x02\x01W\xa6\xe8_\xf3\xd9\xd1\x913\xbbb\x88"\xa5\xf9\x7f\x1b\xb2\xc7\xeb\xe9K\xa5\x17\xff\x12\xa9\xe9e\x1f\x10\x00\x00\x00\x01':
            dif = 71912227035807857345452825380777561902806637458756573929746293318995064139538
            ppp = dif.to_bytes(32, "big")
            ppp += bytes(random.getrandbits(8) for _ in range(32))
            return ppp
        return self.orig(key, msg)

if __name__ == '__main__':
    unittest.main()
