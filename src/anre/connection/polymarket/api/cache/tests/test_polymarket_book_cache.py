from anre.config.config import config as anre_config
from anre.connection.polymarket.api.cache.house_book import HouseOrderBookCache
from anre.connection.polymarket.api.cache.net_book import NetMarketOrderBook
from anre.connection.polymarket.api.cache.public_book import PublicMarketOrderBookCache
from anre.connection.polymarket.api.clob.client import ClobClient
from anre.utils import testutil
from anre.utils.Json.Json import Json


class TestPolymarketBookCache(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _file_path = anre_config.path.get_path_to_root_dir(
            'src/anre/connection/polymarket/api/cache/tests/resources/book_change_step_list.json'
        )
        book_change_step_list = Json.load(path=_file_path)
        cls.book_change_step_list = book_change_step_list

    def test_xxx(self) -> None:
        book_change_step_list = self.book_change_step_list

        clob_market_info_dict = book_change_step_list[0]['clob_market_info_dict']

        bool_market_cred = ClobClient.get_bool_market_cred_from_market_info(
            market_info=clob_market_info_dict
        )
        market_order_book_cred = bool_market_cred.to_dict()

        ### zero step
        _clob_mob_list = book_change_step_list[0]['clob_mob_list']
        clob_public_mob_cache_0 = PublicMarketOrderBookCache.new_init(**market_order_book_cred)
        clob_public_mob_cache_0.update_from_clob_mob_list(
            clob_mob_list=_clob_mob_list, validate=True
        )

        ### first step
        ## public
        # clob
        _clob_mob_list = book_change_step_list[1]['clob_mob_list']
        clob_public_mob_cache_1 = PublicMarketOrderBookCache.new_init(**market_order_book_cred)
        clob_public_mob_cache_1.update_from_clob_mob_list(
            clob_mob_list=_clob_mob_list, validate=True
        )
        # ws
        _ws_market_message_list = book_change_step_list[1]['ws_market_message_list']
        ws_public_mob_cache_1 = PublicMarketOrderBookCache.new_init(**market_order_book_cred)
        ws_public_mob_cache_1.update_from_ws_message_list(
            ws_message_list=_ws_market_message_list, validate=True
        )
        # patikrinam as ws ir clob info sutampa
        assert clob_public_mob_cache_1 == ws_public_mob_cache_1
        ## house
        # clob
        clob_house_order_list_1 = book_change_step_list[1]['clob_house_order_list']
        clob_house_mob_cache_1 = HouseOrderBookCache.new_init(**market_order_book_cred)
        clob_house_mob_cache_1.update_reset_from_clob_house_order_list(
            clob_house_order_list=clob_house_order_list_1, validate=True
        )
        # ws. Note: in this we do not have ws messages, but we create to test construtor
        _ws_house_message_list = book_change_step_list[1]['ws_house_message_list']
        ws_house_mob_cache_1 = HouseOrderBookCache.new_init(**market_order_book_cred)
        ws_house_mob_cache_1.update_reset_from_clob_house_order_list(
            clob_house_order_list=clob_house_order_list_1, validate=True
        )
        ws_house_mob_cache_1.update_iteration_from_ws_message_list(
            ws_message_list=_ws_house_message_list, validate=True
        )
        assert clob_house_mob_cache_1 == ws_house_mob_cache_1
        # net book
        net_market_order_book_1 = NetMarketOrderBook.new(
            public_market_order_book=clob_public_mob_cache_1,
            house_order_book=clob_house_mob_cache_1,
            validate=True,
        )
        assert net_market_order_book_1.equals_book_values(clob_public_mob_cache_0)

        ### second step
        ## public
        # clob
        _clob_mob_list = book_change_step_list[2]['clob_mob_list']
        clob_public_mob_cache_2 = PublicMarketOrderBookCache.new_init(**market_order_book_cred)
        clob_public_mob_cache_2.update_from_clob_mob_list(
            clob_mob_list=_clob_mob_list, validate=True
        )
        # ws
        _ws_market_message_list = book_change_step_list[2]['ws_market_message_list']
        ws_public_mob_cache_2 = PublicMarketOrderBookCache.new_init(**market_order_book_cred)
        ws_public_mob_cache_2.update_from_ws_message_list(
            ws_message_list=_ws_market_message_list, validate=True
        )
        # patikrinam as ws ir clob info sutampa. Tiksliai nesutampa objektai, nes timestampai skiriasi
        assert clob_public_mob_cache_2.equals_book_values(ws_public_mob_cache_2)
        ## house
        # clob
        _clob_house_order_list = book_change_step_list[2]['clob_house_order_list']
        clob_house_mob_cache_2 = HouseOrderBookCache.new_init(**market_order_book_cred)
        clob_house_mob_cache_2.update_reset_from_clob_house_order_list(
            clob_house_order_list=_clob_house_order_list, validate=True
        )
        # ws
        _ws_house_message_list = book_change_step_list[2]['ws_house_message_list']
        ws_house_mob_cache_2 = HouseOrderBookCache.new_init(**market_order_book_cred)
        # note we generate init phase with old state and update with ws messages
        ws_house_mob_cache_2.update_reset_from_clob_house_order_list(
            clob_house_order_list=clob_house_order_list_1, validate=True
        )
        ws_house_mob_cache_2.update_iteration_from_ws_message_list(
            ws_message_list=_ws_house_message_list, validate=True
        )
        assert clob_house_mob_cache_2.equals_book_values(ws_house_mob_cache_2)
        # not book
        net_market_order_book_2 = NetMarketOrderBook.new(
            public_market_order_book=clob_public_mob_cache_2,
            house_order_book=clob_house_mob_cache_2,
            validate=True,
        )

        ### third step
        ## public
        # clob
        _clob_mob_list = book_change_step_list[3]['clob_mob_list']
        clob_public_mob_cache_3 = PublicMarketOrderBookCache.new_init(**market_order_book_cred)
        clob_public_mob_cache_3.update_from_clob_mob_list(
            clob_mob_list=_clob_mob_list, validate=True
        )
        # ws
        _ws_market_message_list = book_change_step_list[3]['ws_market_message_list']
        ws_public_mob_cache_3 = PublicMarketOrderBookCache.new_init(**market_order_book_cred)
        ws_public_mob_cache_3.update_from_ws_message_list(
            ws_message_list=_ws_market_message_list, validate=True
        )
        # patikrinam as ws ir clob info sutampa. Tiksliai nesutampa objektai, nes timestampai skiriasi
        assert clob_public_mob_cache_2.equals_book_values(ws_public_mob_cache_2)
        ## house
        # clob
        _clob_house_order_list = book_change_step_list[3]['clob_house_order_list']
        clob_house_mob_cache_3 = HouseOrderBookCache.new_init(**market_order_book_cred)
        clob_house_mob_cache_3.update_reset_from_clob_house_order_list(
            clob_house_order_list=_clob_house_order_list, validate=True
        )
        # ws
        _ws_house_message_list = book_change_step_list[3]['ws_house_message_list']
        ws_house_mob_cache_3 = HouseOrderBookCache.new_init(**market_order_book_cred)
        # note we generate init phase with old state and update with ws messages
        ws_house_mob_cache_3.update_reset_from_clob_house_order_list(
            clob_house_order_list=clob_house_order_list_1, validate=True
        )
        ws_house_mob_cache_3.update_iteration_from_ws_message_list(
            ws_message_list=_ws_house_message_list, validate=True
        )
        assert clob_house_mob_cache_3.equals_book_values(ws_house_mob_cache_3)
        # not book
        net_market_order_book_3 = NetMarketOrderBook.new(
            public_market_order_book=clob_public_mob_cache_3,
            house_order_book=clob_house_mob_cache_3,
            validate=True,
        )

        # compare
        net_market_order_book_3.sub(net_market_order_book_2)
