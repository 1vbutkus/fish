from typing import Any

from anre.utils.dotNest.generator.random.randomDimension.iRandomDimension import IRandomDimension
from anre.utils.dotNest.generator.random.randomDimension.randomDimensions.randomDimensionChoice import (
    RandomDimensionChoice,
)
from anre.utils.dotNest.generator.random.randomDimension.randomDimensions.randomDimensionNumber import (
    RandomDimensionNumber,
)


class Creator:
    @staticmethod
    def new(dotPath: str, dtype: str, **kwargs: Any) -> IRandomDimension:
        kwargs = {key: value for key, value in kwargs.items() if value is not None}
        if dtype in ['int', 'float']:
            return RandomDimensionNumber(dotPath=dotPath, dtype=dtype, **kwargs)
        elif dtype in ['choice']:
            return RandomDimensionChoice(dotPath=dotPath, dtype=dtype, **kwargs)
        else:
            raise NotImplementedError(f'dtype({dtype}) is not implemented yet in Creator.')
