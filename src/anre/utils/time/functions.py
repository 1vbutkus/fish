import datetime

import numpy as np
import pandas as pd

from .convert import Convert


def _int_division_floor(n, d):
    return n // d


def _int_division_ceil(n, d):
    return -_int_division_floor(n, -d)


def floor_dt(x, precision: float = 1.0):
    _coef = np.int64(1000000000 * precision)
    if isinstance(x, (pd.Series, pd.DatetimeIndex, np.ndarray)):
        num = _int_division_floor(Convert.dt2number(x=x).astype(np.int64), _coef) * _coef
    elif isinstance(x, (np.datetime64, pd.Timestamp, datetime.datetime)):
        num = _int_division_floor(np.int64(Convert.dt2number(x=x)), _coef) * _coef
    else:
        raise NotImplementedError(f"Not implemented type `{type(x)}`")
    return Convert.number2dt(num)


def ceil_dt(x, precision: float = 1.0):
    _coef = np.int64(1000000000 * precision)
    if isinstance(x, (pd.Series, pd.DatetimeIndex, np.ndarray)):
        num = _int_division_ceil(Convert.dt2number(x=x).astype(np.int64), _coef) * _coef
    elif isinstance(x, (np.datetime64, pd.Timestamp, datetime.datetime)):
        num = _int_division_ceil(np.int64(Convert.dt2number(x=x)), _coef) * _coef
    else:
        raise NotImplementedError(f"Not implemented type `{type(x)}`")
    return Convert.number2dt(num)


def time_mean(x: pd.Series | np.ndarray):
    if isinstance(x, (np.ndarray, pd.Series)):
        xMinValue = x.min()
        return xMinValue + (x - xMinValue).mean()
    else:
        raise NotImplementedError(f"Not implemented type `{type(x)}`")


def get_time_range(start: datetime.datetime, finish: datetime.datetime, precision: float | int = 1):
    nano_seconds = int(precision * 1000000000)
    _start = ceil_dt(start, precision=precision)
    _finish = floor_dt(finish, precision=precision) + datetime.timedelta(microseconds=1)
    return np.arange(_start, _finish, np.timedelta64(nano_seconds, 'ns'))


def get_random_time_sr(start, end, n):
    start_u = Convert.dt2number(start)
    end_u = Convert.dt2number(end)

    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='ns').to_series()


def split_date_ranges(from_dt: datetime.datetime, to_dt: datetime.datetime, step: int):
    if step <= 0:
        raise ValueError("Step must be positive")

    delta = datetime.timedelta(days=step)

    # Align to day boundary
    from_dt = from_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    to_dt = to_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    while from_dt <= to_dt:
        yield from_dt
        from_dt += delta
