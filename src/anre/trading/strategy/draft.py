import datetime
from abc import ABC, abstractmethod
from typing import Optional

from cachetools import TTLCache, cached
from anre.connection.polymarket.api.clob import ClobClient, ClobMarketInfoParser
from anre.connection.polymarket.master_client import MasterClient
from anre.trading.strategy.action.actions.base import StrategyAction
from anre.utils.time.convert import Convert as TimeConvert
from anre.config.config import config as anre_config
from anre.connection.polymarket.api.cache.house_book import HouseOrderBookCache
from anre.connection.polymarket.api.cache.net_book import NetMarketOrderBook
from anre.connection.polymarket.api.cache.public_book import PublicMarketOrderBookCache
from anre.connection.polymarket.api.clob import ClobMarketInfoParser
from anre.utils import testutil
from anre.utils.Json.Json import Json


class MarketDataState:
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

    def get_net_mob(self) -> NetMarketOrderBook:
        clob_mob_list = self._master_client.clob_client.get_mob_dict_list(token_ids=self._asset_ids)
        public_market_order_book = PublicMarketOrderBookCache.new_init(
            **self._bool_market_cred.to_dict()
        )
        public_market_order_book.update_from_clob_mob_list(
            clob_mob_list=clob_mob_list, validate=True
        )

        house_order_dict_list = self._master_client.clob_client.get_house_order_dict_list(
            condition_id=self._condition_id
        )
        house_order_book = HouseOrderBookCache.new_init(**self._bool_market_cred.to_dict())
        house_order_book.update_reset_from_clob_house_order_list(house_order_dict_list)

        net_market_order_book = NetMarketOrderBook.new(
            public_market_order_book=public_market_order_book,
            house_order_book=house_order_book,
            validate=True,
        )
        return net_market_order_book

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


def __dummy__():
    condition_id = '0x41eda073eeca4071d3a643a527bf8549851ff16c7e4b924a007671cb11920f98'
    self = MarketDataState(condition_id)
    self._asset_ids

    market_info = self.market_info_parser.market_info
    self.get_historical_price()
    self.get_house_order_dict_list()
    self.get_net_mob()
    self.get_top_level_price_dict()

    # self._master_client.clob_client.


class IStrategyBrain(ABC):
    @abstractmethod
    def run_iteration(self) -> list[StrategyAction]:
        pass


class StrategyBox:
    pass


def __dummy__():
    master_client = MasterClient()

    # master_client.clob_client.cancel_orders_all()

    # end_date_min = datetime.datetime.now() + datetime.timedelta(days=20)
    # market_info_list = master_client.gamma_client.get_market_info_list(
    #     limit=300, active=True, closed=False, end_date_min=end_date_min
    # )

    # slug = "will-zohran-madanis-vote-share-be-less-than-24-in-the-first-round-of-the-nyc-democratic-mayoral-primary"
    # slug = "will-iran-strike-gulf-oil-facilities-before-september"
    slug = "russia-x-ukraine-ceasefire-before-october"
    res = master_client.gamma_client.get_market_info_list(
        slug=slug,
    )
    assert len(res) == 1
    market_info = res[0]
    condition_id = market_info['conditionId']

    master_client.clob_client.get_single_market_info(condition_id=condition_id)

    master_client.clob_client.get_house_order_dict_list()
    #   'market': '0x140167d871a5f240e42dd8a021b03f2777f37589bd56b2c761c9b2bc8e2826f1',
    #   'asset_id': '23936405301368733389536574829640272390080862024402654321653331008041129806355',

    #   'market': '0xdaf2b4abb3e232c7cdc75a86d0018db39a071f1be40e68bf0b3085637420c6f0',
    #   'asset_id': '109054364550013931316084741620575744721889388390339985430626121306120801600493',

    condition_id = '0xdaf2b4abb3e232c7cdc75a86d0018db39a071f1be40e68bf0b3085637420c6f0'

    MasterClient.gamma_client.get_market_info_list(condition_ids=condition_id)

    MasterClient.clob_client.get_single_market_info(condition_id=condition_id)

    order_dict_list = MasterClient.clob_client.get_house_order_dict_list(condition_id=condition_id)
    order_id_list = [item['id'] for item in order_dict_list]
    MasterClient.clob_client.is_order_scoring(order_id=order_id_list[0])
