# mypy: disable-error-code="var-annotated"
from typing import Iterable

from anre.utils.modeling.timeSlice.levelSlicer import LevelSlicer
from anre.utils.modeling.timeSlice.pureSlice import PureSlice
from anre.utils.modeling.timeSlice.timeSlice import TimeSlice
from anre.utils.parameter.parameter import Parameter


class TimeSliceSchema:
    @classmethod
    def new_by_cv_count(cls, values: Iterable, n_splits: int) -> 'TimeSliceSchema':
        assert isinstance(values, Iterable)
        if not isinstance(values, list):
            values = list(values)
        assert isinstance(values, list)
        assert n_splits > 1

        values_count = len(values)
        assert values_count >= n_splits
        test_size = values_count // n_splits
        train_size = values_count - test_size
        test_init_poss = values_count - test_size * n_splits
        assert test_init_poss >= 0
        params = {
            'trainSizeDefault': train_size,
            'testSizeDefault': test_size,
            'levels': [
                {
                    'shiftStep': test_size,
                    'testInitPoss': test_init_poss,
                },
            ],
        }
        self = cls(values=values, prm=params)
        # check if matching n_splits
        rootTimeSlice = self.get_rootTimeSlice()
        assert len(rootTimeSlice.get_childrenList()) == n_splits
        return self

    def __init__(self, values: Iterable, prm: Parameter | dict) -> None:
        if isinstance(prm, dict):
            prm = Parameter(prm)
        assert isinstance(prm, Parameter)
        assert isinstance(values, Iterable)
        if not isinstance(values, list):
            values = list(values)
        assert isinstance(values, list)

        self._validatePrm(values=values, prm=prm)
        self._prm: Parameter = prm
        self._values: list = values

    def get_rootTimeSlice(self) -> TimeSlice:
        return self._get_rootTimeSlice(values=self._values, prm=self._prm)

    @classmethod
    def _get_rootTimeSlice(cls, values: list, prm: Parameter) -> TimeSlice:
        rootPureSlice = PureSlice(
            sliceId=None,
            values=values,
        )
        rootTimeSlice = TimeSlice(
            pureSlice=rootPureSlice,
        )
        levelSlicerList = cls._get_levelSlicerList(prm=prm)
        rootTimeSlice.add_children(levelSlicerList=levelSlicerList)
        return rootTimeSlice

    @staticmethod
    def _get_levelSlicerList(prm) -> list[LevelSlicer]:
        trainSizeDefault = prm['trainSizeDefault']
        testSizeDefault = prm['testSizeDefault']

        levelSlicerList = []
        levelParamsList = prm['levels']
        trainSizeRequirement = None
        for levelParams in reversed(levelParamsList):
            trainSize = levelParams.pop('trainSize', trainSizeDefault)
            testSize = levelParams.pop('testSize', testSizeDefault)
            levelSlicer = LevelSlicer(
                trainSize=trainSize,
                trainSizeRequirement=trainSizeRequirement,
                testSize=testSize,
                **levelParams,
            )
            trainSizeRequirement = levelSlicer.get_valueCountRequirement()
            levelSlicerList.insert(0, levelSlicer)
        return levelSlicerList

    @staticmethod
    def _validatePrm(values, prm):
        params = prm.paramDict

        assert 'values' not in params
        assert 'trainSizeDefault' in params
        assert 'testSizeDefault' in params
        assert 'levels' in params
        levelsList = params['levels']
        assert len(levelsList) > 0
        assert values
