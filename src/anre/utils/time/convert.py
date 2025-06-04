import datetime
import numbers
from typing import cast, overload
from zoneinfo import ZoneInfo

import ciso8601
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

npType = np.ndarray | np.datetime64
pdType = pd.Series | pd.Timestamp | pd.Index | pd.DatetimeIndex

# _EPOCH = datetime.datetime(1970, 1, 1, tzinfo=ZoneInfo('UTC'))
_EPOCH = datetime.datetime.utcfromtimestamp(0.0)


class Convert:
    @staticmethod
    def timedelta2microseconds(x: datetime.timedelta) -> int:
        return (x.days * 86400 + x.seconds) * 1000000 + x.microseconds

    @classmethod
    def timedelta2nanoseconds(cls, x: datetime.timedelta) -> int:
        return cls.timedelta2microseconds(x=x) * 1000

    @classmethod
    def seconds2npdatetime(cls, x: float) -> np.timedelta64:
        return np.timedelta64(int(x * 1000000000), 'ns')

    @classmethod
    def datetime2seconds(cls, dt: datetime.datetime) -> float:
        return (dt - _EPOCH).total_seconds()

    @classmethod
    def seconds2datetime(cls, seconds: float) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(seconds)

    @classmethod
    def betfairTime2seconds(cls, betfairTime: int) -> float:
        return betfairTime / 1000

    @classmethod
    def seconds2betfairTime(cls, seconds: float) -> int:
        return round(seconds * 1000)

    @classmethod
    def dt2matplotlib(cls, d) -> float | np.ndarray:
        return mdates.date2num(d)

    @classmethod
    def matplotlib2dt(cls, x) -> datetime.datetime | np.ndarray:
        res = mdates.num2date(x, tz=None)
        if isinstance(res, datetime.datetime):
            res = res.replace(tzinfo=None)
        else:
            res = np.array([x.replace(tzinfo=None) for x in res], dtype='datetime64')
        return res

    @classmethod
    def seconds2dt(
        cls, seconds: float | int | np.ndarray | pd.Series | pd.Index
    ) -> datetime.datetime | pdType | npType:
        return cls.number2dt(seconds * 1000000000)

    @overload
    @classmethod
    def dt2seconds(cls, x: datetime.datetime | np.datetime64 | pd.Timestamp) -> float | int: ...

    @overload
    @classmethod
    def dt2seconds(cls, x: pd.Series | pd.Index | pd.DatetimeIndex) -> pd.Series | pd.Index: ...

    @overload
    @classmethod
    def dt2seconds(cls, x: np.ndarray) -> np.ndarray: ...

    @classmethod
    def dt2seconds(cls, x: datetime.datetime | pdType | npType) -> float | int | pdType | npType:
        return cls.dt2number(x=x) / 1000000000

    @staticmethod
    def str2dt_series(sr: pdType, errors='coerce', format="%Y-%m-%dT%H:%M:%S.%fZ") -> pd.Series:
        assert isinstance(sr, (pd.Series, pd.DatetimeIndex, pd.Index))
        return cast(pd.Series, pd.to_datetime(sr, errors=errors, format=format))

    @overload
    @classmethod
    def dt2number(cls, x: datetime.datetime | pd.Timestamp) -> float | int: ...

    @overload
    @classmethod
    def dt2number(cls, x: pd.Series | pd.Index | pd.DatetimeIndex) -> pd.Series | pd.Index: ...

    @overload
    @classmethod
    def dt2number(cls, x: npType) -> np.ndarray: ...

    @classmethod
    def dt2number(
        cls, x: datetime.datetime | pdType | npType
    ) -> float | int | pd.Series | pd.Index | np.ndarray:
        if isinstance(x, (datetime.datetime, pd.Timestamp)):
            return cls.timedelta2nanoseconds(x - _EPOCH)
        elif isinstance(x, (pd.Series, pd.DatetimeIndex)):
            return x.astype('datetime64[ns]').astype(np.int64)
        elif isinstance(x, (np.ndarray, np.datetime64)):
            return x.astype('datetime64[ns]').astype(np.int64)
        else:
            raise NotImplementedError(f"Not implemented type `{type(x)}`")

    @overload
    @classmethod
    def number2dt(cls, x: int | float) -> datetime.datetime: ...

    @overload
    @classmethod
    def number2dt(cls, x: pd.Series) -> pd.Series: ...

    @overload
    @classmethod
    def number2dt(cls, x: pd.Index | pd.DatetimeIndex) -> pd.Index: ...

    @overload
    @classmethod
    def number2dt(cls, x: np.ndarray) -> np.ndarray: ...

    @classmethod
    def number2dt(
        cls, x: int | float | pd.Series | pd.Index | pd.DatetimeIndex | np.ndarray
    ) -> datetime.datetime | pd.Series | pd.Index | np.ndarray:
        if isinstance(x, (int, float, numbers.Number)):
            return datetime.datetime.utcfromtimestamp(round(x / 1000) / 1000000)
        elif isinstance(x, (pd.Series, pd.DatetimeIndex, pd.Index)):
            return x.astype('datetime64[ns]')
        elif isinstance(x, (np.ndarray, np.datetime64)):
            return x.astype('datetime64[ns]')
        else:
            raise NotImplementedError(f"Not implemented type `{type(x)}`")

    @overload
    @classmethod
    def str2dt(cls, x: str) -> datetime.datetime: ...

    @overload
    @classmethod
    def str2dt(cls, x: pd.Series) -> pd.Series: ...

    @overload
    @classmethod
    def str2dt(cls, x: pd.Index) -> pd.Index: ...

    @overload
    @classmethod
    def str2dt(cls, x: np.ndarray) -> np.ndarray: ...

    @classmethod
    def str2dt(
        cls, x: str | pd.Series | pd.Index | np.ndarray
    ) -> datetime.datetime | pd.Series | pd.Index | np.ndarray:
        if isinstance(x, str):
            return ciso8601.parse_datetime_as_naive(x)
        elif isinstance(x, (pd.Series, pd.DatetimeIndex, pd.Index)):
            return cls.str2dt_series(sr=x, errors='coerce', format="%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            raise NotImplementedError(f"Not implemented type `{type(x)}`")

    @overload
    @classmethod
    def dt2str(cls, x: datetime.datetime | np.datetime64 | pd.Timestamp | str) -> str: ...

    @overload
    @classmethod
    def dt2str(cls, x: pd.Series) -> pd.Series: ...

    @overload
    @classmethod
    def dt2str(cls, x: pd.Index | pd.DatetimeIndex) -> pd.Index: ...

    @overload
    @classmethod
    def dt2str(cls, x: np.ndarray) -> np.ndarray: ...

    @classmethod
    def dt2str(
        cls, x: datetime.datetime | pdType | npType | str
    ) -> str | pd.Series | pd.Index | np.ndarray:
        if isinstance(x, str):
            return x
        elif isinstance(x, datetime.datetime):
            return x.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        elif isinstance(x, pd.Series):
            return x.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        elif isinstance(x, (pd.DatetimeIndex, pd.Index)):
            return pd.Index(x.to_series().dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        elif isinstance(x, np.datetime64):
            return x.astype(str) + 'Z'
        else:
            raise NotImplementedError(f"Not implemented type `{type(x)}`")

    @overload
    @staticmethod
    def dt2NaiveUtcDt(x: datetime.datetime) -> datetime.datetime: ...

    @overload
    @staticmethod
    def dt2NaiveUtcDt(x: pd.Series) -> pd.Series: ...

    @staticmethod
    def dt2NaiveUtcDt(x: datetime.datetime | pd.Series) -> datetime.datetime | pd.Series:
        if isinstance(x, datetime.datetime):
            if x.tzname() is None:
                x = x.replace(tzinfo=ZoneInfo('UTC'))
            return x.astimezone(ZoneInfo('UTC')).replace(tzinfo=None)
        elif isinstance(x, pd.Series):
            if x.dt.tz is None:
                return x
            else:
                return x.dt.tz_convert('UTC').dt.tz_convert(None)
        else:
            raise NotImplementedError(f"Not implemented type `{type(x)}`")

    @overload
    @staticmethod
    def dt2awareDt(x: datetime.datetime, tzStr: str) -> datetime.datetime: ...

    @overload
    @staticmethod
    def dt2awareDt(x: pd.Series, tzStr: str) -> pd.Series: ...

    @staticmethod
    def dt2awareDt(x: datetime.datetime | pd.Series, tzStr: str) -> datetime.datetime | pd.Series:
        if isinstance(x, datetime.datetime):
            if x.tzname() is None:
                x = x.replace(tzinfo=ZoneInfo('UTC'))
            return x.astimezone(ZoneInfo(tzStr))
        elif isinstance(x, pd.Series):
            if x.dt.tz is None:
                x = x.dt.tz_localize('UTC')
            return x.dt.tz_convert(tzStr)
        else:
            raise NotImplementedError(f"Not implemented type `{type(x)}`")

    @staticmethod
    def date2dt(x: datetime.date) -> datetime.datetime:
        return datetime.datetime(x.year, x.month, x.day)
