from anre.trading.strategy.action.actions.base import StrategyAction


class CancelOrdersByMarket(StrategyAction):
    def __init__(self, condition_id: str = "", asset_id: str = ""):
        assert condition_id or asset_id
        super().__init__()
        self.condition_id = condition_id
        self.asset_id = asset_id
