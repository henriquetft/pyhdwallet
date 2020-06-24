import unittest
from binascii import unhexlify
from pyhdutils.hdnode import HDNode
from pyhdutils.networks import BITCOIN_MAINNET

class TestHDNode(unittest.TestCase):
    def setUp(self):
        seed = b'5636fa7760cca11a5ef1212c56fe0f5e576004e371b88a53780994ece7b6fe8f6923bd5ba3ab0688b0dbb865dbfef37894a39bf2ce9b11315c5413d510a1eee1'
        seed_buffer = unhexlify(seed)
        self.hdnode_from_seed = HDNode.from_seed(seed_buffer, BITCOIN_MAINNET)
        self.hdnode_from_base58 = HDNode.from_base58("xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")

    def test_creation(self):
        self.assertEqual(self.hdnode_from_seed, self.hdnode_from_base58)

    def test_fromSeed(self):
        self.assertIsNotNone(self.hdnode_from_seed)
        self.assertEqual(self.hdnode_from_seed.get_address(), "17avao5dfvwuq1ugvo5wN7sUSNUjMa93BX")
        self.assertEqual(self.hdnode_from_seed.to_base58(), "xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")

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


if __name__ == '__main__':
    unittest.main()
