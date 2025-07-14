import base64
import time
from functools import partial
from typing import Callable, Literal, Optional

from py_clob_client.client import ClobClient as ClobInternalClient
from py_clob_client.clob_types import (
    ApiCreds,
    BookParams,
    OpenOrderParams,
    OrderArgs,
    OrderScoringParams,
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
    _house_address = anre_config.cred.get_polymarket_creds()['address']

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
            funder=polymarket_creds['address'],
        )
        api_creds = ApiCreds(
            api_key=polymarket_creds['ApiCreds']['key'],
            api_secret=polymarket_creds['ApiCreds']['secret'],
            api_passphrase=polymarket_creds['ApiCreds']['passphrase'],
        )
        # api_creds = client.create_or_derive_api_creds()
        api_client.set_api_creds(api_creds)
        return api_client

    def _collect_chunks(
        self,
        fun: Callable,
        cursor: str | int = "",
        sleep_time: float = 0.5,
        chunk_limit: int = None,
    ) -> list[dict]:
        assert sleep_time >= 0.01
        data = []
        count = 0
        while cursor != "LTE=":
            count += 1
            run_cursor = cursor
            result = fun(cursor=run_cursor)
            data.extend(result['data'])
            cursor = result['next_cursor']
            if chunk_limit is not None and count >= chunk_limit:
                break
            if cursor != "LTE=":
                time.sleep(sleep_time)
        return data

    def get_tick1000(self, token_id: str) -> int:
        _tick_size = self._clob_internal_client.get_tick_size(token_id=token_id)
        tick1000 = int(round(1000 * float(_tick_size)))
        return min(tick1000, 1)

    def get_single_market_info(self, condition_id: str) -> dict:
        return self._clob_internal_client.get_market(condition_id=condition_id)

    def get_market_info_chunk(self, cursor: str | int = "") -> dict:
        """Get available CLOB markets

        Please limit 50 request per 10 seconds.

        :param cursor: str, "" means the beginning and ‘LTE=’ means the end
        :return: dict with keys: data, next_cursor, count, limit
        """
        if isinstance(cursor, int):
            cursor = self.number_to_cursor(cursor)
        return self._clob_internal_client.get_markets(next_cursor=cursor)

    def get_market_info_list(
        self, cursor: str | int = "", sleep_time=0.5, chunk_limit: int = None
    ) -> list[dict]:
        return self._collect_chunks(
            fun=partial(
                self.get_market_info_chunk,
            ),
            cursor=cursor,
            sleep_time=sleep_time,
            chunk_limit=chunk_limit,
        )

    def get_sampling_market_info_chunk(self, cursor: str = "") -> dict:
        """Get available CLOB markets that have rewards enabled. Single chunk.

        Please limit 50 request per 10 seconds.

        :param cursor: str, "" means the beginning and ‘LTE=’ means the end
        :return: dict with keys: data, next_cursor, count, limit
        """
        if isinstance(cursor, int):
            cursor = self.number_to_cursor(cursor)
        return self._clob_internal_client.get_sampling_markets(next_cursor=cursor)

    def get_sampling_market_info_list(
        self, cursor: str | int = "", sleep_time=0.5, chunk_limit: int = None
    ) -> list[dict]:
        return self._collect_chunks(
            fun=partial(
                self.get_sampling_market_info_chunk,
            ),
            cursor=cursor,
            sleep_time=sleep_time,
            chunk_limit=chunk_limit,
        )

    def get_simplified_markets_info_chunk(self, cursor: str | int = "") -> dict:
        """Get available CLOB markets expressed in a simplified schema. Single chunk."""
        if isinstance(cursor, int):
            cursor = self.number_to_cursor(cursor)
        return self._clob_internal_client.get_simplified_markets(next_cursor=cursor)

    def get_simplified_markets_info_list(
        self, cursor: str | int = "", sleep_time=0.5, chunk_limit: int = None
    ) -> list[dict]:
        return self._collect_chunks(
            fun=partial(
                self.get_simplified_markets_info_chunk,
            ),
            cursor=cursor,
            sleep_time=sleep_time,
            chunk_limit=chunk_limit,
        )

    def get_sampling_simplified_market_info_chunk(self, cursor: str | int = "") -> dict:
        """Get available CLOB markets expressed in a simplified schema. That have rewards enabled. Single chunk."""
        if isinstance(cursor, int):
            cursor = self.number_to_cursor(cursor)
        return self._clob_internal_client.get_sampling_simplified_markets(next_cursor=cursor)

    def get_sampling_simplified_markets_info_list(
        self, cursor: str | int = "", sleep_time=0.5, chunk_limit: int = None
    ) -> list[dict]:
        return self._collect_chunks(
            fun=partial(
                self.get_sampling_simplified_market_info_chunk,
            ),
            cursor=cursor,
            sleep_time=sleep_time,
            chunk_limit=chunk_limit,
        )

    def get_house_trade_dict_chunk(
        self,
        id: str = None,
        maker_address: str = None,
        market: str = None,
        asset_id: str = None,
        before: int = None,
        after: int = None,
        cursor: str | int = "",
    ) -> dict:
        if isinstance(cursor, int):
            cursor = self.number_to_cursor(cursor)
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
            next_cursor=cursor,
        )
        return trades

    def get_house_trade_dict_list(
        self,
        id: str = None,
        maker_address: str = None,
        condition_id: str = None,
        asset_id: str = None,
        before: int = None,
        after: int = None,
        cursor: str | int = "",
        sleep_time=0.5,
        chunk_limit: int = None,
    ) -> list[dict]:
        return self._collect_chunks(
            fun=partial(
                self.get_house_trade_dict_chunk,
                id=id,
                maker_address=maker_address,
                market=condition_id,
                asset_id=asset_id,
                before=before,
                after=after,
            ),
            cursor=cursor,
            sleep_time=sleep_time,
            chunk_limit=chunk_limit,
        )

    def get_single_house_order_dict(self, order_id: str = None) -> dict:
        return self._clob_internal_client.get_order(order_id=order_id)

    def get_house_order_dict_chunk(
        self,
        order_id: str = None,
        condition_id: str = None,
        asset_id: str = None,
        cursor: str | int = "",
    ):
        if isinstance(cursor, int):
            cursor = self.number_to_cursor(cursor)
        params = OpenOrderParams(id=order_id, market=condition_id, asset_id=asset_id)
        return self._clob_internal_client.get_orders(params, next_cursor=cursor)

    def get_house_order_dict_list(
        self,
        order_id: str = None,
        condition_id: str = None,
        asset_id: str = None,
        cursor: str | int = "",
        sleep_time=0.5,
        chunk_limit: int = None,
    ) -> list[dict]:
        return self._collect_chunks(
            fun=partial(
                self.get_house_order_dict_chunk,
                order_id=order_id,
                condition_id=condition_id,
                asset_id=asset_id,
            ),
            cursor=cursor,
            sleep_time=sleep_time,
            chunk_limit=chunk_limit,
        )

    def get_single_mob_dict(self, token_id: str) -> dict:
        return self._clob_internal_client.get_order_book(token_id=token_id)

    def get_mob_dict_list(self, token_ids: list[str] | tuple[str, ...]) -> list[dict]:
        return self._clob_internal_client.get_order_books(token_ids=token_ids)

    def place_order(
        self,
        token_id: str,
        price: float,
        size: float,
        side: Literal["BUY", "SELL"],
        order_type: str = "GTC",
    ):
        assert side in ['BUY', 'SELL']
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

    def cancel_orders_by_ids(self, order_ids: list[str]):
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

    def is_order_scoring(self, order_id: str) -> bool:
        params = OrderScoringParams(orderId=order_id)
        resp = self._clob_internal_client.is_order_scoring(params=params)
        return resp['scoring']

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
        assert isinstance(encoded_value, str)
        if not encoded_value:
            return 0
        return int(base64.b64decode(encoded_value).decode())

    def get_server_time(self) -> int:
        return self._clob_internal_client.get_server_time()

    def get_top_level_price_dict(
        self, token_ids: list[str] | tuple[str, ...]
    ) -> dict[str, dict[str, float]]:
        params = [
            BookParams(token_id=token_id, side=side)
            for side in ['BUY', 'SELL']
            for token_id in token_ids
        ]
        res = self._clob_internal_client.get_prices(params=params)
        for token_id, price_dict in res.items():
            for side, price in price_dict.items():
                price_dict[side] = float(price)
        return res

    def get_top_level_price_midpoint_dict(
        self, token_ids: list[str] | tuple[str, ...]
    ) -> dict[str, float]:
        params = [BookParams(token_id=token_id) for token_id in token_ids]
        res = self._clob_internal_client.get_midpoints(params=params)
        for token_id, midpoint in res.items():
            res[token_id] = float(midpoint)
        return res


def __demo__():
    self = ClobClient()
    print(self)

    token_ids = [
        '75808883562514695201169204487787555859570951708948163798444132865757266366758',
        '79733714773966769289571596081594645290144843853077301462790845252981871229351',
    ]
    self.get_top_level_price_dict(token_ids)
    self.get_top_level_price_midpoint_dict(token_ids)
