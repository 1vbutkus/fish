from __future__ import annotations

import abc
from typing import Any

import numpy as np

from anre.type import Type
from anre.utils.dataStructure.info import InfoBase


class ITransformer(abc.ABC):
    classId: str
    isFitted: bool

    @classmethod
    @abc.abstractmethod
    def new(cls, **kwargs: Any) -> ITransformer: ...

    @abc.abstractmethod
    def fit(self, x: Type.Xy) -> ITransformer: ...

    @abc.abstractmethod
    def transform(self, x: Type.Xy) -> np.ndarray: ...

    @abc.abstractmethod
    def inverse_transform(self, x: Type.Xy) -> np.ndarray: ...

    @abc.abstractmethod
    def save(self, dirPath: str, overwrite: bool = False) -> None: ...

    @classmethod
    @abc.abstractmethod
    def load(cls, dirPath: str) -> ITransformer: ...

    @abc.abstractmethod
    def get_info(self) -> InfoBase: ...

    @abc.abstractmethod
    def copy(self) -> ITransformer: ...

    @abc.abstractmethod
    def recreate(self) -> ITransformer: ...
