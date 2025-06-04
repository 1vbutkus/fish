import warnings

import numpy as np
import pandas as pd

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.modeling.dataSet.dataSetMl import DataSetMl
from anre.utils.modeling.featureSelection.featureSelection import FeatureSelection
from anre.utils.modeling.model.concatModel.concatModel import ConcatModel
from anre.utils.modeling.model.leafModel.leafModel import LeafModel


class TestFeatureSelection(testutil.TestCase):
    def test_1D(self) -> None:
        nRows = 200
        xDf = pdu.new.get_randomDf(shape=(nRows, 5))
        y = (np.random.rand(nRows) > 0.5) * 1
        ySr = pd.Series(y, index=xDf.index)

        _ds = DataSetMl.new_1d(X=xDf, y=ySr)
        trainDs, testDs = _ds.split_trainTest(test_size=0.1, seed=123456789)

        modelKwargs = {
            'classId': 'LgbmRegression',
            'hp': {
                'min_child_samples': 50,
                'n_estimators': 30,
                'n_jobs': 1,  # this one is very impornt - works way better
            },
        }

        def modelFactory(xFields, X, target):
            model = LeafModel.new_fromClassId(
                xFields=xFields,
                **modelKwargs,
            )
            model.fit(X, target)
            return model

        featureSelection = FeatureSelection(
            modelFactory=modelFactory, trainDs=trainDs, testDs=testDs
        )
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            targetPerformanceDf = featureSelection.get_targetPerformanceDf()

        self.assertIsInstance(targetPerformanceDf, pd.DataFrame)
        assert targetPerformanceDf.iloc[1:].std().median() > 1e-7

    def test_2D(self) -> None:
        nRows = 200
        xDf = pdu.new.get_randomDf(shape=(nRows, 5))
        yDf = pdu.new.get_randomDf(shape=(nRows, 5), prefix='y')

        _ds = DataSetMl.new(X=xDf, Y=yDf)
        trainDs, testDs = _ds.split_trainTest(test_size=0.1, seed=123456789)

        modelKwargs = {
            'min_child_samples': 50,
            'n_estimators': 30,
            'n_jobs': 1,  # this one is very impornt - works way better
        }

        def modelFactory(xFields, X, target):
            model = ConcatModel.new_buildFit_fromLeafModel(
                model=LeafModel.new_lgbmRegression(**modelKwargs),
                X=X[xFields],
                Y=target,
            )
            return model

        featureSelection = FeatureSelection(
            modelFactory=modelFactory, trainDs=trainDs, testDs=testDs
        )

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            targetPerformanceDf = featureSelection.get_targetPerformanceDf()

        self.assertIsInstance(targetPerformanceDf, pd.DataFrame)
        assert targetPerformanceDf.iloc[1:].std().median() > 1e-7
