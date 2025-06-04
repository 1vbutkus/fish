# mypy: disable-error-code="call-overload"
import warnings
from typing import Callable

import numpy as np
import pandas as pd

from anre.utils.modeling.dataSet.dataSetMl import DataSetMl
from anre.utils.modeling.diagnostic.metric import Metric
from anre.utils.modeling.model.iModel import IModel
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.shapExplainer.shapExplainer import ShapExplainer
from anre.utils.worker.worker import Worker


class FeatureSelection:
    def __init__(self, modelFactory: Callable, trainDs, testDs) -> None:
        assert callable(modelFactory)
        assert isinstance(trainDs, DataSetMl)
        assert isinstance(testDs, DataSetMl)

        self._modelFactory = modelFactory
        self._trainDs = trainDs
        self._testDs = testDs

    def get_targetPerformanceSr(self, xFields, trainDs, testDs):
        modelFactory = self._modelFactory
        _model = modelFactory(xFields=xFields, X=trainDs.X, target=trainDs.target)
        assert isinstance(_model, IModel)
        assert _model.isFitted, "Model from modelFactory must be already fitted"
        targetPerformanceSr = Metric.get_targetPerformanceDf(
            model=_model, dsDict=dict(train=trainDs, test=testDs)
        ).stack()
        return targetPerformanceSr

    def get_targetPerformanceDf(
        self,
        xFields: list[str] | None = None,
        xSortBy: str | None = None,
        worker: Worker | None = None,
    ):
        trainDs = self._trainDs
        testDs = self._testDs

        assert xSortBy is None or isinstance(xSortBy, str)

        if xFields is None:
            xFields = list(trainDs.headerDict["X"])

        if xSortBy is None:
            featurePriorityList = xFields
        elif xSortBy == "correlation":
            featurePriorityList = list(
                trainDs.X.corrwith(trainDs.y).abs().sort_values(ascending=False).index
            )
        elif xSortBy == "modelFeatureImportance":
            _model = self._modelFactory(xFields=xFields)
            assert isinstance(_model, LeafModel)
            _model.fit(trainDs.X, trainDs.y)
            featureImportanceSr = _model.get_featureImportanceSr()
            featurePriorityList = list(featureImportanceSr.sort_values(ascending=False).index)
        elif xSortBy == "shapFeatureImportance":
            _model = self._modelFactory(xFields=xFields)
            assert isinstance(_model, LeafModel)
            _model.fit(trainDs.X, trainDs.y)
            modelShapExplainer = ShapExplainer.new_fromModel(model=_model)
            modelShapExplainer.set_explanation(inputDf=testDs.X.sample(2000))
            featureImportanceSr = modelShapExplainer.get_importanceSr()
            featurePriorityList = list(featureImportanceSr.sort_values(ascending=False).index)
        else:
            msg = f"Value of {xSortBy=} is not handled."
            raise ValueError(msg)

        kwargsList = []
        _kwargs = {
            'xFields': [],
            'trainDs': trainDs,
            'testDs': testDs,
            'name': '__zero__',
            'isZero': True,
        }
        kwargsList.append(_kwargs)

        _xFields_toRun = []
        for _xField in featurePriorityList:
            _xFields_toRun.append(_xField)
            _kwargs = {
                'xFields': list(_xFields_toRun),
                'trainDs': trainDs,
                'testDs': testDs,
                'name': _xField,
                'isZero': False,
            }
            kwargsList.append(_kwargs)

        worker = Worker.new_sequential() if worker is None else worker
        targetPerformanceSrList = worker.starmap(
            self._get_targetPerformanceSr, kwargs_list=kwargsList
        )

        targetPerformanceDf = pd.concat(targetPerformanceSrList, axis=1).transpose()
        return targetPerformanceDf

    def _get_targetPerformanceSr(self, xFields, trainDs, testDs, name, isZero: bool):
        assert isinstance(isZero, bool)

        if isZero:
            _trainDs_zero = self._get_zeroDf(ds=trainDs)
            _testDs_zero = self._get_zeroDf(ds=testDs)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                targetPerformanceSr = self.get_targetPerformanceSr(
                    xFields=["x"], trainDs=_trainDs_zero, testDs=_testDs_zero
                )
        else:
            targetPerformanceSr = self.get_targetPerformanceSr(
                xFields=xFields, trainDs=trainDs, testDs=testDs
            )

        targetPerformanceSr.name = name
        return targetPerformanceSr

    @staticmethod
    def _get_zeroDf(ds: DataSetMl) -> DataSetMl:
        return DataSetMl.new(
            X=pd.DataFrame(
                np.full(fill_value=0, shape=(ds.target.shape[0], 1)),  # type: ignore[attr-defined]
                index=ds.target.index,
                columns=["x"],
            ),
            target=ds.target,
        )
