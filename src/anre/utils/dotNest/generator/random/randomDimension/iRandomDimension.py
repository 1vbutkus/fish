import abc
from typing import Any

import numpy as np


class IRandomDimension(abc.ABC):
    hash: str
    dotPath: str

    @abc.abstractmethod
    def sample(self, randomState: np.random.RandomState) -> Any: ...

    @abc.abstractmethod
    def set(self, inplace: bool = False, **kwargs: Any) -> None: ...

    @abc.abstractmethod
    def set_centerIfPossible(self, value: Any, inplace: bool = False) -> None: ...

    @abc.abstractmethod
    def get_centerOrSample(self) -> Any: ...

    @abc.abstractmethod
    def get_kwargs(self) -> dict[str, Any]: ...
