import unittest
from pyhdutils.hdnode import HDNode
from pyhdutils.networks import *
from binascii import unhexlify

class TestHDNode(unittest.TestCase):
    def setUp(self):
        seed = b'5636fa7760cca11a5ef1212c56fe0f5e576004e371b88a53780994ece7b6fe8f6923bd5ba3ab0688b0dbb865dbfef37894a39bf2ce9b11315c5413d510a1eee1'
        seed_buffer = unhexlify(seed)
        self.hdnodeFromSeed = HDNode.from_seed(seed_buffer, BITCOIN_MAINNET)
        self.hdnodeFromBase58 = HDNode.from_base58("xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")

    def test_creation(self):
        self.assertEqual(self.hdnodeFromSeed, self.hdnodeFromBase58)

    def test_fromSeed(self):
        self.assertIsNotNone(self.hdnodeFromSeed)
        self.assertEqual(self.hdnodeFromSeed.get_address(), "17avao5dfvwuq1ugvo5wN7sUSNUjMa93BX")
        self.assertEqual(self.hdnodeFromSeed.to_base58(), "xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")



if __name__ == '__main__':
    unittest.main()
