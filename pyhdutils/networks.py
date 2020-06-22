"""
Cryptocurrency network definitions
"""


class Network:
    """
    Represents a cryptocurrency network (e.g. Bitcoin Mainnet)
    """
    def __init__(self, description, version_priv, version_pub, pub_key_hash):
        self.description = description
        self.version_priv = version_priv
        self.version_pub = version_pub
        self.pub_key_hash = pub_key_hash

    def __eq__(self, other):
        return self.description == other.description and \
               self.version_priv == other.version_priv and \
               self.version_pub == other.version_pub and \
               self.pub_key_hash == other.pub_key_hash

    def __str__(self):
        return self.description


BITCOIN_MAINNET = Network(description="Bitcoin Mainnet",
                          version_priv=0x0488ADE4,
                          version_pub=0x0488B21E,
                          pub_key_hash=b"\x00")

BITCOIN_TESTNET = Network(description="Bitcoin Testnet",
                          version_priv=0x04358394,
                          version_pub=0x043587CF,
                          pub_key_hash=b"\x6F")

# supported networks
ALL_NETWORKS = [BITCOIN_MAINNET, BITCOIN_TESTNET]
