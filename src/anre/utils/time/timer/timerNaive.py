import datetime
import time

from anre.utils.time.timer.iTimer import ITimer


class TimerNaive(ITimer, object):
    is_real = True

    def nowDt(self, offset=0.0) -> datetime.datetime:
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=offset)

    def nowS(self, offset=0.0) -> float:
        return time.time() + offset
