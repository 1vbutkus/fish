from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.data import DataClient
from anre.connection.polymarket.api.gamma import GammaClient


class MasterClient:
    clob_client = ClobClient()
    data_client = DataClient()
    gamma_client = GammaClient()

    def __init__(self):
        pass


def __dummy__():
    self = MasterClient()

    self.clob_client.get_sampling_simplified_markets_info_list()
    self.clob_client.get_market_info_chunk()
