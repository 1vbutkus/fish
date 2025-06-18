from anre.connection.polymarket.api.data import DataClient
from anre.utils import testutil


class TestDataApi(testutil.TestCase):
    @testutil.api
    def test_smoke(self) -> None:
        data_client = DataClient()

        position_dict_list = data_client.get_house_position_dict_list(limit=3)
        assert isinstance(position_dict_list, list)
        trade_dict_list = data_client.get_house_trade_dict_list(limit=3)
        assert isinstance(trade_dict_list, list)
        house_trade_rec_list = DataClient.parse_house_trade_dict_list(trade_dict_list)
        assert isinstance(house_trade_rec_list, list)