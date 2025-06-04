# mypy: disable-error-code="misc"
import pandas as pd

from anre.utils.modeling.timeSlice.pureSlicer import PureSlicer
from anre.utils.modeling.timeSlice.splitIds import SplitIds


class LevelSlicer:
    def __init__(
        self,
        trainSize: int,
        testSize: int,
        shiftStep: int | None = None,
        slicingType: str | None = None,
        sliceCount: int | None = None,
        testInitPoss: int | None = None,
        trainSizeRequirement: int | None = None,
    ):
        shiftStep = testSize if shiftStep is None else shiftStep
        trainSizeRequirement = trainSize if trainSizeRequirement is None else trainSizeRequirement
        if slicingType is None:
            slicingType = 'rolling' if shiftStep > 0 else 'box'

        assert slicingType in [None, 'box', 'rolling']
        assert sliceCount is None or isinstance(sliceCount, int)
        assert testInitPoss is None or isinstance(testInitPoss, int)
        assert isinstance(shiftStep, int)
        assert isinstance(testSize, int)
        assert isinstance(trainSize, int)
        assert isinstance(trainSizeRequirement, int)
        assert shiftStep != 0
        assert trainSize >= 0
        assert trainSizeRequirement >= 0
        assert testSize >= 0
        assert sliceCount is None or sliceCount >= 0

        self.trainSize = trainSize
        self.trainSizeRequirement = max(trainSizeRequirement, trainSize)
        self.testSize = testSize
        self.shiftStep = shiftStep
        self.slicingType = slicingType
        self.sliceCount = sliceCount
        self.testInitPoss = testInitPoss

    def get_valueCountRequirement(self):
        return self._get_valueCountRequirement(
            trainSizeRequirement=self.trainSizeRequirement,
            testSize=self.testSize,
            shiftStep=self.shiftStep,
            slicingType=self.slicingType,
            sliceCount=self.sliceCount,
            testInitPoss=self.testInitPoss,
        )

    def get_splitIdsGenerator(self, parentGeneralTrainIds: list) -> list[SplitIds]:
        pureSlicer_level = PureSlicer(
            values=parentGeneralTrainIds,
            trainSize=self.trainSize,
            testSize=self.testSize,
            shiftStep=self.shiftStep,
            testInitPoss=self.testInitPoss,
            sliceCountCap=self.sliceCount,
        )

        pureSlicer_general = PureSlicer(
            values=parentGeneralTrainIds,
            trainSize=self.trainSizeRequirement,
            testSize=self.testSize,
            shiftStep=self.shiftStep,
            testInitPoss=self.testInitPoss,
            sliceCountCap=self.sliceCount,
        )

        sliceIds_level = pureSlicer_level.get_sliceIds()
        sliceIds_general = pureSlicer_general.get_sliceIds()
        assert sliceIds_level == sliceIds_general

        for sliceId in sliceIds_level:
            pureSlice_level = pureSlicer_level.get_pureSlice(sliceId=sliceId)
            pureSlice_general = pureSlicer_general.get_pureSlice(sliceId=sliceId)
            assert pureSlice_level.get_testValues() == pureSlice_general.get_testValues()
            assert set(pureSlice_level.get_trainValues()) <= set(
                pureSlice_general.get_trainValues()
            )

            # extra rearegment - so taht the generalTrainIds would be around split
            generalTrainIdsSr = pd.Series(pureSlice_general.get_trainValues())
            ind = generalTrainIdsSr > max(pureSlice_level.get_testValues())
            generalTrainIds = list(reversed(generalTrainIdsSr[ind].values)) + list(
                generalTrainIdsSr[~ind].values
            )

            yield SplitIds(
                sliceId=sliceId,
                testIds=pureSlice_level.get_testValues(),
                trainIds=pureSlice_level.get_trainValues(),
                generalTrainIds=generalTrainIds,
            )

    @staticmethod
    def _get_valueCountRequirement(
        trainSizeRequirement: int,
        testSize: int,
        shiftStep: int,
        slicingType: str,
        sliceCount: int | None,
        testInitPoss: int | None,
    ) -> int:
        if sliceCount is None:
            return trainSizeRequirement + testSize

        if testInitPoss is None:
            extraBecauseInitPoss = 0
        else:
            if shiftStep > 0:
                extraBecauseInitPoss = testInitPoss
            elif shiftStep < 0:
                extraBecauseInitPoss = testSize - testInitPoss
            else:
                raise ValueError

        if slicingType == 'box':
            valueCountRequirement = (
                trainSizeRequirement
                + testSize
                + max(
                    0,
                    extraBecauseInitPoss + abs(shiftStep) * (sliceCount - 1) - trainSizeRequirement,
                )
            )
        elif slicingType == 'rolling':
            valueCountRequirement = (
                trainSizeRequirement
                + testSize
                + abs(shiftStep) * (sliceCount - 1)
                + extraBecauseInitPoss
            )
        else:
            raise NotImplementedError

        return valueCountRequirement
