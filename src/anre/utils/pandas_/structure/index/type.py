import abc

import numpy as np
import pandas as pd


class IType(abc.ABC):
    @abc.abstractmethod
    def is_type(self, index: pd.Index) -> bool: ...

    @abc.abstractmethod
    def get_empty(self, indexName: str) -> pd.Index: ...

    @abc.abstractmethod
    def get_name(self) -> str: ...


class Range(IType):
    def is_type(self, index: pd.Index) -> bool:
        return type(index) is pd.RangeIndex

    def get_empty(self, indexName: str) -> pd.Index:
        return pd.RangeIndex(0, name=indexName)

    def get_name(self) -> str:
        return str(pd.RangeIndex)


class Datetime(IType):
    def is_type(self, index: pd.Index) -> bool:
        return type(index) is pd.DatetimeIndex

    def get_empty(self, indexName: str) -> pd.Index:
        return pd.DatetimeIndex([], name=indexName)

    def get_name(self) -> str:
        return str(pd.DatetimeIndex)


class Int64(IType):
    def is_type(self, index: pd.Index) -> bool:
        return index.dtype == np.int64

    def get_empty(self, indexName: str) -> pd.Index:
        return pd.Index([], name=indexName, dtype=np.int64)

    def get_name(self) -> str:
        return f'{pd.Index}, {np.int64}'


all_type_classes: list[type[IType]] = [
    Datetime,
    Int64,
    Range,
]
