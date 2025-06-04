# mypy: disable-error-code="override"
import copy
from typing import Any

import numpy as np

from anre.utils.dotNest.generator.random.randomDimension.iRandomDimension import IRandomDimension
from anre.utils.hash.hash import Hash


class RandomDimensionBase(IRandomDimension):
    def __init__(self, dotPath: str, dtype: str) -> None:
        assert isinstance(dotPath, str)
        assert isinstance(dtype, str)
        assert dotPath
        assert dtype
        assert dtype in ['float', 'int', 'choice']

        self.dotPath = dotPath
        self.dtype = dtype

    def __repr__(self) -> str:
        argStr = ",".join([f"{key}={value}" for key, value in self.get_kwargs().items()])
        return f'{self.__class__.__name__}({argStr})'

    def __eq__(self, other: Any) -> bool:
        return self.hash == other.hash

    @property
    def hash(self) -> str:
        return Hash.get_dictHash(self.get_kwargs())

    def sample(self, randomState: np.random.RandomState):
        raise NotImplementedError

    def set_centerIfPossible(self, value: Any, inplace: bool = False):
        raise NotImplementedError

    def get_centerOrSample(self) -> Any:
        raise NotImplementedError

    def set(self, inplace: bool = False, **kwargs: Any):
        _kwargs = self.get_kwargs()
        _kwargs.update(kwargs)
        newInstance = self.__class__(**_kwargs)
        if inplace:
            self.__dict__.update(newInstance.__dict__)
        else:
            return newInstance

    def get_kwargs(self) -> dict[str, Any]:
        _kwargs = {key: value for key, value in self.__dict__.items() if not key.startswith('_')}
        return copy.deepcopy(_kwargs)
