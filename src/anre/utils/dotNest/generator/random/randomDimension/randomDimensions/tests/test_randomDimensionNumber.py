import numpy as np

from anre.utils import testutil
from anre.utils.dotNest.generator.random.randomDimension.randomDimensions.randomDimensionNumber import (
    RandomDimensionNumber,
)


class TestRandomDimensionNumber(testutil.TestCase):
    def test_basic(self) -> None:
        randomDimensionNumber = RandomDimensionNumber(
            dotPath='some.path',
            center=0,
            scale=1,
            dtype='float',
        )
        randomState = np.random.RandomState()
        res = randomDimensionNumber.sample(randomState=randomState)
        assert isinstance(res, float)

        randomDimensionNumber.set_centerIfPossible(1)
        with self.assertRaises(AssertionError):
            randomDimensionNumber.set_centerIfPossible("1")
