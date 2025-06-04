# mypy: disable-error-code="type-arg"
from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

from anre.utils.modeling.dataSet.dataSetGeneral import DataSetGeneral


class DataSetMl(DataSetGeneral):
    @classmethod
    def new_1d(
        cls, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray, name: str = 'ds', **kwargs
    ) -> DataSetMl:
        return cls.new(
            X=X,
            y=y,
            name=name,
            **kwargs,
        )

    @classmethod
    def new_2d(
        cls, X: pd.DataFrame | np.ndarray, Y: pd.DataFrame | np.ndarray, name: str = 'ds', **kwargs
    ) -> DataSetMl:
        return cls.new(
            X=X,
            Y=Y,
            name=name,
            **kwargs,
        )

    @classmethod
    def new_target(
        cls,
        X: pd.DataFrame | np.ndarray,
        target: pd.Series | pd.DataFrame | np.ndarray,
        name: str = 'ds',
        **kwargs,
    ) -> 'DataSetMl':
        return cls.new(
            X=X,
            target=target,
            name=name,
            **kwargs,
        )

    def __init__(
        self,
        df: pd.DataFrame,
        headerDict: Mapping[str, str | int | tuple | list],
        name: str = 'ds',
        skipValidation: bool = False,
    ):
        """Esminis ksirtumas, kad yra rezervuotai pavadinimai X, y, Y, target

        Dar apribojima, kad :
            y xor Y
            target tutampa su y arba Y
        """

        # can be modified. Make sure to break connection
        headerDict = headerDict.copy()  # type: ignore[attr-defined]

        # make sure target is in
        if 'target' not in headerDict:
            if 'y' in headerDict:
                headerDict['target'] = headerDict['y']  # type: ignore[index]
            elif 'Y' in headerDict:
                headerDict["target"] = headerDict["Y"]  # type: ignore[index]
            else:
                raise AssertionError('If target is missing, then y or Y must be given')

        super().__init__(df=df, headerDict=headerDict, name=name, skipValidation=True)  # type: ignore[arg-type]
        if not skipValidation:
            self._validate(df=self.df, headerDict=self._headerDict)

    def __setitem__(self, key, value):
        # jei y,Y arba target, tai keciam vienumetu ir uztikrinam, kad vienodi, it tik povisko patikra darom
        if key in ['y', 'Y']:
            self._set_item(key=key, value=value, skipValidation=True)
            self._set_item(key='target', value=key, skipValidation=True)
        elif key == 'target':
            self._set_item(key=key, value=value, skipValidation=True)
            if 'y' in self._headerDict:
                self._set_item(key='y', value='target', skipValidation=True)
            if 'Y' in self._headerDict:
                self._set_item(key='Y', value='target', skipValidation=True)
        else:
            self._set_item(key=key, value=value, skipValidation=True)

        self._validate(df=self.df, headerDict=self._headerDict)

    @staticmethod
    def _validate(df: pd.DataFrame, headerDict: dict[str, str | int | tuple | list]):
        super(DataSetMl, DataSetMl)._validate(df=df, headerDict=headerDict)

        assert 'X' in headerDict
        X = df[headerDict['X']]
        assert isinstance(X, pd.DataFrame)

        assert 'target' in headerDict
        target = df[headerDict['target']]
        assert isinstance(target, (pd.DataFrame, pd.Series))

        assert (('Y' in headerDict) + ('y' in headerDict)) <= 1, (
            "Can't both of ('y', 'Y') be provided."
        )

        if "y" in headerDict:
            assert headerDict["target"] == headerDict["y"]
            y = df[headerDict["y"]]
            assert isinstance(y, pd.Series)

        if "Y" in headerDict:
            assert headerDict["target"] == headerDict["Y"]
            Y = df[headerDict["Y"]]
            assert isinstance(Y, pd.DataFrame)

        if 'groups' in headerDict:
            groups = df[headerDict['groups']]
            assert isinstance(groups, pd.Series)

    @property
    def X(self) -> pd.DataFrame:
        resDf = self['X']
        assert isinstance(resDf, pd.DataFrame)
        return resDf

    @property
    def Y(self) -> pd.DataFrame:
        target = self.target
        assert isinstance(target, pd.DataFrame)
        return target

    @property
    def y(self) -> pd.Series:
        target = self.target
        assert isinstance(target, pd.Series)
        return target

    @property
    def target(self) -> list[pd.Series, pd.DataFrame]:
        resDf = self['target']
        return resDf
