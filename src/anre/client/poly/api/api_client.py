from typing import Optional, Literal
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
    OpenOrderParams,
    PriceHistoryArgs
)
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY,SELL

from anre.config.config import config as anre_config
from anre.client.poly.api.gamma import GammaMarketClient


class ApiClient:
    _clob_client_cls: Optional[ClobClient] = None

    def __init__(self):
        if self._clob_client_cls is None:
            self._clob_client_cls = self._create_clob_client_cls()
        assert isinstance(self._clob_client_cls, ClobClient)
        self._clob_client: ClobClient = self._clob_client_cls
        self.gamma = GammaMarketClient()

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

    def get_clob_market(self, condition_id: str):
        return self._clob_client.get_market(condition_id=condition_id)

    def get_clob_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_markets(next_cursor=next_cursor)

    def get_sampling_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_sampling_markets(next_cursor=next_cursor)

    def get_simplified_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_simplified_markets(next_cursor=next_cursor)

    def get_sampling_simplified_markets(self, next_cursor: str = "MA=="):
        return self._clob_client.get_sampling_simplified_markets(next_cursor=next_cursor)

    def get_orders(self, id: str = None, market: str = None, asset_id: str = None, next_cursor: str = "MA=="):
        return self._clob_client.get_orders(OpenOrderParams(id=id, market=market, asset_id=asset_id), next_cursor=next_cursor)

    def get_order(self, order_id: str = None):
        return self._clob_client.get_order(order_id=order_id)

    def place_order(self, token_id: str, price: float, size: float, side: Literal["BUY", "SELL"], order_type: str = "GTC"):
        order_args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id,
        )
        signed_order = self._clob_client.create_order(order_args)
        assert order_type in OrderType.__dict__
        resp = self._clob_client.post_order(signed_order, order_type)
        return resp



def __dummy__():

    self = ApiClient()

    markets = self.get_clob_markets()
    len(markets)
    market_dict = markets['data'][0]

    markets = self.get_sampling_markets()
    market_dict = markets['data'][0]

    markets = self.get_simplified_markets()
    market_dict = markets['data'][0]

    markets = self.get_sampling_simplified_markets()
    market_dict = markets['data'][0]




    self.gamma.get_events(slug="what-will-powell-say-during-june-press-conference")
    self.gamma.get_markets(slug="will-powell-say-inflation-40-times-during-june-press-conference")
    market = self.gamma.get_market('542930')
    condition_id = market['conditionId']
    market = self.get_clob_market(condition_id=condition_id)
    token_id = market['tokens'][0]['token_id']


    price_history = self._clob_client.get_price_history(PriceHistoryArgs(market=token_id, interval='1m', fidelity=10))
    trades = self._clob_client.get_trades()

    self._clob_client.get_last_trade_price(token_id=token_id)

    order_book = self._clob_client.get_order_book(token_id=token_id)
    self._clob_client.get_order_book_hash(order_book)
    self._clob_client.time




    place_resp = self.place_order(
        token_id=token_id,
        price=0.1,
        size=100,
        side=BUY,
    )

    order = self.get_order(order_id=place_resp['orderID'])

    self.get_orders()
    self.cancel_all()


