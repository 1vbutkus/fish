from numbers import Number
from typing import Any

import numpy as np

from anre.utils.dotNest.generator.random.randomDimension.randomDimensionBase import (
    RandomDimensionBase,
)


class RandomDimensionNumber(RandomDimensionBase):
    def __init__(
        self,
        dotPath: str,
        center: float,
        scale: float,
        dtype='float',
        hardLims: tuple = (-np.inf, np.inf),
    ) -> None:
        assert isinstance(center, (Number, float, int))
        assert isinstance(scale, (Number, float, int))
        assert isinstance(hardLims, (tuple, list))

        assert len(hardLims) == 2
        assert hardLims[0] <= hardLims[1]
        assert dtype in ['int', 'float']
        assert scale >= 0
        assert hardLims[0] <= center <= hardLims[1], (
            f'center is not in interval, i.e. {center} is not [{hardLims[0]}, {hardLims[1]}], {dotPath=}'
        )

        super().__init__(dotPath=dotPath, dtype=dtype)

        self.center = center
        self.scale = scale
        self.hardLims = hardLims

    def get_interval(self) -> tuple:
        _low, _high = self.center - self.scale, self.center + self.scale
        low = max(self.hardLims[0], _low)
        high = min(self.hardLims[1], _high)
        assert low <= high
        return low, high

    def sample(self, randomState: np.random.RandomState):
        assert isinstance(randomState, np.random.RandomState)

        low, high = self.get_interval()
        if self.dtype == 'float':
            return randomState.uniform(low=low, high=high)
        elif self.dtype == 'int':
            return randomState.randint(low, high)
        else:
            raise NotImplementedError

    def set_centerIfPossible(self, value: Any, inplace: bool = False):
        assert isinstance(value, (Number, float, int))
        assert self.hardLims[0] <= value <= self.hardLims[1]
        return self.set(center=value, inplace=inplace)

    def get_centerOrSample(self) -> float:
        return self.center
