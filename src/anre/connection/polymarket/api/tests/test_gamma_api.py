from anre.connection.polymarket.api.gamma import GammaClient
from anre.utils import testutil


class TestGammaApi(testutil.TestCase):
    @testutil.api
    def test_smoke(self) -> None:
        gamma = GammaClient()

        markets = gamma.get_markets(limit=30, active=True, closed=False, end_date_min='2025-06-08')
        assert len(markets) == 30
