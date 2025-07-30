import unittest

import pytest

from anre.trading.strategy.brain.brains.balance_market_maker.balance_market_maker import (
    BalanceMarketMaker as BalanceMarketMakerStrategyBrain,
)


class TestBalanceMarketMakerStrategy(unittest.TestCase):
    def test_smoke(self):
        strategy = BalanceMarketMakerStrategyBrain.new()

        assert not strategy.is_setting_object_finished
        with pytest.raises(AssertionError):
            _ = strategy.update_state_and_get_action_list(action_freeze=False)
