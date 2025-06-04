# mypy: disable-error-code="misc,override,union-attr"

from __future__ import annotations

import copy
import os
from typing import Any

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from anre.type import Type
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.transformer.info import Info
from anre.utils.modeling.transformer.iTransformer import ITransformer


class Ecdf(ITransformer):
    classId = 'Ecdf'
    __version__ = "0.0.0.1"
    _fileName = 'ecdf.csv'

    @classmethod
    def new(cls, **kwargs: Any) -> 'Ecdf':
        return cls(isFitted=False, transform_fun=None, **kwargs)

    def __init__(self, isFitted: bool, transform_fun: interp1d | None, **kwargs: Any) -> None:
        assert self.__class__.__name__ == self.classId

        assert isinstance(isFitted, bool)
        assert isinstance(transform_fun, interp1d) or transform_fun is None

        self._kwargs = kwargs
        self._isFitted = isFitted
        self._transform_fun: interp1d | None = transform_fun
        self._inverse_fun: interp1d | None = None

    @property
    def isFitted(self) -> bool:
        return self._isFitted

    @property
    def transform_fun(self) -> interp1d:
        assert self._transform_fun is not None
        return self._transform_fun

    def fit(self, x: Type.y) -> 'Ecdf':
        assert not self._isFitted
        assert self._transform_fun is None
        self._isFitted = True
        if not isinstance(x, pd.Series):
            x = pd.Series(x)
        self._transform_fun = self.get_ecdf_interp1d(x=x, **self._kwargs)
        return self

    def transform(self, x: Type.y) -> np.ndarray:
        assert self._isFitted
        return self._transform_fun(x)

    def inverse_transform(self, x: Type.y) -> np.ndarray:
        assert self._isFitted
        inverse_fun = self._get_inverse_fun()
        return inverse_fun(x)

    def get_info(self) -> Info:
        return Info(
            classId=self.classId,
            className=self.__class__.__name__,
            version=self.__version__,
            isFitted=self.isFitted,
            attrs=dict(kwargs=self._kwargs),
        )

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        assert self._isFitted
        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

        _filePath = os.path.join(dirPath, self._fileName)
        pd.DataFrame({'x': self._transform_fun.x, 'y': self._transform_fun.y}, dtype=float).to_csv(
            _filePath, index=False
        )

    @classmethod
    def load(cls, dirPath: str) -> Ecdf:
        info = Info.load(dirPath=dirPath)

        assert info.classId == cls.classId

        _filePath = os.path.join(dirPath, cls._fileName)
        df = pd.read_csv(_filePath)
        transform_fun = cls.get_interp1d(df['x'], df['y'])

        return cls(isFitted=info.isFitted, transform_fun=transform_fun, **info.attrs['kwargs'])

    def copy(self) -> 'Ecdf':
        return copy.deepcopy(self)

    def recreate(self) -> 'Ecdf':
        return self.new()

    @staticmethod
    def get_interp1d(x, y) -> interp1d:
        return interp1d(x, y, bounds_error=False, fill_value=(np.min(y), np.max(y)))

    @classmethod
    def get_ecdf_interp1d(cls, x: pd.Series, ptik: float = 0.001) -> interp1d:
        assert isinstance(x, pd.Series)
        assert 1e-10 < ptik < 0.5

        prob = np.round(np.arange(0, 1 + ptik / 2, ptik), 11)
        quantile = np.round(x.quantile(prob), 11)
        df = pd.DataFrame(dict(prob=prob, quantile=quantile)).drop_duplicates(
            'quantile', keep='last'
        )

        ecdf_interp1d = cls.get_interp1d(df['quantile'], df['prob'])
        return ecdf_interp1d

    def inverted(self) -> 'Ecdf':
        assert self.isFitted
        return self.__class__(
            isFitted=self.isFitted, transform_fun=self._inverse_interp1d(fun=self._transform_fun)
        )

    @classmethod
    def _inverse_interp1d(cls, fun: interp1d) -> interp1d:
        assert isinstance(fun, interp1d)
        return cls.get_interp1d(x=fun.y, y=fun.x)

    def _get_inverse_fun(self):
        assert self._transform_fun is not None
        assert isinstance(self._transform_fun, interp1d)
        if self._inverse_fun is None:
            self._inverse_fun = self._inverse_interp1d(fun=self._transform_fun)
        return self._inverse_fun
