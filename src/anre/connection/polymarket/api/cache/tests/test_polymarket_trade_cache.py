from anre.config.config import config as anre_config
from anre.connection.polymarket.api.cache.house_trade import HouseTradeCache
from anre.utils import testutil
from anre.utils.Json.Json import Json


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
        position_by_outcome_tuple_0 = (
            position_by_outcome_dict_0['Yes'],
            position_by_outcome_dict_0['No'],
        )
        ## data
        data_trade_dict_list_0 = trade_change_step_list[0]['data_trade_list']
        data_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        data_house_trade_cache.update_from_data_trade_dict_list(data_trade_dict_list_0)
        _ = data_house_trade_cache.get_house_trade_df()
        data_position_by_outcome_tuple_0 = data_house_trade_cache.get_position_by_outcome()
        ## clob
        clob_trade_dict_list_0 = trade_change_step_list[0]['clob_trade_list']
        clob_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        clob_house_trade_cache.update_from_clob_trade_dict_list(clob_trade_dict_list_0)
        _ = clob_house_trade_cache.get_house_trade_df()
        clob_position_by_outcome_tuple_0 = clob_house_trade_cache.get_position_by_outcome()
        # checks
        assert position_by_outcome_tuple_0 == data_position_by_outcome_tuple_0
        assert position_by_outcome_tuple_0 == clob_position_by_outcome_tuple_0

        ### first step
        position_list = trade_change_step_list[1]['position_list']
        assert len(position_list) == 2
        position_by_outcome_dict_1 = {el['outcome']: el['size'] for el in position_list}
        position_by_outcome_tuple_1 = (
            position_by_outcome_dict_1['Yes'],
            position_by_outcome_dict_1['No'],
        )
        ## data
        data_trade_dict_list_1 = trade_change_step_list[1]['data_trade_list']
        data_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        data_house_trade_cache.update_from_data_trade_dict_list(data_trade_dict_list_1)
        _ = data_house_trade_cache.get_house_trade_df()
        data_position_by_outcome_tuple_1 = data_house_trade_cache.get_position_by_outcome()
        ## clob
        clob_trade_dict_list_1 = trade_change_step_list[1]['clob_trade_list']
        clob_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        clob_house_trade_cache.update_from_clob_trade_dict_list(clob_trade_dict_list_1)
        _ = clob_house_trade_cache.get_house_trade_df()
        clob_position_by_outcome_tuple_1 = clob_house_trade_cache.get_position_by_outcome()
        ## ws
        ws_house_message_list_1 = trade_change_step_list[1]['ws_house_message_list']
        ws_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        ws_house_trade_cache.update_from_clob_trade_dict_list(clob_trade_dict_list_0)  # init values
        ws_house_trade_cache.update_from_ws_trade_dict_list(ws_house_message_list_1)  # real update
        ws_position_by_outcome_tuple_1 = clob_house_trade_cache.get_position_by_outcome()
        # checks
        assert position_by_outcome_tuple_0 != position_by_outcome_tuple_1
        assert position_by_outcome_tuple_1 == data_position_by_outcome_tuple_1
        assert position_by_outcome_tuple_1 == clob_position_by_outcome_tuple_1
        assert position_by_outcome_tuple_1 == ws_position_by_outcome_tuple_1

        ### second step
        position_list = trade_change_step_list[2]['position_list']
        assert len(position_list) == 2
        position_by_outcome_dict_2 = {el['outcome']: el['size'] for el in position_list}
        position_by_outcome_tuple_2 = (
            position_by_outcome_dict_2['Yes'],
            position_by_outcome_dict_2['No'],
        )
        ## data
        data_trade_dict_list_2 = trade_change_step_list[2]['data_trade_list']
        data_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        data_house_trade_cache.update_from_data_trade_dict_list(data_trade_dict_list_2)
        _ = data_house_trade_cache.get_house_trade_df()
        data_position_by_outcome_tuple_2 = data_house_trade_cache.get_position_by_outcome()
        ## clob
        clob_trade_dict_list_2 = trade_change_step_list[2]['clob_trade_list']
        clob_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        clob_house_trade_cache.update_from_clob_trade_dict_list(clob_trade_dict_list_2)
        _ = clob_house_trade_cache.get_house_trade_df()
        clob_position_by_outcome_tuple_2 = clob_house_trade_cache.get_position_by_outcome()
        ## ws
        ws_house_message_list_2 = trade_change_step_list[2]['ws_house_message_list']
        ws_house_trade_cache = HouseTradeCache(condition_id=condition_id)
        ws_house_trade_cache.update_from_clob_trade_dict_list(clob_trade_dict_list_0)  # init values
        ws_house_trade_cache.update_from_ws_trade_dict_list(ws_house_message_list_2)  # real update
        ws_position_by_outcome_tuple_2 = clob_house_trade_cache.get_position_by_outcome()
        # checks
        assert position_by_outcome_tuple_1 != position_by_outcome_tuple_2
        assert position_by_outcome_tuple_2 == data_position_by_outcome_tuple_2
        assert position_by_outcome_tuple_2 == clob_position_by_outcome_tuple_2
        assert position_by_outcome_tuple_2 == ws_position_by_outcome_tuple_2
