import abc
from typing import Any

from anre.type import Type
from anre.utils.modeling.model.iPredictModel import IPredictModel


class IFitModel(IPredictModel):
    @abc.abstractmethod
    def fit(self, X, y, **kwargs: Any): ...

    @classmethod
    @abc.abstractmethod
    def get_hpKwargs(cls, **kwargs: Any) -> dict[str, Type.BasicType]: ...
