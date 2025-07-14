import datetime
from multiprocessing import Lock
from typing import Optional

from anre.connection.polymarket.api.cache.house_book import HouseOrderBookCache
from anre.connection.polymarket.api.cache.net_book import NetBoolMarketOrderBook
from anre.connection.polymarket.api.cache.public_book import PublicMarketOrderBookCache
from anre.connection.polymarket.api.clob import ClobMarketInfoParser
from anre.connection.polymarket.master_client import MasterClient
from anre.trading.monitor.base import BaseMonitor
from anre.utils.time.timer.timerReal import TimerReal


class FlyBoolMarket(BaseMonitor):
    def __init__(self, condition_id: str, default_gtt=60) -> None:
        assert isinstance(condition_id, str)
        assert isinstance(default_gtt, (int, float))
        self._master_client = MasterClient()
        self._condition_id = condition_id
        self._timer = TimerReal()
        self._update_lock = Lock()
        self._last_iteration_run_time = 0
        self._cache: dict = {}
        self._default_gtt: int | float = default_gtt
        market_info_parser = self._fetch_clob_market_info_parser()
        self._bool_market_cred = market_info_parser.bool_market_cred
        self._asset_ids = (
            self._bool_market_cred.main_asset_id,
            self._bool_market_cred.counter_asset_id,
        )

    def iteration(self, gtt=2):
        # collect info amd mare sure it is valid and up to date

        if self._timer.nowS() > self._last_iteration_run_time + gtt:
            init_last_iteration_run_time = self._last_iteration_run_time
            with self._update_lock:
                if init_last_iteration_run_time == self._last_iteration_run_time:
                    self._update_internal_cache()
                    self._last_iteration_run_time = self._timer.nowS()

    def _assert_up_to_date(self, gtt: Optional[int | float] = None):
        gtt = gtt if gtt is not None else self._default_gtt
        assert self._timer.nowS() <= self._last_iteration_run_time + gtt

    def _update_internal_cache(self):
        self._cache['clob_market_info_parser'] = self._fetch_clob_market_info_parser()

        public_mob = self._fetch_public_mob()
        house_order_dict_list = self._fetch_house_order_dict_list()
        house_mob = self._calc_house_mob(house_order_dict_list=house_order_dict_list)
        net_mob = NetBoolMarketOrderBook.new(
            public_market_order_book=public_mob,
            house_order_book=house_mob,
            validate=True,
        )
        for order_dict in house_order_dict_list:
            ClobMarketInfoParser.alter_house_order_with_extra_info(order_dict)

        self._cache['public_mob'] = public_mob
        self._cache['house_mob'] = house_mob
        self._cache['net_mob'] = net_mob
        self._cache['house_order_dict_list'] = house_order_dict_list

    def _fetch_clob_market_info_parser(self) -> ClobMarketInfoParser:
        market_info = self._master_client.clob_client.get_single_market_info(
            condition_id=self._condition_id
        )
        return ClobMarketInfoParser(market_info=market_info)

    def _fetch_public_mob(self) -> PublicMarketOrderBookCache:
        clob_mob_list = self._master_client.clob_client.get_mob_dict_list(token_ids=self._asset_ids)
        public_market_order_book = PublicMarketOrderBookCache.new_init(
            **self._bool_market_cred.to_dict()
        )
        public_market_order_book.update_from_clob_mob_list(
            clob_mob_list=clob_mob_list, validate=True
        )
        return public_market_order_book

    def _fetch_house_order_dict_list(self) -> list[dict]:
        house_order_dict_list = self._master_client.clob_client.get_house_order_dict_list(
            condition_id=self._condition_id
        )
        return house_order_dict_list

    def _calc_house_mob(self, house_order_dict_list) -> HouseOrderBookCache:
        house_order_book = HouseOrderBookCache.new_init(**self._bool_market_cred.to_dict())
        house_order_book.update_reset_from_clob_house_order_list(house_order_dict_list)
        return house_order_book

    #############################################################################

    @property
    def market_info_parser(self) -> ClobMarketInfoParser:
        self._assert_up_to_date()
        clob_market_info_parser = self._cache['clob_market_info_parser']
        assert isinstance(clob_market_info_parser, ClobMarketInfoParser)
        return clob_market_info_parser

    def get_accepting_order_dt(self) -> datetime.datetime:
        return self.market_info_parser.accepting_order_dt

    def get_game_start_dt(self) -> Optional[datetime.datetime]:
        return self.market_info_parser.game_start_dt

    def get_end_dt(self) -> datetime.datetime:
        return self.market_info_parser.end_dt

    def get_tick1000(self) -> int:
        return self.market_info_parser.tick1000

    def get_market_order_books(
        self,
    ) -> tuple[PublicMarketOrderBookCache, HouseOrderBookCache, NetBoolMarketOrderBook]:
        self._assert_up_to_date()
        return self._cache['public_mob'], self._cache['house_mob'], self._cache['net_mob']

    def get_house_order_dict_list(self):
        self._assert_up_to_date()
        return self._cache['house_order_dict_list']

    # def get_historical_price(self):
    #     return self._master_client.clob_client.get_price_history(
    #         token_id=self.market_info_parser.bool_market_cred.yes_asset_id,
    #         interval='1m',
    #         fidelity=10,
    #     )
