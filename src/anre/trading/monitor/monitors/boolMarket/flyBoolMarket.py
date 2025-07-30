import datetime
import logging
from multiprocessing import Lock
from typing import Optional

from anre.connection.polymarket.api.cache.house_book import HouseOrderBookCache
from anre.connection.polymarket.api.cache.net_book import NetBoolMarketOrderBook
from anre.connection.polymarket.api.cache.public_book import PublicMarketOrderBookCache
from anre.connection.polymarket.api.clob import ClobMarketInfoParser, ClobTradeParser
from anre.connection.polymarket.api.types import HouseTradeRec
from anre.connection.polymarket.api.utils import get_position_by_outcome
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
        self._last_iteration_finish_time = 0
        self._cache: dict = {}
        self._default_gtt: int | float = default_gtt
        market_info_parser = self._fetch_clob_market_info_parser()
        self._bool_market_cred = market_info_parser.bool_market_cred
        self._asset_ids = (
            self._bool_market_cred.main_asset_id,
            self._bool_market_cred.counter_asset_id,
        )
        self._logger = logging.getLogger(__name__)

    def iteration(self, gtt=2):
        # collect info amd mare sure it is valid and up to date
        if self._timer.nowS() > self._last_iteration_finish_time + gtt:
            init_last_iteration_finish_time = self._last_iteration_finish_time
            with self._update_lock:
                if init_last_iteration_finish_time == self._last_iteration_finish_time:
                    self._update_internal_cache()
                    self._last_iteration_finish_time = self._timer.nowS()

    def assert_up_to_date(self, gtt: Optional[int | float] = None):
        gtt = gtt if gtt is not None else self._default_gtt
        assert self._timer.nowS() <= self._last_iteration_finish_time + gtt, (
            f'It is not up to date. Last update was {self._timer.nowS() - self._last_iteration_finish_time} seconds ago.'
        )

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

        balance_position_slow = self._fetch_house_balance_position()
        house_trade_rec_dict = self._fetch_house_trades()
        yes_position, no_position = get_position_by_outcome(list(house_trade_rec_dict.values()))
        balance_position = yes_position - no_position
        if abs(balance_position_slow - balance_position) > 1e-3:
            self._logger.warning(
                f'The balance position is not consistent: {balance_position} != {balance_position}'
            )

        self._cache['public_mob'] = public_mob
        self._cache['house_mob'] = house_mob
        self._cache['net_mob'] = net_mob
        self._cache['house_order_dict_list'] = house_order_dict_list
        self._cache['house_trade_rec_dict'] = house_trade_rec_dict
        self._cache['balance_position'] = balance_position

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

    def _fetch_house_trades(self) -> dict[str, HouseTradeRec]:
        house_order_dict_list = self._master_client.clob_client.get_house_trade_dict_list(
            condition_id=self._condition_id
        )
        trade_rec_dict = ClobTradeParser.parse_house_trade_dict_list(house_order_dict_list)
        return trade_rec_dict

    def _fetch_house_balance_position(self) -> int | float:
        house_position_dict_list = self._master_client.data_client.get_house_position_dict_list(
            condition_id=self._condition_id
        )
        assert len(house_position_dict_list) <= 2, 'The count is too big'
        balance_position = 0.0
        for position_dict in house_position_dict_list:
            if position_dict['outcome'] == 'Yes':
                balance_position += position_dict['size']
            elif position_dict['outcome'] == 'No':
                balance_position -= position_dict['size']
            else:
                raise ValueError(f'Unexpected outcome: {position_dict["outcome"]}')
        return balance_position

    def _calc_house_mob(self, house_order_dict_list) -> HouseOrderBookCache:
        house_order_book = HouseOrderBookCache.new_init(**self._bool_market_cred.to_dict())
        house_order_book.update_reset_from_clob_house_order_list(house_order_dict_list)
        return house_order_book

    #############################################################################

    @property
    def market_info_parser(self) -> ClobMarketInfoParser:
        self.assert_up_to_date()
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
        self.assert_up_to_date()
        return self._cache['public_mob'], self._cache['house_mob'], self._cache['net_mob']

    def get_house_order_dict_list(self):
        self.assert_up_to_date()
        return self._cache['house_order_dict_list']

    def get_house_balance_position(self) -> int | float:
        self.assert_up_to_date()
        return self._cache['balance_position']

    # def get_historical_price(self):
    #     return self._master_client.clob_client.get_price_history(
    #         token_id=self.market_info_parser.bool_market_cred.yes_asset_id,
    #         interval='1m',
    #         fidelity=10,
    #     )


def __dummy__():
    condition_id = '0x0de7d3a8cb29764fc91c5941a00e1cf010b9ee0f2f4b0cd82a9e0737ffed0c96'  # jerome-powell-out-as-fed-chair-by-august-31

    cls = FlyBoolMarket
    self = monitor = cls(condition_id=condition_id, default_gtt=3600)

    self.iteration(gtt=2)
    self.get_house_balance_position()
