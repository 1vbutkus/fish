from typing import Any, Dict, Optional

from anre.trading.monitor.base import BaseMonitor
from anre.trading.strategy.action.actions.base import StrategyAction
from anre.trading.strategy.brain.brains.base.brainBase import StrategyBrain
from anre.trading.strategy.brain.brains.dummy.config import Config


class FixedMarketMaker(StrategyBrain):
    __version__ = "0.0.0.0"
    configClass = Config
    strategyLabel = 'FixedMarketMaker'

    def __init__(self, config, tag_dict: Optional[Dict[str, str]] = None, comment: str = ''):
        super().__init__(config=config, tag_dict=tag_dict, comment=comment)
        self._monitor: Optional[BaseMonitor] = None

    def set_objects(self, monitor: BaseMonitor, **kwargs):
        assert not self.is_setting_object_finished
        assert isinstance(monitor, BaseMonitor)
        self._monitor = monitor
        self.is_setting_object_finished = True

    def get_report_dict(self) -> Dict[str, Any]:
        return {}

    def update_state_and_get_action_list(self, action_freeze: bool) -> list[StrategyAction]:
        assert self.is_setting_object_finished

        return []
