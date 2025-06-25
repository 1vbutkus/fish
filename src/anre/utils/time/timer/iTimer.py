import datetime

from typing import Protocol


class ITimer(Protocol):
    is_real: bool

    def nowDt(self, offset=0.) -> datetime.datetime: pass

    def nowS(self, offset=0.) -> float: pass
