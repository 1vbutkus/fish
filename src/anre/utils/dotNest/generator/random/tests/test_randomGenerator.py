# mypy: disable-error-code="call-overload,var-annotated"
from typing import Any

from anre.utils import testutil
from anre.utils.dotNest.generator.random.randomDimension.randomVar import RandomVar
from anre.utils.dotNest.generator.random.randomGenerator import RandomGenerator


class TestRandomGenerator(testutil.TestCase):
    def test_basic(self) -> None:
        baseParam = {
            'const0_1': 1,
            'const0_2': 1,
            'dict0': {
                'int': 1,
                'float': 2.0,
                'chose': 'a',
                'extra': 'extra',
                'list': [
                    {'a': 1},
                    {'b': 2},
                    {'c': 3},
                ],
            },
        }
        randomDimensionParamList: list[dict[str, Any]] = [
            {
                'dotPath': 'dict0.int',
                'center': 200,
                'scale': 5,
                'dtype': 'int',
            },
            {
                'dotPath': 'dict0.float',
                'center': 200,
                'scale': 5,
                'dtype': 'float',
            },
            {
                'dotPath': 'dict0.chose',
                'elems': ['a', 'b', 'c'],
                'dtype': 'choice',
            },
            {
                'dotPath': 'dict0.list[1].b',
                'elems': [1, 2, 3],
                'dtype': 'choice',
            },
        ]

        randomGenerator = RandomGenerator.new(
            baseParam=baseParam,
            randomDimensionParamList=randomDimensionParamList,
        )
        newParam = randomGenerator.sample()
        assert len(newParam['dict0']['chose']) == 1
        assert isinstance(newParam['dict0']['int'], int)
        assert newParam['dict0']['int'] < 20
        assert newParam['dict0']['float'] < 20

        newParam1 = randomGenerator.sample()
        newParam2 = randomGenerator.sample()
        assert newParam1 != newParam2

        # is it reproducable?
        seed = 123456798
        randomGenerator.set_seed(seed=seed)
        newParam1 = randomGenerator.sample()
        randomGenerator.set_seed(seed=seed)
        newParam2 = randomGenerator.sample()
        assert newParam1 == newParam2

    def test_randomWithNoRandom1(self) -> None:
        baseParam = {
            'a': 1,
            'b': 2,
        }
        randomDimensionParamList = []
        randomGenerator = RandomGenerator.new(
            baseParam=baseParam,
            randomDimensionParamList=randomDimensionParamList,
        )
        for _ in range(5):
            assert randomGenerator.sample() == baseParam

    def test_randomWithNoRandom2(self) -> None:
        baseParam = {
            'a': 1,
            'b': 2,
        }
        _baseParam, _randomDimensionList = RandomGenerator.split_baseParamAndRandomVar(
            baseParamWithRandomVar=baseParam
        )
        randomGenerator = RandomGenerator(
            baseParam=_baseParam,
            randomDimensionList=_randomDimensionList,
        )
        for _ in range(5):
            assert randomGenerator.sample() == baseParam

    def test_fromRandomVar(self) -> None:
        baseParam = {
            'const0_1': 1,
            'const0_2': RandomVar.new_float(center=10, scale=5),
            'dict0': {
                'int': 1,
                'float': 2.0,
                'chose': RandomVar.new_choice(['a', 'b', 'c']),
                'extra': 'extra',
                'list': [
                    {'a': 1},
                    {'b': RandomVar.new_int(center=10, scale=5)},
                    {'c': 3},
                ],
            },
        }
        _baseParam, _randomDimensionList = RandomGenerator.split_baseParamAndRandomVar(
            baseParamWithRandomVar=baseParam
        )
        randomGenerator = RandomGenerator(
            baseParam=_baseParam,
            randomDimensionList=_randomDimensionList,
        )

        newParam = randomGenerator.sample()
        assert len(newParam['dict0']['chose']) == 1
        assert isinstance(newParam['dict0']['int'], int)
        assert newParam['dict0']['int'] < 20
        assert newParam['dict0']['float'] < 20

        newParam1 = randomGenerator.sample()
        newParam2 = randomGenerator.sample()
        assert newParam1 != newParam2

        # is it reproducable?
        seed = 123456798
        randomGenerator.set_seed(seed=seed)
        newParam1 = randomGenerator.sample()
        randomGenerator.set_seed(seed=seed)
        newParam2 = randomGenerator.sample()
        assert newParam1 == newParam2
