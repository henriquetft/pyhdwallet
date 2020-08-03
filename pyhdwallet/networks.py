"""
Cryptocurrency network definitions
"""

class Network:
    """
    Represents a cryptocurrency network (e.g. Bitcoin Mainnet)
    """
    def __init__(self, description, version_priv, version_pub, pub_key_hash,
                 wif):
        self.description = description
        self.version_priv = version_priv
        self.version_pub = version_pub
        self.pub_key_hash = pub_key_hash
        self.wif = wif

    @classmethod
    def get_supported_networks(cls):
        """
        Returns the list of supported networks

        :return: list of supported networks
        """
        return cls.__NETWORK_LIST

    @classmethod
    def set_supported_networks(cls, network_list):
        """
        Sets up the list of supported networks

        :param network_list: New list of supported networks
        """
        cls.__NETWORK_LIST = network_list

    def __eq__(self, other):
        return self.description == other.description and \
               self.version_priv == other.version_priv and \
               self.version_pub == other.version_pub and \
               self.pub_key_hash == other.pub_key_hash and \
               self.wif == other.wif

    def __str__(self):
        return self.description


BITCOIN_MAINNET = Network(description="Bitcoin Mainnet",
                          version_priv=0x0488ADE4,
                          version_pub=0x0488B21E,
                          pub_key_hash=b"\x00",
                          wif=b"\x80")

BITCOIN_TESTNET = Network(description="Bitcoin Testnet",
                          version_priv=0x04358394,
                          version_pub=0x043587CF,
                          pub_key_hash=b"\x6F",
                          wif=b"\xEF")

# supported networks
Network.set_supported_networks([BITCOIN_MAINNET, BITCOIN_TESTNET])
