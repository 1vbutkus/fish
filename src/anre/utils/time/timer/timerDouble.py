import datetime
from typing import Union

from anre.utils.time.timer.iTimer import ITimer
from anre.utils.time.timer.timerPseudo import TimerPseudo


class TimerDouble(ITimer, object):

    def __init__(self, timerOriginal: ITimer):

        self._timerOriginal = timerOriginal
        self._timerInAction: Union[ITimer, TimerPseudo] = self._timerOriginal
        self._modeLabel = 'original'

    def set_mode(self, label: str):
        if label == 'original':
            self._timerInAction = self._timerOriginal
        elif label == 'pseudo':
            self._timerInAction = TimerPseudo(nowDt=self._timerOriginal.nowDt())
        else:
            raise ValueError

        self._modeLabel = label

    def update_currMoment_ofPseudo(self, **kwargs):
        assert self._modeLabel == 'pseudo', 'Tried to update_currMoment then not in pseudo mode'
        self._timerInAction.set_currentTime(**kwargs)

    @property
    def is_real(self) -> bool:
        return self._timerOriginal.is_real

    def nowDt(self, offset=0.) -> datetime.datetime:
        return self._timerInAction.nowDt(offset=offset)

    def nowS(self, offset=0.) -> float:
        return self._timerInAction.nowS(offset=offset)

    def nowDt_original(self, offset=0.) -> datetime.datetime:
        return self._timerOriginal.nowDt(offset=offset)

    def nowS_original(self, offset=0.) -> float:
        return self._timerOriginal.nowS(offset=offset)
