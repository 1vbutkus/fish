import uuid
from abc import ABC


class StrategyAction(ABC):
    def __init__(self, **kwargs):
        self.internal_id: str = str(uuid.uuid4())
        self._is_approved: bool = False
        self._is_aborted: bool = False
        self._is_started: bool = False
        self._is_pending: bool = False
        self._is_success: bool = False
        self._is_failed: bool = False
        self._is_done: bool = False  # failed or success
        self._related_order_ids: list[str] = []

    def set_aborted(self):
        assert not self._is_aborted, 'Action is already aborted'
        self._is_aborted = True

    def set_approved(self):
        assert not self._is_approved, 'Action is already approved'
        assert not self._is_aborted, 'Action is already aborted'
        self._is_approved = True

    def set_started(self):
        assert not self._is_started, 'Action is already started'
        assert self._is_approved, 'Action is not approved'
        assert not self._is_aborted, 'Action is already aborted'
        self._is_started = True
        self._is_pending = True

    def set_final_status(self, is_success: bool, is_failed: bool):
        assert self._is_started, 'Action is not started'
        assert self._is_pending, 'Action is not pending'
        assert not self._is_done, 'Action is already done'
        assert isinstance(is_success, bool)
        assert isinstance(is_failed, bool)
        assert is_success != is_failed, 'Action is failed and success at the same time'
        self._is_success = is_success
        self._is_failed = is_failed
        self._is_pending = False
        self._is_done = True

    def set_related_order_ids(self, order_ids: list[str]):
        self._related_order_ids = order_ids

    @property
    def related_order_ids(self) -> list[str]:
        raise self._related_order_ids
