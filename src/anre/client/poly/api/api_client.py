from typing import Optional
from typing import overload, Union


from typing import Optional, Union
from pydantic import BaseModel

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    ApiCreds,
    AssetType,
    BalanceAllowanceParams,
    OrderArgs,
    OrderType,
)
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY

from anre.config.config import config as anre_config



class ApiClient:
    _clob_client_cls: Optional[ClobClient] = None

    def __init__(self):
        if self._clob_client_cls is None:
            self._clob_client_cls = self._create_clob_client_cls()
        assert isinstance(self._clob_client_cls, ClobClient)
        self._clob_client: ClobClient = self._clob_client_cls

    def _create_clob_client_cls(self):
        polymarket_creds = anre_config.cred.get_polymarket_creds()
        api_client = ClobClient(
            host=polymarket_creds['host'],
            key=polymarket_creds['pk'],
            chain_id=POLYGON,
            signature_type=1,
            funder=polymarket_creds['contract'],
        )
        api_creds = ApiCreds(
            api_key=polymarket_creds['ApiCreds']['api_key'],
            api_secret=polymarket_creds['ApiCreds']['api_secret'],
            api_passphrase=polymarket_creds['ApiCreds']['api_passphrase'],
        )
        # api_creds = client.create_or_derive_api_creds()
        api_client.set_api_creds(api_creds)
        return api_client

    def cancel_all(self):
        self._clob_client.cancel_all()

    def get_clob_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_markets(next_cursor=next_cursor)

    def get_sampling_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_sampling_markets(next_cursor=next_cursor)

    def get_simplified_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_simplified_markets(next_cursor=next_cursor)

    def get_sampling_simplified_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_sampling_simplified_markets(next_cursor=next_cursor)

    def get_pr(self):
        return self._clob_client.get_prices()



def __dummy__():

    self = ApiClient()

    markets = self.get_clob_markets()
    market_dict = markets['data'][0]

    markets = self.get_sampling_markets()
    market_dict = markets['data'][0]

    markets = self.get_simplified_markets()
    market_dict = markets['data'][0]

    markets = self.get_sampling_simplified_markets()
    market_dict = markets['data'][0]
