import datetime

from anre.utils.time.convert import Convert
from anre.utils.time.timer.iTimer import ITimer


class TimerPseudo(ITimer, object):
    is_real = False

    def __init__(self, nowDt: datetime.datetime = None, nowS: float = None):

        super().__init__()
        self._curr_nowDt = datetime.datetime(1970, 1, 1)
        self._curr_nowS = Convert.datetime2seconds(self._curr_nowDt)

        countOfArgs = (nowDt is not None) + (nowS is not None)
        assert countOfArgs <= 1, f'Most one argument is expecting, but {countOfArgs} was given: {nowDt}, {nowS}'
        if countOfArgs > 0:
            self.set_currentTime(nowDt=nowDt, nowS=nowS, isBackwardsOk=True)

    @classmethod
    def update(cls, force=False):
        pass

    @classmethod
    def _get_offset(cls, force=False):
        pass

    def nowDt(self, offset=0.):
        return self._curr_nowDt + datetime.timedelta(seconds=offset)

    def nowS(self, offset=0.):
        return self._curr_nowS + offset

    def set_currentTime(self, shiftSec: float = None, nowDt: datetime.datetime = None, nowS: float = None, isBackwardsOk=False):

        countOfArgs = (shiftSec is not None) + (nowDt is not None) + (nowS is not None)
        assert countOfArgs == 1, f'Exactly one argument is expecting, but {countOfArgs} was given: {shiftSec}, {nowDt}, {nowS}'
        if shiftSec is not None:
            assert shiftSec >= 0 or isBackwardsOk, 'Time is not allowed to go back. Use isBackwardsOk=True if needed.'
            self._curr_nowDt += datetime.timedelta(seconds=shiftSec)
            self._curr_nowS = Convert.datetime2seconds(self._curr_nowDt)
        elif nowDt is not None:
            assert isinstance(nowDt, datetime.datetime)
            assert self._curr_nowDt <= nowDt or isBackwardsOk, 'Time is not allowed to go back. Use isBackwardsOk=True if needed.'
            self._curr_nowDt = nowDt
            self._curr_nowS = Convert.datetime2seconds(self._curr_nowDt)
        elif nowS is not None:
            assert self._curr_nowS <= nowS or isBackwardsOk, 'Time is not allowed to go back. Use isBackwardsOk=True if needed.'
            self._curr_nowDt = Convert.seconds2datetime(nowS)
            self._curr_nowS = nowS
