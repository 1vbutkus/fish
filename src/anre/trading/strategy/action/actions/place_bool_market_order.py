from typing import Literal

from anre.trading.strategy.action.actions.base import StrategyAction


class PlaceBoolMarketOrder(StrategyAction):
    def __init__(
        self,
        main_asset_id: str,
        counter_asset_id: str,
        main_price1000: int,
        size: float,
        bool_side: Literal["LONG", "SHORT"],
        order_type: str = "GTC",
    ):
        assert bool_side in ("LONG", "SHORT"), f"bool_side must be LONG or SHORT, got {bool_side}"
        assert isinstance(main_price1000, int), f"price1000 must int, got {main_price1000}"
        assert isinstance(main_asset_id, str) and main_asset_id
        assert isinstance(counter_asset_id, str) and counter_asset_id
        assert main_asset_id != counter_asset_id
        assert 0 < main_price1000 < 1000, (
            f"price1000 must be between 1 and 1000, got {main_price1000}"
        )
        assert size > 0, f"size must be > 0, got {size}"
        assert size * main_price1000 >= 1000, "Size to small relative to price (1)"
        assert size * (1000 - main_price1000) >= 1000, "Size to small relative to price (2)"

        super().__init__()
        self.main_token_id = main_asset_id
        self.counter_token_id = counter_asset_id
        self.main_price1000 = main_price1000
        self.size = size
        self.bool_side = bool_side
        self.order_type = order_type

    def __repr__(self):
        return (
            f"PlaceBoolMarketOrder(main_token_id={self.main_token_id}, "
            f"counter_token_id={self.counter_token_id}, "
            f"main_price1000={self.main_price1000}, "
            f"size={self.size}, "
            f"bool_side={self.bool_side}, "
            f"order_type={self.order_type})"
        )

