from typing import Literal

from anre.trading.strategy.action.actions.atomic.place_direct_order import PlaceDirectOrder
from anre.trading.strategy.action.actions.base import StrategyAtomicAction, StrategyComplexAction


class PlaceBoolMarketOrder(StrategyComplexAction):
    def __init__(
        self,
        main_asset_id: str,
        counter_asset_id: str,
        main_price1000: int,
        size1000: int,
        bool_side: Literal["LONG", "SHORT"],
        order_type: str = "GTC",
    ):
        assert bool_side in ("LONG", "SHORT"), f"bool_side must be LONG or SHORT, got {bool_side}"
        assert isinstance(main_price1000, int), f"price1000 must int, got {main_price1000}"
        assert isinstance(size1000, int), f"size1000 must int, got {size1000}"
        assert isinstance(main_asset_id, str) and main_asset_id
        assert isinstance(counter_asset_id, str) and counter_asset_id
        assert main_asset_id != counter_asset_id
        assert 0 < main_price1000 < 1000, (
            f"price1000 must be between 1 and 1000, got {main_price1000}"
        )
        assert size1000 > 0, f"size must be > 0, got {size1000}"
        assert size1000 * main_price1000 >= 1000000, "Size to small relative to price (1)"
        assert size1000 * (1000 - main_price1000) >= 1000000, "Size to small relative to price (2)"

        super().__init__()
        self.main_token_id = main_asset_id
        self.counter_token_id = counter_asset_id
        self.main_price1000 = main_price1000
        self.size1000 = size1000
        self.bool_side = bool_side
        self.order_type = order_type
        self._atomic_actions: list[StrategyAtomicAction] | None = None

    def __repr__(self):
        return (
            f"PlaceBoolMarketOrder(main_token_id={self.main_token_id}, "
            f"counter_token_id={self.counter_token_id}, "
            f"main_price1000={self.main_price1000}, "
            f"size1000={self.size1000}, "
            f"bool_side={self.bool_side}, "
            f"order_type={self.order_type})"
        )

    def to_atomic_actions(self) -> list[StrategyAtomicAction]:
        # TODO: galimeoptimizuoti, kad viso kapitalo nesuavlgytume

        self.set_started()
        assert self._atomic_actions is None, "This action is already split"
        if self.bool_side == 'LONG':
            token_id = self.main_token_id
            price1000 = self.main_price1000
        elif self.bool_side == 'SHORT':
            token_id = self.counter_token_id
            price1000 = 1000 - self.main_price1000
        else:
            raise ValueError(f'Unknown bool_side: {self.bool_side}')

        action = PlaceDirectOrder(
            token_id=token_id,
            price1000=price1000,
            size1000=self.size1000,
            trade_side="BUY",
            order_type=self.order_type,
            parent_id=self.internal_id,
        )
        if self.is_approved:
            action.set_approved()
        atomic_actions = [action]
        self._atomic_actions = atomic_actions
        return atomic_actions

    def set_state_from_atomic_actions(self):
        atomic_actions = self._atomic_actions
        assert len(atomic_actions) == 1
        action = atomic_actions[0]
        assert isinstance(action, PlaceDirectOrder)
        assert action.parent_id and action.parent_id == self.internal_id
        assert action.is_done
        related_order_ids = action.related_order_ids
        if related_order_ids:
            self.set_related_order_ids(action.related_order_ids)
        self.set_final_status(is_success=action.is_success, is_failed=action.is_failed)
