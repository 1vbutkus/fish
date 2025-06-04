# mypy: disable-error-code="func-returns-value"
import copy

import numpy as np

from anre.utils.dotNest.dotNest import DotNest
from anre.utils.dotNest.generator.random.randomDimension.creator import (
    Creator as RandomDimensionCreator,
)
from anre.utils.dotNest.generator.random.randomDimension.iRandomDimension import IRandomDimension
from anre.utils.dotNest.generator.random.randomDimension.randomVar import RandomVar
from anre.utils.functions import check_isAllUnique


class RandomGenerator:
    @classmethod
    def new(
        cls,
        baseParam: dict | list,
        randomDimensionParamList: list[dict],
        seed: int | None = None,
    ) -> 'RandomGenerator':
        randomDimensionList = [
            RandomDimensionCreator.new(**randomDimensionParam)
            for randomDimensionParam in randomDimensionParamList
        ]
        return cls(
            baseParam=baseParam,
            randomDimensionList=randomDimensionList,
            seed=seed,
        )

    def __init__(
        self,
        baseParam: dict | list,
        randomDimensionList: list[IRandomDimension],
        seed: int | None = None,
    ):
        assert isinstance(baseParam, (dict, list))
        baseParamDotDict = DotNest.convert_nest2dotDict(baseParam)
        _ = DotNest.convert_dotDict2nest(baseParamDotDict)  # check that it is transformable

        dotPaths = [randomDimension.dotPath for randomDimension in randomDimensionList]
        assert check_isAllUnique(dotPaths)
        availablePaths = baseParamDotDict.keys()
        badPaths = [dotPath for dotPath in dotPaths if dotPath not in availablePaths]
        assert not badPaths, f'There are some bad paths: {badPaths=}, {availablePaths=}'
        assert all([dotPath in availablePaths for dotPath in dotPaths])

        randomDimensionList = self._set_defaults_byBaseParam(
            randomDimensionList=randomDimensionList, baseParamDotDict=baseParamDotDict
        )
        self.randomDimensionList: list[IRandomDimension] = randomDimensionList
        self._baseParamDotDict: dict = baseParamDotDict
        self._randomState = np.random.RandomState(seed=seed)

    def __next__(self):
        return self.sample()

    def __iter__(self):
        return self

    @property
    def baseParam(self) -> dict | list:
        return DotNest.convert_dotDict2nest(mixedNest=self._baseParamDotDict)

    @staticmethod
    def split_baseParamAndRandomVar(
        baseParamWithRandomVar: dict | list,
    ) -> tuple[dict | list, list[IRandomDimension]]:
        _randomState = np.random.RandomState()
        _baseParamDotDict = DotNest.convert_nest2dotDict(
            DotNest.convert_dotDict2nest(baseParamWithRandomVar)
        )
        randomDimensionList: list[IRandomDimension] = [
            rv.get_randomDimension(dotPath=dotPath)
            for dotPath, rv in _baseParamDotDict.items()
            if isinstance(rv, RandomVar)
        ]
        baseParam = copy.deepcopy(baseParamWithRandomVar)
        for randomDimension in randomDimensionList:
            assert (
                randomDimension.dotPath in _baseParamDotDict
            )  # double check that it already exist
            DotNest.nestSet(
                nest=baseParam,
                key=randomDimension.dotPath,
                value=randomDimension.get_centerOrSample(),
            )
        return baseParam, randomDimensionList

    def set_seed(self, seed: int):
        self._randomState = np.random.RandomState(seed=seed)

    def sample(self) -> dict | list:
        _updateParams = {
            randomDimension.dotPath: randomDimension.sample(randomState=self._randomState)
            for randomDimension in self.randomDimensionList
        }
        newParamDotDict = self._baseParamDotDict.copy()
        newParamDotDict.update(_updateParams)
        baseParam = DotNest.convert_dotDict2nest(mixedNest=newParamDotDict)
        return baseParam

    @staticmethod
    def _set_defaults_byBaseParam(
        randomDimensionList: list[IRandomDimension], baseParamDotDict: dict
    ) -> list[IRandomDimension]:
        newRandomDimensionList = []
        for randomDimension in randomDimensionList:
            value = baseParamDotDict[randomDimension.dotPath]
            randomDimension = randomDimension.set_centerIfPossible(value=value, inplace=False)  # type: ignore[assignment]
            newRandomDimensionList.append(randomDimension)
        return newRandomDimensionList
