# mypy: disable-error-code="syntax"
from anre.utils.modeling.timeSlice.pureSlice import PureSlice


class PureSlicer:
    def __init__(
        self,
        values: list,
        trainSize: int,
        testSize: int,
        shiftStep: int,
        testInitPoss: int | None = None,
        sliceCountCap: int | None = None,
    ):
        assert isinstance(values, list)
        assert values

        assert shiftStep != 0, 'shiftStep can not be zero'
        assert trainSize > 0, 'trainSize must be positive'
        assert testSize >= 0, 'trainSize must be not negative'
        assert len(values) - testSize >= trainSize, (
            f'Not valid relation: {len(values)} - {testSize} >= {trainSize}'
        )
        assert sliceCountCap is None or sliceCountCap > 0
        if testInitPoss is None:
            testInitPoss = 0 if shiftStep > 0 else len(values)
        assert testInitPoss >= 0
        if shiftStep > 0:
            assert len(values) - testInitPoss - testSize >= 0
        else:
            assert testInitPoss - testSize >= 0

        self.values = values
        self.trainSize = trainSize
        self.testSize = testSize
        self.shiftStep = shiftStep
        self.testInitPoss = testInitPoss
        self.sliceCountCap = sliceCountCap

    def get_sliceIds(self):
        return self._get_sliceIds(
            countValue=len(self.values),
            testSize=self.testSize,
            shiftStep=self.shiftStep,
            testInitPoss=self.testInitPoss,
            sliceCountCap=self.sliceCountCap,
        )

    def get_pureSlice(self, sliceId) -> PureSlice:
        trainIds, testIds = self._get_elemIds(
            trainSize=self.trainSize,
            testSize=self.testSize,
            shiftStep=self.shiftStep,
            testInitPoss=self.testInitPoss,
            sliceId=sliceId,
        )

        assert max(trainIds) <= len(self.values)
        assert max(testIds) <= len(self.values)

        pureSlice = PureSlice(
            sliceId=sliceId,
            values=self.values,
            trainIds=trainIds,
            testIds=testIds,
        )
        return pureSlice

    @classmethod
    def get_sliceCount(
        cls, countValue, testSize, shiftStep, testInitPoss, sliceCountCap=None
    ) -> int:
        if shiftStep > 0:
            maxSliceCount = (countValue - testSize - testInitPoss) // abs(shiftStep) + 1
        else:
            maxSliceCount = (testInitPoss - testSize) // abs(shiftStep) + 1
        assert maxSliceCount > 0

        if sliceCountCap is not None:
            assert sliceCountCap > 0
            sliceCount = min(sliceCountCap, maxSliceCount)
        else:
            sliceCount = maxSliceCount

        return sliceCount

    @staticmethod
    def _get_elemIds(trainSize, testSize, shiftStep, testInitPoss, sliceId) -> (list, list):
        minTrainId = 0

        if shiftStep > 0:
            testStart = testInitPoss + shiftStep * sliceId
        else:
            testStart = testInitPoss - testSize + shiftStep * sliceId

        testStop = testStart + testSize
        testIds = list(range(testStart, testStop))

        trainStart = max(minTrainId, testStart - trainSize)
        if trainStart + trainSize > testStart:
            assert trainStart <= testStart
            shortCount = trainStart + trainSize - testStart
            trainIds = list(range(trainStart, testStart)) + list(
                range(testStop, testStop + shortCount)
            )
        else:
            trainIds = list(range(trainStart, trainStart + trainSize))

        assert not (set(trainIds) & set(testIds))
        assert len(trainIds) == trainSize
        assert len(testIds) == testSize
        if len(trainIds):
            assert min(trainIds) >= minTrainId
        _allIds = list(set(trainIds) | set(testIds))
        _allIds.sort()
        assert _allIds == list(range(min(_allIds), max(_allIds) + 1))

        return trainIds, testIds

    @classmethod
    def _get_sliceIds(
        cls,
        countValue: int,
        testSize: int,
        shiftStep: int,
        testInitPoss: int,
        sliceCountCap: int | None = None,
    ) -> list[int]:
        sliceCount = cls.get_sliceCount(
            countValue=countValue,
            testSize=testSize,
            shiftStep=shiftStep,
            testInitPoss=testInitPoss,
            sliceCountCap=sliceCountCap,
        )
        return list(range(sliceCount))
