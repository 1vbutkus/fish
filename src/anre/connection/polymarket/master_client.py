from typing import Optional

from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.data import DataClient
from anre.connection.polymarket.api.gamma import GammaClient
from anre.utils.decorators import singleton


@singleton
class MasterClient:
    clob_client: Optional[ClobClient] = None
    data_client: Optional[DataClient] = None
    gamma_client: Optional[GammaClient] = None

    def __init__(self):
        if self.clob_client is None:
            self.clob_client = ClobClient()
        if self.data_client is None:
            self.data_client = DataClient()
        if self.gamma_client is None:
            self.gamma_client = GammaClient()

    @classmethod
    def get_clob_client(cls) -> ClobClient:
        if cls.clob_client is None:
            cls.clob_client = ClobClient()
        return cls.clob_client


def __dummy__():
    self = MasterClient()

    self.clob_client.get_sampling_simplified_markets_info_list()
    self.clob_client.get_market_info_chunk()
