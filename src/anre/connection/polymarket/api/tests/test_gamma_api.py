import datetime

from anre.connection.polymarket.api.gamma import GammaClient
from anre.utils import testutil


@testutil.api
class TestGammaApi(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        client = GammaClient()
        cls.client = client

    def test_smoke(self) -> None:
        client = self.client

        end_date_min = datetime.datetime.now() + datetime.timedelta(days=20)
        market_info_list = client.get_market_info_list(
            limit=30, active=True, closed=False, end_date_min=end_date_min
        )
        assert len(market_info_list) == 30

        market_info = market_info_list[0]
        _market_info = client.get_single_market_info(market_id=market_info['id'])
        assert market_info['conditionId'] == _market_info['conditionId']
        # siap dictai nera lygus

        event_info_list = client.get_event_info_list(limit=30, active=True, closed=False)
        assert len(event_info_list) == 30
