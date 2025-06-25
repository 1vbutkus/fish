import datetime
from dataclasses import dataclass

from dataclass_type_validator import dataclass_validate

from anre.utils.time.convert import Convert as TimeConvert

levelInt2StrDict = {
    10: "DEBUG",
    20: "INFO",
    25: "NOTE",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL",
}


@dataclass_validate
@dataclass(frozen=True)
class MessageRecord:
    msg: str
    callerName: str
    level: int
    publishTime: datetime.datetime

    def get_formattedMessageStr(self) -> str:
        msgForPrint = "({level}, {publishTimeDt}, {publishTimeSec}, {callerName}): {msg}".format(
            level=self.levelStr,
            publishTimeDt=self.publishTime.strftime("%H:%M:%S"),
            publishTimeSec=TimeConvert.datetime2seconds(self.publishTime),
            msg=self.msg,
            callerName=self.callerName,
        )
        return msgForPrint

    @property
    def levelStr(self) -> str:
        if self.level in levelInt2StrDict:
            return levelInt2StrDict[self.level]

        return f'Level {self.level}'
