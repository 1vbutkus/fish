import datetime
from typing import Optional

from cachetools import TTLCache, cached

from anre.connection.polymarket.api.cache.house_book import HouseOrderBookCache
from anre.connection.polymarket.api.cache.net_book import NetBoolMarketOrderBook
from anre.connection.polymarket.api.cache.public_book import PublicMarketOrderBookCache
from anre.connection.polymarket.api.clob import ClobMarketInfoParser
from anre.connection.polymarket.master_client import MasterClient
from anre.trading.monitor.base import BaseMonitor


class FlyBoolMarket(BaseMonitor):
    def __init__(self, condition_id: str) -> None:
        assert isinstance(condition_id, str)
        self._master_client = MasterClient()
        self._condition_id = condition_id
        self._bool_market_cred = self.market_info_parser.bool_market_cred
        self._asset_ids = self._bool_market_cred.yes_asset_id, self._bool_market_cred.no_asset_id

    @cached(cache=TTLCache(maxsize=1, ttl=3600))
    def _get_clob_market_info_parser(self) -> ClobMarketInfoParser:
        # Note: sita butu galima pakeisti vidiniu cachu, kuri butu galima atnaujinti su ws zinutemis
        market_info = self._master_client.clob_client.get_single_market_info(
            condition_id=self._condition_id
        )
        return ClobMarketInfoParser(market_info=market_info)

    @property
    def market_info_parser(self):
        return self._get_clob_market_info_parser()

    def get_accepting_order_dt(self) -> datetime.datetime:
        return self.market_info_parser.accepting_order_dt

    def get_game_start_dt(self) -> Optional[datetime.datetime]:
        return self.market_info_parser.game_start_dt

    def get_end_dt(self) -> datetime.datetime:
        return self.market_info_parser.end_dt

    def get_public_mob(self) -> PublicMarketOrderBookCache:
        clob_mob_list = self._master_client.clob_client.get_mob_dict_list(token_ids=self._asset_ids)
        public_market_order_book = PublicMarketOrderBookCache.new_init(
            **self._bool_market_cred.to_dict()
        )
        public_market_order_book.update_from_clob_mob_list(
            clob_mob_list=clob_mob_list, validate=True
        )
        return public_market_order_book

    def get_house_mob(self) -> HouseOrderBookCache:
        house_order_dict_list = self._master_client.clob_client.get_house_order_dict_list(
            condition_id=self._condition_id
        )
        house_order_book = HouseOrderBookCache.new_init(**self._bool_market_cred.to_dict())
        house_order_book.update_reset_from_clob_house_order_list(house_order_dict_list)
        return house_order_book

    def get_market_order_books(
        self,
    ) -> tuple[PublicMarketOrderBookCache, HouseOrderBookCache, NetBoolMarketOrderBook]:
        public_market_order_book = self.get_public_mob()
        house_order_book = self.get_house_mob()
        net_market_order_book = NetBoolMarketOrderBook.new(
            public_market_order_book=public_market_order_book,
            house_order_book=house_order_book,
            validate=True,
        )
        return public_market_order_book, house_order_book, net_market_order_book

    def get_house_order_dict_list(self):
        return self._master_client.clob_client.get_house_order_dict_list(
            condition_id=self._condition_id
        )

    def get_historical_price(self):
        return self._master_client.clob_client.get_price_history(
            token_id=self.market_info_parser.bool_market_cred.yes_asset_id,
            interval='1m',
            fidelity=10,
        )

    def get_top_level_price_dict(self) -> dict[str, dict[str, float]]:
        return self._master_client.clob_client.get_top_level_price_dict(
            token_ids=self._asset_ids,
        )
