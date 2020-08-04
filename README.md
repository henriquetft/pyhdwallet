# pyhdwallet


A Python lib for working with [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) (Hierarchical Deterministic Wallets)

This project aims to provide an API similar to [bitcoincashjs2-lib](https://github.com/Bitcoin-com/bitcoincashjs2-lib) 
concerning HD utilities.

**Don't trust. Verify.**


## Sample Usage
```python
>>> from binascii import unhexlify
>>> from pyhdwallet import ECPair, HDNode
>>> from pyhdwallet.hashutils import sha256
>>> from pyhdwallet.networks import BITCOIN_TESTNET
>>> 
>>> 
>>> SEED = b'5636fa7760cca11a5ef1212c56fe0f5e576004e371b88a53780994ece7b6fe8f6923bd5ba3ab0688b0dbb865dbfef37894a39bf2ce9b11315c5413d510a1eee1'
>>> seed_buffer = unhexlify(SEED)
>>> 
>>> hdnode = HDNode.from_seed(seed_buffer)
>>> print("xprv:", hdnode.to_base58())
xprv: xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg
>>> print("xpub:", hdnode.neutered().to_base58())
xpub: xpub661MyMwAqRbcEostTtXtcUMQRMLqZgZ7gmT3bmqRtvMdsqjD9tvW46xrS53Se68UQLRAYGjSkpm5Cje9We12dE3CAK1p4W3xFauG5aX1Z8u
>>> print("address:", hdnode.get_address())
address: 17avao5dfvwuq1ugvo5wN7sUSNUjMa93BX
>>> 
>>> hdnode_testnet = HDNode.from_seed(seed_buffer, network=BITCOIN_TESTNET)
>>> print("tprv (testnet):", hdnode_testnet.to_base58())
tprv (testnet): tprv8ZgxMBicQKsPd92x2RrPQz2fBSvZPjsGf6SZforGpZK8ne99bix1241pVxr42tpDyyCXoWVNqRDYanbg1snq4cdwYdGXTKPUcAGxkXczrnh
>>> 
>>> hdnode2 = HDNode.from_base58("xprv9s21ZrQH143K2KoRMrztFLQfsKWMADqGKYXSoPRpLapf13Q4cMcFWJeNangQ2XRucXfkoQscg4dk7w3vtfStFZNM1z4DnxfRh4XYJkT1gAg")
>>> 
>>> child = hdnode.derive_path("m/0/1'/1")
>>> print("address child:", child.get_address())
address child: 14fW6kaeFiPees7FWNkvNFxewqhX7zSj2r
>>> print("child hdnode: ", child)
child hdnode:  HDNode (keyPair=ECPair (privKey=85992014414924097038377675237145575004969559361289161063865857372311461164262, pubKey=b'\x02E\x8aEg\xc9\x03\xaf@\x12\xe1\xa4a"}\xfa1)\xfcM\x1e.\x05\xe6\x11\xcc\xac\x17\xdf\xc2\x02\xb12', compressed=True, network=Bitcoin Mainnet), chainCode=b'\xe9>(\x84\xb2\x83"\x80c8)\xdb\xbf\x1d\xe8\xa9*1\x15\x10s\xc5x\xb1E\xfc)ONuC>',depth=3, index=1,parentFingerprint=1079081844)
>>> 
>>> ecpair = child.get_keypair()
>>> print("public key:", ecpair.pubkey_buffer)
public key: b'\x02E\x8aEg\xc9\x03\xaf@\x12\xe1\xa4a"}\xfa1)\xfcM\x1e.\x05\xe6\x11\xcc\xac\x17\xdf\xc2\x02\xb12'
>>> print("wif:", ecpair.to_wif())
wif: L3bGjEiQ6TynvKskm567Kh2rKrrs2JmgACV81Zb6MFFx9JyMnJNV
>>> ecpair2 = ECPair.from_wif("L1HZ6Vo7RJtXBzx75o2N2AhpXFVVuXVatqu6Xsy4iWNtmPphhJiz")
>>> print("wif2:", ecpair2.to_wif())
wif2: L1HZ6Vo7RJtXBzx75o2N2AhpXFVVuXVatqu6Xsy4iWNtmPphhJiz
>>> 
>>> signature = ecpair.sign(sha256(b"Message"))
>>> print("signature valid:", ecpair.verify(sha256(b"Message"), signature))
signature valid: True
```

## Documentation
See the [documentation](https://henriquetft.github.io/pyhdwallet/) for more info.
