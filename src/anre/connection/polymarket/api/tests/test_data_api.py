from anre.connection.polymarket.api.data import DataClient
from anre.utils import testutil


class TestDataApi(testutil.TestCase):
    @testutil.api
    def test_smoke(self) -> None:
        data_client = DataClient()

        positions = data_client.get_house_positions(limit=3)
        assert isinstance(positions, list)
        trades = data_client.get_house_trades(limit=3)
        assert isinstance(trades, list)
