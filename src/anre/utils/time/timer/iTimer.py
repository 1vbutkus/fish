import datetime
from typing import Protocol, runtime_checkable


@runtime_checkable
class ITimer(Protocol):
    is_real: bool

    def nowDt(self, offset=0.0) -> datetime.datetime:
        pass

    def nowS(self, offset=0.0) -> float:
        pass
