import base64
import time
from typing import Callable, Literal, Optional
from functools import partial

from py_clob_client.client import ClobClient as ClobInternalClient
from py_clob_client.clob_types import (
    ApiCreds,
    OpenOrderParams,
    OrderArgs,
    OrderType,
    PriceHistoryArgs,
    TradeParams,
)
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY, SELL

from anre.config.config import config as anre_config

assert BUY == 'BUY'
assert SELL == 'SELL'


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

    def get_market_info(self, condition_id: str) -> dict:
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

    def get_market_order_book(self, token_id: str) -> dict:
        return self._clob_internal_client.get_order_book(token_id=token_id)

    def get_mob_list(self, token_ids: list[str]) -> list[dict]:
        return self._clob_internal_client.get_order_books(token_ids=token_ids)

    def collect_chunks(
        self, fun: Callable, next_cursor: str = "", sleep_time: float = 0.3
    ) -> list[dict]:
        data = []
        while next_cursor != "LTE=":
            result = fun(next_cursor=next_cursor)
            data.extend(result['data'])
            next_cursor = result['next_cursor']
            if next_cursor != "LTE=":
                time.sleep(sleep_time)
        return data

    def get_our_order(self, order_id: str = None):
        return self._clob_internal_client.get_order(order_id=order_id)

    def get_house_orders(self, order_id: str = None,
                         condition_id: str = None,
                         asset_id: str = None,
                         next_cursor: str = "",
                         sleep_time=0.3,
                         ):
        return self.collect_chunks(
            fun=partial(
                self.get_our_orders_chunk,
                order_id=order_id,
                condition_id=condition_id,
                asset_id=asset_id,
            ),
            next_cursor=next_cursor,
            sleep_time=sleep_time,
        )

    def get_our_orders_chunk(
        self,
        order_id: str = None,
        condition_id: str = None,
        asset_id: str = None,
        next_cursor: str = "",
    ):
        params = OpenOrderParams(id=order_id, market=condition_id, asset_id=asset_id)
        return self._clob_internal_client.get_orders(params, next_cursor=next_cursor)

    def get_our_trades_chunk(
        self,
        id: str = None,
        maker_address: str = None,
        market: str = None,
        asset_id: str = None,
        before: int = None,
        after: int = None,
        next_cursor: str = "MA==",
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

    def place_order(
        self,
        token_id: str,
        price: float,
        size: float,
        side: Literal["BUY", "SELL"],
        order_type: str = "GTC",
    ):
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

    def cancel_orders_all(self):
        return self._clob_internal_client.cancel_all()

    def cancel_orders_by_id(self, order_ids: list[str]):
        return self._clob_internal_client.cancel_orders(order_ids=order_ids)

    def cancel_orders_by_market(self, condition_id: str = "", asset_id: str = ""):
        return self._clob_internal_client.cancel_market_orders(
            market=condition_id, asset_id=asset_id
        )

    def get_price_history(
        self,
        token_id: str,
        from_ts: int = None,
        to_ts: int = None,
        interval: str = None,
        fidelity: int = None,
    ):
        params = PriceHistoryArgs(
            market=token_id, startTs=from_ts, end=to_ts, interval=interval, fidelity=fidelity
        )
        price_history = self._clob_internal_client.get_price_history(params)
        return price_history

    @staticmethod
    def number_to_cursor(value: str | int) -> str:
        """
        Encodes a given string to Base64 format.
        :param value: The string to be encoded.
        :return: Base64-encoded string.
        """
        # Encode to bytes, then convert to Base64 and decode back to string
        return base64.b64encode(str(value).encode()).decode()

    @staticmethod
    def cursor_to_number(encoded_value: str) -> int:
        """
        Decodes a Base64-encoded string back to its original form.
        :param encoded_value: The Base64 string to be decoded.
        :return: Decoded string.
        """
        # Decode Base64 to bytes, then decode bytes back to string
        return int(base64.b64decode(encoded_value).decode())


def __demo__():
    self = ClobClient()
    print(self)

    self.get_market_info("0xc2c0d4a0500a76186568270e28ff3619e7598578d2e90094bb89f2e0371cff0a")
