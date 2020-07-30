import unittest
from pyhdwallet.ecpair import ECPair
from pyhdwallet.hashutils import sha256
from pyhdwallet.ecutils import ECSignature


class TestECSignature(unittest.TestCase):
    def test_msg1(self):
        # https://kjur.github.io/jsrsasign/sample/sample-ecdsa.html
        m = b"Bitcoin: A Peer-to-Peer Electronic Cash System"
        r = 16585169871999922969978897389792393736153195404500074220463475545187239063880
        s = 101989596681849864701598391615792467471854786825375833846457837318456308008154
        ecpair = ECPair(privkey='73d286994b2ac1a0f160fb45816c1dd6605551eb0ea12d5595a440a3665ef89d')
        self.assertVerify(ecpair.pubkey_buffer, r, s, m)

    def test_msg2(self):
        m = b"A purely peer-to-peer version of electronic cash would allow " \
            b"online payments"
        r = 53416277923213062165260564277038918077705079659558875401218116132761110201958
        s = 86605321333558372720412441800808448223714537838874906966097860970072205178705
        ecpair = ECPair(privkey='45d0475126e983f3162c98b73d93585e9c7be66220ba1e95dae87bbbff2fb40e')
        self.assertVerify(ecpair.pubkey_buffer, r, s, m)

    def test_msg3(self):
        m = b"What is needed is an electronic payment system based on " \
            b"cryptographic proof instead of trust"
        r = 68734943327797312301443474635907363454601483827607971122239706615210184455578
        s = 101235560920937280916292394003527251888819329338326063465504738929993008856598
        ecpair = ECPair(privkey='eb2bc889499f757cc135bd2da7aea647b3132a2dd330d1ed033d731a4cf2a737')
        self.assertVerify(ecpair.pubkey_buffer, r, s, m)

    def test_msg4(self):
        m = b"Maarten Bodewes generated this test vector on 2016-11-08"
        r = int('241097efbf8b63bf145c8961dbdf10c310efbb3b2676bbc0f8b08505c9e2f795', 16)
        s = int('021006b7838609339e8b415a7f9acb1b661828131aef1ecbc7955dfb01f3ca0e', 16)
        ecpair = ECPair(privkey='ebb2c082fd7727890a28ac82f6bdf97bad8de9f5d7c9028692de1a255cad3e0f')
        self.assertVerify(ecpair.pubkey_buffer, r, s, m)

    def assertVerify(self, pubkey_buffer, r, s, message):
        result = ECSignature(r, s).verify(pubkey_buffer, sha256(message))
        self.assertTrue(result)
        tampered_msg = message[1:]
        result2 = ECSignature(r, s).verify(pubkey_buffer, sha256(tampered_msg))
        self.assertFalse(result2)


if __name__ == '__main__':
    unittest.main()
