from typing import Literal, Optional

from anre.trading.strategy.action.actions.base import StrategyAtomicAction


class PlaceDirectOrder(StrategyAtomicAction):
    def __init__(
        self,
        token_id: str,
        price1000: int,
        size1000: int,
        trade_side: Literal["BUY", "SELL"],
        order_type: str = "GTC",
        parent_id: Optional[str] = None,
    ):
        assert size1000 * price1000 >= 1000000, (
            f"Price * size must be >= 1, got {size1000 / 1000} * {price1000 / 1000}"
        )
        super().__init__(parent_id=parent_id)
        self.token_id = token_id
        self.price1000 = price1000
        self.size1000 = size1000
        self.trade_side = trade_side
        self.order_type = order_type

    def __repr__(self):
        return (
            f"PlaceDirectOrder(token_id={self.token_id}, "
            f"price1000={self.price1000}, "
            f"size1000={self.size1000}, "
            f"trade_side={self.trade_side}, "
            f"order_type={self.order_type})"
        )
