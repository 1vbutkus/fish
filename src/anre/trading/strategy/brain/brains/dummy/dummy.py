from typing import Any, Dict

from anre.trading.strategy.action.actions.base import StrategyAction
from anre.trading.strategy.brain.brains.base.brainBase import StrategyBrain
from anre.trading.strategy.brain.brains.dummy.config import Config


class Dummy(StrategyBrain):
    __version__ = "0.0.0.0"
    configClass = Config
    strategyLabel = 'Dummy'


    def get_report_dict(self) -> Dict[str, Any]:
        return {}

    def update_state_and_get_action_list(self, action_freez: bool) -> list[StrategyAction]:
        assert self.isSetObjects
        return []
