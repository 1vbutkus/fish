from __future__ import annotations

import abc
from typing import Any

import pandas as pd

from anre.type import Type
from anre.utils.modeling.model.iFitModel import IFitModel
from anre.utils.modeling.model.iModel import IModel
from anre.utils.modeling.model.leafModel.coreModel.info import Info


class ICoreModel(IModel, IFitModel):
    @classmethod
    @abc.abstractmethod
    def new(cls, name: str = 'Model', **kwargs: Any) -> ICoreModel: ...

    @classmethod
    @abc.abstractmethod
    def new_fromEngine(cls, engine, name: str = 'Model', **kwargs: Any) -> ICoreModel: ...

    @classmethod
    @abc.abstractmethod
    def get_hpKwargs(cls, **kwargs: Any) -> dict[str, Type.BasicType]: ...

    @classmethod
    @abc.abstractmethod
    def get_hyperParameterList(cls, **kwargs: Any): ...

    @abc.abstractmethod
    def fit(self, X, y, **kwargs: Any): ...

    @abc.abstractmethod
    def fit_continue(self, X, y, **kwargs: Any): ...

    @classmethod
    @abc.abstractmethod
    def isValidEngine(cls, engine) -> bool: ...

    @abc.abstractmethod
    def copy(self) -> ICoreModel: ...

    @abc.abstractmethod
    def recreate(self, **kwargs: Any) -> ICoreModel: ...

    @abc.abstractmethod
    def get_info(self) -> Info: ...

    @abc.abstractmethod
    def get_engine(self): ...

    @abc.abstractmethod
    def get_featureImportanceSr(self) -> pd.Series: ...
