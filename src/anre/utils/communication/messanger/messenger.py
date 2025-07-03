import dataclasses
import logging
import traceback
import warnings
from collections import Counter
from typing import Callable, List, Literal, Optional

from anre.utils.communication.alarm.alarm import alarm
from anre.utils.communication.messanger.messageRecord import MessageRecord
from anre.utils.communication.messanger.runtimeConfig import RuntimeConfig
from anre.utils.communication.popup import popupMsg
from anre.utils.time.timer.iTimer import ITimer
from anre.utils.time.timer.timerReal import TimerReal


class Messenger:
    @classmethod
    def new(
        cls,
        timer: ITimer = None,
        name: str = 'bird.messenger',
        quiet: bool = False,
        collectMessages: bool = False,
        alarmLevel: int = 40,
        popLevel=40,
    ):
        runtimeConfig = RuntimeConfig(
            quiet=quiet,
            collectMessages=collectMessages,
            alarmLevel=alarmLevel,
            popLevel=popLevel,
        )
        return cls(timer=timer, name=name, runtimeConfig=runtimeConfig)

    def __init__(
        self,
        timer: ITimer = None,
        name: str = 'bird.messenger',
        quiet: bool = False,
        collectMessages: bool = False,
        runtimeConfig: RuntimeConfig = None,
    ):
        if runtimeConfig is None:
            warnings.warn(
                'Please use Messenger.new(...) instead of Messenger(...)',
                DeprecationWarning,
                stacklevel=2,
            )
            runtimeConfig = RuntimeConfig(
                quiet=quiet,
                collectMessages=collectMessages,
                alarmLevel=30,
                popLevel=40,
            )

        timer = timer if timer is not None else TimerReal()

        assert isinstance(timer, ITimer)
        assert isinstance(name, str)
        assert isinstance(runtimeConfig, RuntimeConfig)

        self._runtimeConfig: RuntimeConfig = runtimeConfig
        self._timer = timer
        self._name = name
        self._logger = logging.getLogger(name)
        self._counter = Counter()
        self._messageLog: List[MessageRecord] = []  # TODO: nerinkti pagal parametra
        self._callbacks: List[Callable] = []

    def register_callback(self, callback: Callable):
        assert callback is None or isinstance(callback, Callable)
        self._callbacks.append(callback)

    def set_config(self, **kwargs):
        newConfig = dataclasses.replace(self._runtimeConfig, **kwargs)
        self._runtimeConfig = newConfig

    def debug(self, msg: str):
        self._spread_message(msg=msg, level=10)

    def info(self, msg: str, soundAlert: bool = None, popAlert: bool = None):
        self._spread_message(msg=msg, level=20, soundAlert=soundAlert, popAlert=popAlert)

    def note(self, msg: str, soundAlert: bool = None, popAlert: bool = None):
        self._spread_message(msg=msg, level=25, soundAlert=soundAlert, popAlert=popAlert)

    def warning(self, msg: str, soundAlert: bool = None, popAlert: bool = None):
        self._spread_message(msg=msg, level=30, soundAlert=soundAlert, popAlert=popAlert)

    def error(self, msg: str, soundAlert: bool = None, popAlert: bool = None):
        self._spread_message(msg=msg, level=40, soundAlert=soundAlert, popAlert=popAlert)

    def critical(self, msg: str, soundAlert: bool = None, popAlert: bool = None):
        self._spread_message(msg=msg, level=50, soundAlert=soundAlert, popAlert=popAlert)

    def _spread_message(self, msg: str, level: int, soundAlert: bool = None, popAlert: bool = None):
        publishTime = self._timer.nowDt()
        messageRecord = MessageRecord(
            msg=msg, callerName=self._name, level=level, publishTime=publishTime
        )

        if self._runtimeConfig.collectMessages:
            self._messageLog.append(messageRecord)
        self._counter.update([messageRecord.levelStr])

        if not self._runtimeConfig.quiet:
            formattedMessageStr = messageRecord.get_formattedMessageStr()
            self._logger.log(messageRecord.level, formattedMessageStr)

            if soundAlert is None:
                soundAlert = messageRecord.level >= self._runtimeConfig.alarmLevel

            if popAlert is None:
                popAlert = messageRecord.level >= self._runtimeConfig.popLevel

            if soundAlert:
                alarm()

            if popAlert:
                popupMsg(formattedMessageStr)

        try:
            for callback in self._callbacks:
                callback(messageRecord)
        except BaseException as e:
            msg = f'Messenger callback failed. Please investigate. Error: {e.__class__.__name__}({e}); traceback: {traceback.format_exc()}'
            self.error(msg)
            print(msg)

    def get_messageLog(self) -> [MessageRecord]:
        if self._messageLog:
            return self._messageLog.copy()
        else:
            return []

    def clear_messageLog(self) -> None:
        self._messageLog.clear()

    def get_msgCount(
        self,
        level: Optional[Literal["DEBUG", "INFO", "NOTE", "WARNING", "ERROR", "CRITICAL"]] = None,
    ) -> int:
        if level is None:
            return sum(self._counter.values())

        assert level in ["DEBUG", "INFO", "NOTE", "WARNING", "ERROR", "CRITICAL"]
        return self._counter[level]

    # def set_color(org_string, level=None):
    #     color_levels = {
    #         10: "\033[36m{}\033[0m",       # DEBUG
    #         20: "\033[32m{}\033[0m",       # INFO
    #         30: "\033[33m{}\033[0m",       # WARNING
    #         40: "\033[31m{}\033[0m",       # ERROR
    #         50: "\033[7;31;31m{}\033[0m"   # FATAL/CRITICAL/EXCEPTION
    #     }
    #     if level is None:
    #         return color_levels[20].format(org_string)
    #     else:
    #         return color_levels[int(level)].format(org_string)
