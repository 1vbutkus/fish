from typing import Any

import numpy as np

from anre.utils.dotNest.generator.random.randomDimension.randomDimensionBase import (
    RandomDimensionBase,
)


class RandomDimensionChoice(RandomDimensionBase):
    def __init__(self, dotPath: str, elems, dtype='choice') -> None:
        assert isinstance(elems, (tuple, list))
        assert elems
        assert dtype == 'choice'
        super().__init__(dotPath=dotPath, dtype=dtype)

        self.elems = elems

    def sample(self, randomState: np.random.RandomState):
        assert isinstance(randomState, np.random.RandomState)
        if self.dtype == 'choice':
            return randomState.choice(self.elems)
        else:
            raise NotImplementedError

    def set_centerIfPossible(self, value: Any, inplace: bool = False):
        assert value in self.elems, f'value(`{value}`) is not in elems={self.elems}'
        if inplace:
            return self
        else:
            return self.__class__(**self.get_kwargs())  # recreate

    def get_centerOrSample(self) -> float:
        return self.sample(randomState=np.random.RandomState())
