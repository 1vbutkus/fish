from __future__ import annotations

import abc

from anre.utils.modeling.model.iPersistModel import IPersistModel
from anre.utils.modeling.model.iPredictModel import IPredictModel


class IModel(IPredictModel, IPersistModel):
    classId: str
    name: str
    isFitted: bool
    isRegression: bool
    isClassification: bool

    input_shape: tuple[int | None, ...]
    output_shape: tuple[int | None, ...]

    @abc.abstractmethod
    def save(self, dirPath: str, overwrite: bool = False) -> None: ...

    @classmethod
    @abc.abstractmethod
    def load(cls, dirPath: str) -> IModel: ...
