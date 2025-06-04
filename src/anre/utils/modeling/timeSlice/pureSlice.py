# mypy: disable-error-code="assignment"
from anre.utils import functions


class PureSlice:
    def __init__(
        self,
        sliceId: int | None,
        values: list,
        trainIds: list[int | None] = None,
        testIds: list[int | None] = None,
    ):
        assert sliceId is None or isinstance(sliceId, int)
        assert isinstance(values, list)
        assert values

        _allIds = self._get_allIds(values=values)
        trainIds = _allIds if trainIds is None else trainIds
        testIds = [] if testIds is None else testIds

        assert isinstance(trainIds, list)
        assert isinstance(testIds, list)

        assert not functions.diff_list(trainIds, _allIds)
        assert not functions.diff_list(testIds, _allIds)
        assert not (set(trainIds) & set(testIds))

        self._sliceId = sliceId
        self._values = values
        self._trainIds = trainIds
        self._testIds = testIds

    def __repr__(self) -> str:
        def strCap(obj):
            objStr = str(obj)
            if len(objStr) > 150:
                objStr = objStr[:75] + ' [...] ' + objStr[-75:]
            return objStr

        return f'PureSlice(\n  sliceId={self._sliceId},\n  testIds={strCap(self._testIds)},\n  trainIds={strCap(self._trainIds)},\n  values={strCap(self._values)},\n)'

    def get_trainIds(self) -> list:
        return self._trainIds.copy()

    def get_testIds(self) -> list:
        return self._testIds.copy()

    def get_trainValues(self) -> list:
        return [self._values[_id] for _id in self._trainIds]  # type: ignore[index]

    def get_testValues(self) -> list:
        return [self._values[_id] for _id in self._testIds]  # type: ignore[index]

    def get_allIds(self) -> list[int]:
        return list(range(len(self._values)))

    def get_sliceId(self) -> int | None:
        return self._sliceId

    def get_values(self) -> list[int]:
        return self._values.copy()

    @staticmethod
    def _get_allIds(values) -> list[int]:
        return list(range(len(values)))
