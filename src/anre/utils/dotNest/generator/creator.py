# mypy: disable-error-code="assignment"
from anre.utils.dotNest.generator.const.constGenerator import ConstGenerator
from anre.utils.dotNest.generator.random.randomGenerator import RandomGenerator


class Creator:
    @staticmethod
    def new(
        baseParam: dict,
        randomDimensionParamList: list[dict] | None = None,
        seed: int | None = None,
    ) -> RandomGenerator | ConstGenerator:
        if randomDimensionParamList:
            randomGenerator = RandomGenerator.new(
                baseParam=baseParam, randomDimensionParamList=randomDimensionParamList, seed=seed
            )
        else:
            _baseParam, _randomDimensionList = RandomGenerator.split_baseParamAndRandomVar(
                baseParamWithRandomVar=baseParam
            )
            if _randomDimensionList:
                randomGenerator = RandomGenerator(
                    baseParam=_baseParam,
                    randomDimensionList=_randomDimensionList,
                    seed=seed,
                )
            else:
                # assert seed is None, f'We are using constant generator, but still setting up seed.'
                randomGenerator = ConstGenerator.new(baseParam=baseParam)

        return randomGenerator
