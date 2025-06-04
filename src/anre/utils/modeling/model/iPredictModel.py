import abc
from typing import Any

import numpy as np

from anre.type import Type

typeX = Type.X


class IPredictModel(abc.ABC):
    @abc.abstractmethod
    def predict(self, X: typeX, **kwargs: Any) -> np.ndarray: ...
