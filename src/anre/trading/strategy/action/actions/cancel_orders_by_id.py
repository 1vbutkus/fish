from anre.trading.strategy.action.actions.base import StrategyAction


class CancelOrdersById(StrategyAction):
    def __init__(self, order_ids):
        assert order_ids
        super().__init__()
        self.order_ids = order_ids
