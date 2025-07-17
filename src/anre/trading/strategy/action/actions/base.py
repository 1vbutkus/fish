import uuid
from abc import ABC, abstractmethod
from typing import Optional


class StrategyAction(ABC):
    is_atomic: bool = False

    def __init__(self, *, parent_id: Optional[str] = None, **kwargs):
        self.internal_id: str = str(uuid.uuid4())
        self._is_approved: bool = False
        self._is_aborted: bool = False
        self._is_started: bool = False
        self._is_pending: bool = False
        self._is_success: bool = False
        self._is_failed: bool = False
        self._is_done: bool = False  # failed or success
        self._related_order_ids: list[str] = []
        self.parent_id: Optional[str] = parent_id
        assert not kwargs, f'Unexpected kwargs: {kwargs}'

    def set_aborted(self):
        assert not self._is_aborted, 'Action is already aborted'
        self._is_aborted = True

    def set_approved(self):
        assert not self._is_approved, 'Action is already approved'
        assert not self._is_aborted, 'Action is already aborted'
        self._is_approved = True

    def set_started(self):
        assert not self._is_started, f'Action is already started: {self}'
        assert self._is_approved, f'Action is not approved: {self}'
        assert not self._is_aborted, f'Action is already aborted: {self}'
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
        return self._related_order_ids

    @property
    def is_approved(self) -> bool:
        return self._is_approved

    @property
    def is_aborted(self) -> bool:
        return self._is_aborted

    @property
    def is_started(self) -> bool:
        return self._is_started

    @property
    def is_pending(self) -> bool:
        return self._is_pending

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failed(self) -> bool:
        return self._is_failed

    @property
    def is_done(self) -> bool:
        return self._is_done

    @abstractmethod
    def to_atomic_actions(self) -> list['StrategyAtomicAction']:
        pass

    @abstractmethod
    def set_state_from_atomic_actions(self):
        pass


class StrategyAtomicAction(StrategyAction):
    is_atomic: bool = True

    def to_atomic_actions(self) -> list['StrategyAtomicAction']:
        return [self]

    def set_state_from_atomic_actions(self):
        pass


class StrategyComplexAction(StrategyAction):
    is_atomic: bool = False
