class SplitIds:
    def __init__(self, sliceId: int, testIds: list, trainIds: list, generalTrainIds: list) -> None:
        assert isinstance(sliceId, int)
        assert isinstance(testIds, list)
        assert isinstance(trainIds, list)
        assert isinstance(generalTrainIds, list)

        assert set(trainIds) <= set(generalTrainIds)

        self.sliceId = sliceId
        self.testIds = testIds
        self.trainIds = trainIds
        self.generalTrainIds = generalTrainIds
