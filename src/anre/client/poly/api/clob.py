import time
from typing import Optional, Literal, Callable
from typing import overload, Union
import base64



from typing import Optional, Union
from pydantic import BaseModel

from py_clob_client.client import ClobClient as ClobInternalClient
from py_clob_client.clob_types import (
    ApiCreds,
    AssetType,
    BalanceAllowanceParams,
    OrderArgs,
    OrderType,
    OpenOrderParams,
    PriceHistoryArgs,
    TradeParams
)
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY,SELL
from anre.config.config import config as anre_config

def base64_encode(value: str) -> str:
    """
    Encodes a given string to Base64 format.
    :param value: The string to be encoded.
    :return: Base64-encoded string.
    """
    # Encode to bytes, then convert to Base64 and decode back to string
    return base64.b64encode(value.encode()).decode()


def base64_decode(encoded_value: str) -> str:
    """
    Decodes a Base64-encoded string back to its original form.
    :param encoded_value: The Base64 string to be decoded.
    :return: Decoded string.
    """
    # Decode Base64 to bytes, then decode bytes back to string
    return base64.b64decode(encoded_value).decode()




class ClobClient:
    _clob_internal_client: Optional[ClobInternalClient] = None

    def __init__(self):
        if self._clob_internal_client is None:
            self._clob_internal_client = self._create_clob_internal_client()
        assert isinstance(self._clob_internal_client, ClobInternalClient)

    @staticmethod
    def _create_clob_internal_client():
        polymarket_creds = anre_config.cred.get_polymarket_creds()
        api_client = ClobInternalClient(
            host=polymarket_creds['host'],
            key=polymarket_creds['pk'],
            chain_id=POLYGON,
            signature_type=1,
            funder=polymarket_creds['contract'],
        )
        api_creds = ApiCreds(
            api_key=polymarket_creds['ApiCreds']['key'],
            api_secret=polymarket_creds['ApiCreds']['secret'],
            api_passphrase=polymarket_creds['ApiCreds']['passphrase'],
        )
        # api_creds = client.create_or_derive_api_creds()
        api_client.set_api_creds(api_creds)
        return api_client

    def get_market(self, condition_id: str) -> dict:
        return self._clob_internal_client.get_market(condition_id=condition_id)

    def get_markets_chunk(self, next_cursor: str = "") -> dict:
        """Get available CLOB markets

        Please limit 50 request per 10 seconds.

        :param next_cursor: str, "" means the beginning and ‘LTE=’ means the end
        :return: dict with keys: data, next_cursor, count, limit
        """
        return self._clob_internal_client.get_markets(next_cursor=next_cursor)

    def get_sampling_markets_chunk(self, next_cursor: str = "") -> dict:
        """Get available CLOB markets that have rewards enabled. Single chunk.

        Please limit 50 request per 10 seconds.

        :param next_cursor: str, "" means the beginning and ‘LTE=’ means the end
        :return: dict with keys: data, next_cursor, count, limit
        """
        return self._clob_internal_client.get_sampling_markets(next_cursor=next_cursor)

    def get_simplified_markets_chunk(self, next_cursor: str = "") -> dict:
        """Get available CLOB markets expressed in a simplified schema. Single chunk."""
        return self._clob_internal_client.get_simplified_markets(next_cursor=next_cursor)

    def get_sampling_simplified_markets_chunk(self, next_cursor: str = "") -> dict:
        """Get available CLOB markets expressed in a simplified schema. Single chunk."""
        return self._clob_internal_client.get_sampling_simplified_markets(next_cursor=next_cursor)

    def get_order_book(self, token_id: str) -> dict:
        return self._clob_internal_client.get_order_book(token_id=token_id)

    def get_order_books(self, token_ids: list[str]) -> list[dict]:
        return self._clob_internal_client.get_order_books(token_ids=token_ids)

    def collect_chunks(self, fun: Callable, next_cursor: str = "", sleep_time: float = 0.3) -> list[dict]:
        data = []
        while next_cursor!="LTE=":
            result = fun(next_cursor=next_cursor)
            data.extend(result['data'])
            next_cursor = result['next_cursor']
            time.sleep(sleep_time)
        return data

    def get_order(self, order_id: str = None):
        return self._clob_internal_client.get_order(order_id=order_id)

    def get_orders_chunk(self, order_id: str = None, condition_id: str = None, asset_id: str = None, next_cursor: str = ""):
        params = OpenOrderParams(id=order_id, market=condition_id, asset_id=asset_id)
        return self._clob_internal_client.get_orders(params, next_cursor=next_cursor)

    def get_trades_chunk(self,
                    id: str = None,
                    maker_address: str = None,
                    market: str = None,
                    asset_id: str = None,
                    before: int = None,
                    after: int = None,
                    next_cursor: str = "MA=="
                   ):
        params = TradeParams(
            id=id,
            maker_address=maker_address,
            market=market,
            asset_id=asset_id,
            before=before,
            after=after,
        )
        trades = self._clob_internal_client.get_trades(
            params=params,
            next_cursor=next_cursor,
        )
        return trades

    def place_order(self, token_id: str, price: float, size: float, side: Literal["BUY", "SELL"], order_type: str = "GTC"):
        params = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id,
        )
        signed_order = self._clob_internal_client.create_order(params)
        assert order_type in OrderType.__dict__
        resp = self._clob_internal_client.post_order(signed_order, order_type)
        return resp

    def cancel_all(self):
        return self._clob_internal_client.cancel_all()

    def cancel_orders(self, order_ids: list[str]):
        return self._clob_internal_client.cancel_orders(order_ids=order_ids)

    def cancel_market_orders(self, condition_id: str = "", asset_id: str = ""):
        return self._clob_internal_client.cancel_market_orders(market=condition_id, asset_id=asset_id)

    def get_price_history(self, token_id: str, from_ts: int = None,
        to_ts: int = None,    interval: str = None,
        fidelity: int = None,):
        params = PriceHistoryArgs(market=token_id, startTs=from_ts, end=to_ts, interval=interval, fidelity=fidelity)
        price_history = self._clob_internal_client.get_price_history(params)
        return price_history

def __demo__():

    self = ClobClient()

    next_cursor = base64_encode(str(57050))
    markets_chunk = self.get_markets_chunk(next_cursor=next_cursor)
    markets_chunk = self.get_simplified_markets_chunk(next_cursor=next_cursor)

    markets_chunk = self.get_sampling_markets_chunk(next_cursor='')
    markets_chunk = self.get_sampling_simplified_markets_chunk(next_cursor='')

    market_dict = None
    for _market in markets_chunk['data']:
        if _market['active'] and _market['accepting_orders'] and _market['tokens'][0]['price'] > 0.1:
            market_dict = _market
            break
    assert market_dict

    condition_id = market_dict['condition_id']
    token_dict = market_dict['tokens'][0]
    token_id = token_dict['token_id']

    price_history = self.get_price_history(token_id=token_id, interval='1m', fidelity=10)
    order_book = self.get_order_book(token_id=token_id)

    orders_chunk = self.get_orders_chunk(condition_id=condition_id)
    assert orders_chunk['count'] == 0
    place_resp = self.place_order(
        token_id=token_id,
        price=0.1,
        size=10,
        side=BUY,
    )
    order = self.get_order(order_id=place_resp['orderID'])
    orders_chunk = self.get_orders_chunk(condition_id=condition_id)
    assert orders_chunk['count'] == 1

    self.cancel_market_orders(condition_id=condition_id)
    orders_chunk = self.get_orders_chunk(condition_id=condition_id)
    assert orders_chunk['count'] == 0


