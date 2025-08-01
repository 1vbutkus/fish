from anre.trading.strategy.action.actions.base import StrategyAtomicAction


class CancelOrdersByIds(StrategyAtomicAction):
    def __init__(self, order_ids):
        assert order_ids
        super().__init__()
        self.order_ids = order_ids
