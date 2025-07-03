import unittest

from anre.trading.strategy.brain.brains.dummy.dummy import Dummy as DummyStrategyBrain


class TestDummyStrategy(unittest.TestCase):
    def test_smoke(self):
        strategy = DummyStrategyBrain.new()

        assert not strategy.is_setting_object_finished
        with self.assertRaises(AssertionError):
            _ = strategy.update_state_and_get_action_list(action_freeze=False)

        strategy.set_objects()
        assert strategy.is_setting_object_finished
        with self.assertRaises(AssertionError):
            strategy.set_objects()

        actionList = strategy.update_state_and_get_action_list(action_freeze=False)
        assert isinstance(actionList, list)
        assert not actionList

        report_dict = strategy.get_report_dict()
        assert isinstance(report_dict, dict)
        assert not report_dict
