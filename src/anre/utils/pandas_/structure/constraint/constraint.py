import abc
from dataclasses import dataclass
from typing import Any

import pandas as pd


class IConstraint(abc.ABC):
    @abc.abstractmethod
    def check(self, sr: pd.Series | pd.Index) -> bool: ...

    @abc.abstractmethod
    def get_error_message(self, sr: pd.Series | pd.Index) -> str: ...


@dataclass
class MonoInc(IConstraint):
    def check(self, sr: pd.Series | pd.Index) -> bool:
        return sr.is_monotonic_increasing

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return 'values should be monotonically increasing'


@dataclass
class MonoIncWithin(IConstraint):
    seconds: float

    def __post_init__(self):
        assert self.seconds >= 0

    def check(self, sr: pd.Series | pd.Index) -> bool:
        assert isinstance(sr, pd.Series)
        diff_min = sr.diff().dt.total_seconds().dropna().min()
        if pd.isna(diff_min):
            return True
        else:
            return diff_min >= -self.seconds

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        assert isinstance(sr, pd.Series)
        return (
            f'values should be monotonically increasing withing tolerance of {self.seconds}'
            + f' Got: {sr.diff().dt.total_seconds().dropna().min()}'
        )


@dataclass
class Positive(IConstraint):
    def check(self, sr: pd.Series | pd.Index) -> bool:
        return not (sr <= 0).any()

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return 'only positive values are allowed'


@dataclass
class NotNegative(IConstraint):
    def check(self, sr: pd.Series | pd.Index) -> bool:
        return not (sr < 0).any()

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return 'negative values are not allowed'


@dataclass
class NotNA(IConstraint):
    def check(self, sr: pd.Series | pd.Index) -> bool:
        return not sr.isna().any()

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return 'NA values are not allowed'


@dataclass
class Constant(IConstraint):
    def check(self, sr: pd.Series | pd.Index) -> bool:
        return sr.nunique() <= 1

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return f'all values should be identical, but {sr.nunique()} unique values found'


@dataclass
class Unique(IConstraint):
    def check(self, sr: pd.Series | pd.Index) -> bool:
        return sr.is_unique

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return f'all values should be unique, but only {sr.nunique()} out of {len(sr)} values are unique'


@dataclass
class ContainsOnly(IConstraint):
    values: list[Any]

    def check(self, sr: pd.Series | pd.Index) -> bool:
        return bool(sr.isin(self.values).all())

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return f'only {self.values} are allowed but actual uniques values were {list(sr.unique())}'


@dataclass
class StartsWith(IConstraint):
    value: Any

    def get_first_value(self, sr: pd.Series | pd.Index):
        return sr.iloc[0] if type(sr) is pd.Series else sr[0]

    def check(self, sr: pd.Series | pd.Index) -> bool:
        return self.get_first_value(sr) == self.value

    def get_error_message(self, sr: pd.Series | pd.Index) -> str:
        return f'first value should be {self.value} but was {self.get_first_value(sr)}'
