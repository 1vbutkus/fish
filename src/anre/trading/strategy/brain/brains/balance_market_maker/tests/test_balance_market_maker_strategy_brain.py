import unittest

import pytest

from anre.trading.strategy.brain.brains.fixed_market_maker.fixed_market_maker import (
    FixedMarketMaker as FixedMarketMakerStrategyBrain,
)


class TestFixedMarketMakingStrategy(unittest.TestCase):
    def test_smoke(self):
        strategy = FixedMarketMakerStrategyBrain.new()

        assert not strategy.is_setting_object_finished
        with pytest.raises(AssertionError):
            _ = strategy.update_state_and_get_action_list(action_freeze=False)
