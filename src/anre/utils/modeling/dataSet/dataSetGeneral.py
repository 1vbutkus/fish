# mypy: disable-error-code="return"
from __future__ import annotations

import copy
from typing import Any, Sequence, Type, TypeVar

import numpy as np
import pandas as pd

from anre.utils import functions
from anre.utils.pandas_ import sample as pandas_sample


class _Indexer:
    @classmethod
    def new(cls, pdIndexer, ds):
        return cls(
            pdIndexer=pdIndexer,
            headerDict=ds._headerDict,
            name=ds.name,
            cls=ds.__class__,
        )

    def __init__(self, pdIndexer, headerDict, name, cls) -> None:
        self.pdIndexer = pdIndexer
        self.headerDict = headerDict
        self.name = name
        self.cls = cls

    def __getitem__(self, item):
        return self.cls(
            df=self.pdIndexer[item],
            headerDict=self.headerDict,
            name=self.name,
            skipValidation=True,
        )


DataSetGeneralSubClass = TypeVar('DataSetGeneralSubClass', bound='DataSetGeneral')


class DataSetGeneral:
    @classmethod
    def new(
        cls: Type[DataSetGeneralSubClass], name: str = "ds", **kwargs: Any
    ) -> DataSetGeneralSubClass:
        assert isinstance(name, str) or name is None
        assert isinstance(kwargs, dict)
        assert bool(kwargs)

        # check types a convert if possible
        dataDict = {}
        headerDict = {}
        countOfColumns = 0
        for header, value in kwargs.items():
            assert isinstance(header, str)
            if isinstance(value, np.ndarray):
                if len(value.shape) == 1:
                    value = pd.Series(value, name=header)
                elif len(value.shape) == 2:
                    value = pd.DataFrame(
                        value, columns=[f"{header}{i}" for i in range(value.shape[-1])]
                    )
                else:
                    raise ValueError(f"Input must me 1 i 2 dimensions, but got: {len(value.shape)}")
            elif isinstance(value, pd.Series):
                value.name = header
            assert isinstance(value, (pd.Series, pd.DataFrame))
            dataDict[header] = value
            headerDict[header] = (
                list(value.columns) if isinstance(value, pd.DataFrame) else value.name
            )
            countOfColumns += len(value.columns) if isinstance(value, pd.DataFrame) else 1

        # check that index match
        valueFirst = dataDict[list(dataDict.keys())[0]]
        assert isinstance(valueFirst, (pd.Series, pd.DataFrame))
        assert all([value.index.equals(valueFirst.index) for value in dataDict.values()])

        df = pd.concat(dataDict.values(), axis=1)
        assert len(df.shape) == 2
        assert df.shape[0] == valueFirst.shape[0]
        assert df.shape[1] == countOfColumns

        return cls(df=df, headerDict=headerDict, name=name)  # type: ignore[arg-type]

    def __init__(
        self,
        df: pd.DataFrame,
        headerDict: dict[str, str | int | tuple | list],
        name: str = "ds",
        skipValidation: bool = False,
    ):
        assert isinstance(df, pd.DataFrame)
        assert isinstance(headerDict, dict)
        assert isinstance(name, str)

        ### validate structure
        if not skipValidation:
            self._validate(df=df, headerDict=headerDict)

        self.df = df
        self._headerDict = headerDict
        self._name = name

    def __repr__(self) -> str:
        # return f'{self.__class__.__name__}(shape={self.df.shape}, keys={list(self._headerDict)})'
        return f"{self.__class__.__name__}(shape={self.df.shape}, headerDict={self._headerDict})"

    def __getattr__(self, item):
        return self.__getitem__(item=item)

    def __getitem__(self, item):
        assert item in self._headerDict, (
            f"item `{item}` is not defined in header. Available :{set(self._headerDict)}"
        )
        return self.df[self._headerDict[item]]

    def __setitem__(self, key, value):
        self._set_item(key=key, value=value, skipValidation=False)

    def _set_item(self, key, value, skipValidation: bool):
        if isinstance(value, np.ndarray):
            assert value.shape == (self.df.shape[0],)
            value = pd.Series(value, index=self.df.index, name=key)

        assert isinstance(key, str)
        assert isinstance(value, (str, list, pd.DataFrame, pd.Series))

        if isinstance(value, str):
            assert value in self.df.columns
            self._headerDict[key] = value
        elif isinstance(value, list):
            assert set(value) <= set(self.df.columns)
            self._headerDict[key] = value
        elif isinstance(value, pd.Series):
            assert value.index.equals(self.df.index)
            self.df[key] = value
            self._headerDict[key] = key
        elif isinstance(value, pd.DataFrame):
            assert value.index.equals(self.df.index)
            oldColumns = functions.diff_list(self.df.columns, value.columns)
            self.df = self.df[oldColumns].join(value)
            self._headerDict[key] = list(value.columns)

        if not skipValidation:
            self._validate(df=self.df, headerDict=self._headerDict)

    def __contains__(self, item):
        return item in self._headerDict

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d

    def copy(self):
        return self.__class__(
            df=self.df.copy(),
            headerDict=copy.deepcopy(self._headerDict),
            name=self.name,
        )

    def set(self, inplace: bool = False, **kwargs: Any):
        if inplace:
            obj = self
            for name, value in kwargs.items():
                obj[name] = value
        else:
            obj = self.copy()
            for name, value in kwargs.items():
                obj[name] = value
            return obj

    @staticmethod
    def _validate(df: pd.DataFrame, headerDict: dict[str, str | int | tuple | list]):
        assert "name" not in headerDict
        assert "inplace" not in headerDict
        assert "df" not in headerDict
        assert not isinstance(df.columns, pd.MultiIndex)
        assert df.columns.is_unique

        for header, col in headerDict.items():
            assert isinstance(header, str)
            if isinstance(col, list):
                columns = col
            elif isinstance(col, (str, int, tuple)):
                columns = [col]
            else:
                raise TypeError(f"header `{header}` has bad column(`{col}`) type(`{type(col)}`)")

            for column in columns:
                assert column in df, f"column(`{column}`) is not in df.columns: {list(df.columns)}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def headerDict(self) -> dict:
        return copy.deepcopy(self._headerDict)

    @property
    def groups(self) -> pd.Series | None:
        if "groups" in self:
            return self["groups"]

    def keys(self) -> list[str]:
        return list(self._headerDict)

    def drop_header(
        self, header: str, withData: bool = False, inplace: bool = False
    ) -> DataSetGeneral | None:
        assert header in self._headerDict
        headerDict = copy.deepcopy(self._headerDict)
        columns = headerDict.pop(header)
        if inplace:
            if withData:
                self.df.drop(columns=columns, inplace=True)
            self._headerDict = headerDict
        else:
            if withData:
                df = self.df.drop(columns=columns)
            else:
                df = self.df.copy()
            self._headerDict = headerDict
            return self.__class__(
                df=df,
                headerDict=headerDict,
                name=self.name,
            )

    def set_header(self, inplace: bool = False, **kwargs: Any):
        headerDict = copy.deepcopy(self._headerDict)
        headerDict.update(kwargs)
        self._validate(df=self.df, headerDict=headerDict)

        if inplace:
            self._headerDict = headerDict

        else:
            return self.__class__(
                df=self.df.copy(),
                headerDict=headerDict,
            )

    @property
    def loc(self) -> _Indexer:
        return _Indexer.new(pdIndexer=self.df.loc, ds=self)

    @property
    def iloc(self) -> _Indexer:
        return _Indexer.new(pdIndexer=self.df.iloc, ds=self)

    def dropNa(self, inplace: bool = False):
        if inplace:
            self.df = self.df.dropna()
        else:
            return self.__class__(
                df=self.df.dropna(),
                headerDict=self._headerDict,
            )

    def sample(self, *arg, **kwargs: Any):
        return self.__class__(
            df=self.df.sample(*arg, **kwargs),
            headerDict=self._headerDict,
        )

    def equals(self, other: "DataSetGeneral") -> bool:
        return self.df.equals(other.df) and self._headerDict.__eq__(other._headerDict)

    def split_trainTest(
        self,
        useGroupsIfPossible=True,
        useShuffleSplit: bool = False,
        seed=None,
        **kwargs,
    ) -> tuple:
        if useGroupsIfPossible:
            trainDf, testDf = pandas_sample.split_trainTest(
                df=self.df,
                groups=self.groups,
                useShuffleSplit=useShuffleSplit,
                seed=seed,
                **kwargs,
            )
        else:
            trainDf, testDf = pandas_sample.split_trainTest(
                df=self.df,
                groups=None,
                useShuffleSplit=useShuffleSplit,
                seed=seed,
                **kwargs,
            )
        trainDs = self.__class__(
            df=trainDf,
            headerDict=self._headerDict,
            name=self.name,
        )
        testDs = self.__class__(
            df=testDf,
            headerDict=self._headerDict,
            name=self.name,
        )
        return trainDs, testDs

    @classmethod
    def concat(
        cls,
        dsList: Sequence[DataSetGeneral],
        name: str = "ds",
        creatNewGroupsFromNames: bool = False,
        keys=None,
        **kwargs,
    ) -> DataSetGeneral:
        assert isinstance(dsList, list)
        assert bool(dsList)
        dsFirst = dsList[0]
        assert isinstance(dsFirst, cls)

        headerDict = copy.deepcopy(dsFirst._headerDict)
        assert all([ds._headerDict == headerDict for ds in dsList])

        keys = [ds.name for ds in dsList] if keys is None else keys
        df = pd.concat([ds.df for ds in dsList], keys=keys, **kwargs)
        assert df.shape[1] == dsFirst.df.shape[1]

        if creatNewGroupsFromNames:
            groups = pd.Series(df.index.get_level_values(0).values, index=df.index)
            if "groups" not in headerDict:
                headerDict["groups"] = "groups"
            df[headerDict["groups"]] = groups

        ds = cls(df=df, headerDict=headerDict, name=name)
        return ds
