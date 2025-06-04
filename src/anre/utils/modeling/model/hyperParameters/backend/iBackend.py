import abc
from typing import Any

from anre.utils.modeling.model.hyperParameters.hyperParameter import HyperParameter


class IBackend(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_hyperParameterList(cls, **kwargs: Any) -> list[HyperParameter]: ...
