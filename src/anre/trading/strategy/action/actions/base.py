import uuid
from abc import ABC


class StrategyAction(ABC):
    def __init__(self, **kwargs):
        self.internal_id: str = str(uuid.uuid4())
        self._is_approved: bool = False
        self._is_aborted: bool = False
        self._is_started: bool = False
        self._is_pending: bool = False
        self._is_finished: bool = False
        self._is_failed: bool = False
        self._is_done: bool = False
        self._related_order_ids: list[str] = []

    def set_related_order_ids(self, order_ids: list[str]):
        self._related_order_ids = order_ids

    def related_order_ids(self) -> list[str]:
        raise self._related_order_ids
