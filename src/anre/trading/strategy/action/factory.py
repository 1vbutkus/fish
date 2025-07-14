from typing import Literal

from anre.trading.strategy.action.actions.place_bool_market_order import PlaceBoolMarketOrder
from anre.trading.strategy.action.actions.cancel_orders_by_ids import CancelOrdersByIds


class Factory:

    @classmethod
    def new_place_bool_market_order(
        cls,
        main_asset_id: str,
        counter_asset_id: str,
        main_price1000: int,
        size: float,
        bool_side: Literal["LONG", "SHORT"],
        order_type: str = "GTC",
    ) -> PlaceBoolMarketOrder:
        return PlaceBoolMarketOrder(
            main_asset_id=main_asset_id,
            counter_asset_id=counter_asset_id,
            main_price1000=main_price1000,
            size=size,
            bool_side=bool_side,
            order_type=order_type,
        )

    @classmethod
    def new_cancel_orders_by_ids(
        cls,
        order_ids: list[str],
    ) -> CancelOrdersByIds:
        return CancelOrdersByIds(
            order_ids=order_ids
        )

