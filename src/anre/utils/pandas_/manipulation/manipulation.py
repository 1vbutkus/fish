# mypy: disable-error-code="assignment,call-overload,operator"
import typing

import numpy as np
import pandas as pd


class Manipulation:
    @staticmethod
    def lookup_byIndex(df: pd.DataFrame, rowIdx, colIdx) -> pd.Series:
        idx = pd.MultiIndex.from_arrays([rowIdx, colIdx])
        sr = df.stack().reindex(idx)
        return typing.cast(pd.Series, sr)

    @classmethod
    def columnLookup_byIndex(cls, df: pd.DataFrame, colIdx) -> pd.Series:
        assert len(colIdx) == df.shape[0], (
            f'len(colIdx)={len(colIdx)} must be equal to row count({df.shape[0]}) (each colIdx for each row)'
        )
        return cls.lookup_byIndex(df=df, rowIdx=df.index, colIdx=colIdx)

    @staticmethod
    def add_indexLevel(
        index: pd.MultiIndex | pd.Index,
        value: str | int = '',
        name: str | None = None,
        n: int = 1,
        onTop: bool = False,
    ) -> pd.MultiIndex | pd.Index:
        """Add extra dummy levels to index"""

        assert isinstance(index, (pd.MultiIndex, pd.Index))
        xar = np.array(index.tolist()).transpose()
        names = index.names if isinstance(index, pd.MultiIndex) else [index.name]
        addValues = np.full(shape=(n, xar.shape[-1]), fill_value=value)
        addName = [name] * n

        if onTop:
            names = addName + names
            xar = np.vstack([addValues, xar])
        else:
            names = names + addName
            xar = np.vstack([xar, addValues])

        return pd.MultiIndex.from_arrays(list(xar), names=names)

    @staticmethod
    def count_indexLevels(index: pd.MultiIndex | pd.Index) -> int:
        if isinstance(index, pd.MultiIndex):
            return len(index.levels)
        elif isinstance(index, pd.Index):
            return 1
        else:
            raise ValueError

    @staticmethod
    def flatten_index(index: pd.MultiIndex | pd.Index, sep: str = '_') -> list:
        if isinstance(index, pd.MultiIndex):
            return [sep.join([str(el) for el in col if el is not None]) for col in index]
        elif isinstance(index, pd.Index):
            return list(pd.Index)
        else:
            raise ValueError

    @staticmethod
    def get_lagDf(xSr: pd.Series, lagLim1: int = -3, lagLim2: int = 0) -> pd.DataFrame:
        cols, names = list(), list()
        for i in range(lagLim1, lagLim2 + 1, 1):
            cols.append(xSr.shift(-i))
            names += [i]

        lagDf = pd.concat(cols, axis=1)
        lagDf.columns = pd.Index(names, name='lags')

        return lagDf
