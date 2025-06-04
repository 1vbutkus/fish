from typing import Any

from anre.utils import testutil
from anre.utils.dotNest.generator.creator import Creator as NestGeneratorCreator
from anre.utils.dotNest.generator.random.randomDimension.randomVar import RandomVar


class TestParameterGeneratorCreator(testutil.TestCase):
    def test_basic(self) -> None:
        baseParam = {
            'const0_1': 1,
            'const0_2': 1,
            'dict0': {
                'int': 1,
                'float': 2.0,
                'chose': 'b',
                'extra': 'extra',
            },
        }
        randomDimensionParamList: list[dict[str, Any]] = [
            {
                'dotPath': 'dict0.int',
                'center': 10,
                'scale': 9,
                'dtype': 'int',
            },
            {
                'dotPath': 'dict0.float',
                'center': 20,
                'scale': 1,
                'dtype': 'float',
            },
            {
                'dotPath': 'dict0.chose',
                'elems': ['a', 'b', 'c'],
                'dtype': 'choice',
            },
        ]

        randomGenerator = NestGeneratorCreator.new(
            baseParam=baseParam,
            randomDimensionParamList=randomDimensionParamList,
        )
        prm = next(randomGenerator)
        i = 0
        for i, prm in enumerate(randomGenerator):
            assert isinstance(prm, dict)
            if i > 3:
                break
        assert i == 4

    def test_basic_randomVar(self) -> None:
        baseParam = {
            'const0_1': 1,
            'const0_2': 1,
            'dict0': {
                'int': 1,
                'float': RandomVar.new_float(center=0, scale=1),
                'chose': 'b',
                'extra': 'extra',
            },
        }

        randomGenerator = NestGeneratorCreator.new(
            baseParam=baseParam,
            randomDimensionParamList=None,
            seed=123,
        )
        prm = next(randomGenerator)
        i = 0
        for i, prm in enumerate(randomGenerator):
            assert isinstance(prm, dict)
            if i > 3:
                break
        assert i == 4
