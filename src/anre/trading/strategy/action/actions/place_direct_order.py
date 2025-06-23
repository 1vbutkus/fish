from typing import Literal

from anre.trading.strategy.action.actions.base import StrategyAction


class PlaceDirectOrder(StrategyAction):
    def __init__(
        self,
        token_id: str,
        price: float,
        size: float,
        side: Literal["BUY", "SELL"],
        order_type: str = "GTC",
    ):
        assert size * price >= 1, f"Price * size must be >= 1, got {size} * {price}"
        super().__init__()
        self.token_id = token_id
        self.price = price
        self.size = size
        self.side = side
        self.order_type = order_type
