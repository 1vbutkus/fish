from typing import Literal

from anre.trading.strategy.action.actions.atomic.cancel_orders_by_ids import CancelOrdersByIds
from anre.trading.strategy.action.actions.atomic.place_direct_order import PlaceDirectOrder
from anre.trading.strategy.action.actions.complex.place_bool_market_order import (
    PlaceBoolMarketOrder,
)


class Factory:
    @classmethod
    def new_place_bool_market_order(
        cls,
        main_asset_id: str,
        counter_asset_id: str,
        main_price1000: int,
        size1000: int,
        bool_side: Literal["LONG", "SHORT"],
        order_type: str = "GTC",
    ) -> PlaceBoolMarketOrder:
        return PlaceBoolMarketOrder(
            main_asset_id=main_asset_id,
            counter_asset_id=counter_asset_id,
            main_price1000=main_price1000,
            size1000=size1000,
            bool_side=bool_side,
            order_type=order_type,
        )

    @classmethod
    def new_place_direct_order(
        cls,
        token_id: str,
        price1000: int,
        size1000: int,
        trade_side: Literal["BUY", "SELL"],
        order_type: str = "GTC",
    ) -> PlaceDirectOrder:
        return PlaceDirectOrder(
            token_id=token_id,
            price1000=price1000,
            size1000=size1000,
            trade_side=trade_side,
            order_type=order_type,
        )

    @classmethod
    def new_cancel_orders_by_ids(
        cls,
        order_ids: list[str],
    ) -> CancelOrdersByIds:
        return CancelOrdersByIds(order_ids=order_ids)
