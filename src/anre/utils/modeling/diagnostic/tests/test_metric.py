import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.modeling.dataSet.dataSetMl import DataSetMl
from anre.utils.modeling.diagnostic.metric import Metric
from anre.utils.modeling.model.leafModel.leafModel import LeafModel


class TestMetric(testutil.TestCase):
    def test_regression(self) -> None:
        yTrue = np.random.random(size=20)
        yPred = np.random.random(size=20)
        targetPerformanceDict = Metric.get_targetPerformanceDict_regression(
            yTrue=yTrue, yPred=yPred
        )
        self.assertIsInstance(targetPerformanceDict, dict)
        self.assertTrue(bool(targetPerformanceDict))

    def test_regression_2d(self) -> None:
        yTrue = np.random.random(size=20).reshape(10, -1)
        yPred = np.random.random(size=20).reshape(10, -1)
        targetPerformanceDict = Metric.get_targetPerformanceDict_regression(
            yTrue=yTrue, yPred=yPred
        )
        self.assertIsInstance(targetPerformanceDict, dict)
        self.assertTrue(bool(targetPerformanceDict))

    def test_classification(self) -> None:
        yTrue = np.random.random(size=20) > 0.5
        yPred = np.random.random(size=20)
        targetPerformanceDict = Metric.get_targetPerformanceDict_classification(
            yTrue=yTrue, yPred=yPred
        )
        self.assertIsInstance(targetPerformanceDict, dict)
        self.assertTrue(bool(targetPerformanceDict))

    def test_targetPerformanceDf(self) -> None:
        df = pd.DataFrame(np.random.rand(50, 5), columns=list('ABCDE'))
        headerDict = {'X': ['A', 'B'], 'y': 'E'}
        ds = DataSetMl(df=df, name='testName', headerDict=headerDict)  # type: ignore[arg-type]

        model = LeafModel.new_lgbmRegression(min_child_samples=10, n_estimators=10, max_depth=3)
        model.fit(ds.X, ds.y)

        targetPerformanceDf = Metric.get_targetPerformanceDf(
            model=model, dsDict=dict(train=ds, test=ds)
        )
        assert isinstance(targetPerformanceDf, pd.DataFrame)
