import numpy as np

from anre.utils import testutil
from anre.utils.dotNest.generator.random.randomDimension.randomDimensions.randomDimensionChoice import (
    RandomDimensionChoice,
)


class TestRandomDimensionChoice(testutil.TestCase):
    def test_basic_int(self) -> None:
        randomDimensionChoice = RandomDimensionChoice(
            dotPath='some.path',
            elems=[0, 1, 2],
        )
        randomState = np.random.RandomState()
        res = randomDimensionChoice.sample(randomState=randomState)
        assert isinstance(res, (int, np.int_))

        randomDimensionChoice.set_centerIfPossible(1)
        with self.assertRaises(AssertionError):
            randomDimensionChoice.set_centerIfPossible("1")

    def test_basic_str(self) -> None:
        randomDimensionChoice = RandomDimensionChoice(
            dotPath='some.path',
            elems=['0', '1', '2'],
        )
        randomState = np.random.RandomState()
        res = randomDimensionChoice.sample(randomState=randomState)
        assert isinstance(res, str)
