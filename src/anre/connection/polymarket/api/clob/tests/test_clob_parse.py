import time
import datetime

from anre.connection.polymarket.api.clob import ClobClient, ClobTradeParser, ClobMarketInfoParser
from anre.connection.polymarket.api.types import BoolMarketCred, HouseTradeRec
from anre.utils import testutil


@testutil.api
class TestClobParse(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        client = ClobClient()
        cls.client = client

    def test_market_info(self) -> None:
        client = self.client

        simplified_markets_info_list = client.get_sampling_simplified_markets_info_list(
            chunk_limit=1
        )
        assert simplified_markets_info_list
        simplified_markets_info = simplified_markets_info_list[0]
        condition_id = simplified_markets_info['condition_id']

        market_info = client.get_single_market_info(condition_id=condition_id)
        parser = ClobMarketInfoParser(market_info=market_info)

        assert isinstance(parser.market_info, dict)
        assert isinstance(parser.is_market_bool, bool)
        assert isinstance(parser.bool_market_cred, BoolMarketCred)
        assert isinstance(parser.accepting_order_dt, datetime.datetime)
        assert isinstance(parser.end_dt, datetime.datetime)
        assert isinstance(parser.game_start_dt, datetime.datetime) or parser.game_start_dt is None

    def test_house_trafades(self) -> None:
        client = self.client

        trade_dict_list = client.get_house_trade_dict_list(chunk_limit=1)
        house_trade_dict_list = ClobTradeParser.parse_house_trade_dict_list(
            trade_dict_list=trade_dict_list
        )
        assert isinstance(house_trade_dict_list, list)
        assert house_trade_dict_list
        assert isinstance(house_trade_dict_list[0], HouseTradeRec)
