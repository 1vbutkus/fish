# mypy: disable-error-code="override"
from __future__ import annotations

import copy
from typing import Any, cast

import numpy as np

from anre.type import Type
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.transformer.info import Info
from anre.utils.modeling.transformer.iTransformer import ITransformer


class Identity(ITransformer):
    classId = 'Identity'
    __version__ = "0.0.0.1"

    @classmethod
    def new(cls, **kwargs: Any) -> 'Identity':
        return cls(isFitted=False)

    def __init__(self, isFitted: bool) -> None:
        assert self.__class__.__name__ == self.classId
        assert isinstance(isFitted, bool)

        self._isFitted = isFitted

    @property
    def isFitted(self) -> bool:
        return self._isFitted

    def fit(self, x: Type.Xy) -> 'Identity':
        assert not self._isFitted
        self._isFitted = True
        return self

    def transform(self, x: Type.Xy) -> np.ndarray:
        assert self._isFitted
        return cast(np.ndarray, x)

    def inverse_transform(self, x: Type.Xy) -> np.ndarray:
        assert self._isFitted
        return cast(np.ndarray, x)

    def get_info(self) -> Info:
        return Info(
            classId=self.classId,
            className=self.__class__.__name__,
            version=self.__version__,
            isFitted=self.isFitted,
            attrs=dict(),
        )

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        assert self._isFitted
        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

    @classmethod
    def load(cls, dirPath: str) -> Identity:
        info = Info.load(dirPath=dirPath)

        assert info.classId == cls.classId
        return cls(isFitted=info.isFitted)

    def copy(self) -> 'Identity':
        return copy.deepcopy(self)

    def recreate(self) -> 'Identity':
        return self.new()
