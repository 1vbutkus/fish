from anre.config.config import config as anre_config
from anre.connection.polymarket.api.cache.house_book import HouseOrderBook
from anre.connection.polymarket.api.cache.net_book import NetMarketOrderBook
from anre.connection.polymarket.api.cache.public_book import PublicMarketOrderBook
from anre.utils import testutil
from anre.utils.Json.Json import Json
from dataclasses import dataclass
from dataclasses import dataclass, field
from collections.abc import Sequence

from cytoolz.itertoolz import deque

from anre.connection.polymarket.api.cache.base import AssetBook as BaseAssetBook
from anre.connection.polymarket.api.cache.base import Book1000
from anre.connection.polymarket.api.cache.base import MarketOrderBook as BaseMarketOrderBook

import pandas as pd

from anre.connection.polymarket.api.cache.house_trade import HouseTradeCache
from anre.connection.polymarket.api.data import DataClient
from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.api.types import HouseTradeRec
from anre.connection.polymarket.api.types import HouseTradeRec
from anre.utils.dataStructure.general import GeneralBaseMutable



class TestPolymarketTradeCache(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _file_path = anre_config.path.get_path_to_root_dir(
            'src/anre/connection/polymarket/api/cache/tests/resources/trade_change_step_list.json'
        )
        trade_change_step_list = Json.load(path=_file_path)
        cls.trade_change_step_list = trade_change_step_list

    def test_xxx(self) -> None:
        trade_change_step_list = self.trade_change_step_list

        clob_market_info_dict = trade_change_step_list[0]['clob_market_info_dict']
        condition_id = clob_market_info_dict['condition_id']

        ### zero step
        position_list = trade_change_step_list[0]['position_list']
        assert len(position_list) == 2
        position_by_outcome_dict_0 = {el['outcome']: el['size'] for el in position_list}
        ## data
        data_trade_dict_list_0 = trade_change_step_list[0]['data_trade_list']
        data_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        data_house_trade_cache.extend(DataClient.parse_house_trade_dict_list(data_trade_dict_list_0))
        data_position_by_outcome_dict_0 = data_house_trade_cache.get_position_by_outcome()
        ## clob
        clob_trade_dict_list_0 = trade_change_step_list[0]['clob_trade_list']
        clob_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        clob_house_trade_cache.extend(ClobClient.parse_house_trade_dict_list(clob_trade_dict_list_0))
        clob_position_by_outcome_dict_0 = clob_house_trade_cache.get_position_by_outcome()
        assert position_by_outcome_dict_0 == data_position_by_outcome_dict_0
        assert position_by_outcome_dict_0 == clob_position_by_outcome_dict_0

        ### first step
        position_list = trade_change_step_list[1]['position_list']
        assert len(position_list) == 2
        position_by_outcome_dict_1 = {el['outcome']: el['size'] for el in position_list}
        ## data
        data_trade_dict_list_1 = trade_change_step_list[1]['data_trade_list']
        data_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        data_house_trade_cache.extend(DataClient.parse_house_trade_dict_list(data_trade_dict_list_1))
        data_position_by_outcome_dict_1 = data_house_trade_cache.get_position_by_outcome()
        ## clob
        clob_trade_dict_list_1 = trade_change_step_list[1]['clob_trade_list']
        clob_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        clob_house_trade_cache.extend(ClobClient.parse_house_trade_dict_list(clob_trade_dict_list_1[:1]))
        clob_position_by_outcome_dict_1 = clob_house_trade_cache.get_position_by_outcome()
        # TODO: Su tuo clob dar cia neaisku kodel toks didelis skirtumas
        ## stream
        ws_house_message_list = trade_change_step_list[1]['ws_house_message_list']

        # assert position_by_outcome_dict_0 == data_position_by_outcome_dict_0
        # assert position_by_outcome_dict_0 == clob_position_by_outcome_dict_0

        ### Second step
        position_list = trade_change_step_list[2]['position_list']
        assert len(position_list) == 2
        position_by_outcome_dict_2 = {el['outcome']: el['size'] for el in position_list}
        ## data
        data_trade_dict_list_2 = trade_change_step_list[2]['data_trade_list']
        data_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        data_house_trade_cache.extend(DataClient.parse_house_trade_dict_list(data_trade_dict_list_2))
        data_position_by_outcome_dict_2 = data_house_trade_cache.get_position_by_outcome()
        ## clob
        clob_trade_dict_list_2 = trade_change_step_list[2]['clob_trade_list']
        clob_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        clob_house_trade_cache.extend(ClobClient.parse_house_trade_dict_list(clob_trade_dict_list_2))
        clob_position_by_outcome_dict_2 = clob_house_trade_cache.get_position_by_outcome()
        ## stream
        ws_house_message_list = trade_change_step_list[2]['ws_house_message_list']

