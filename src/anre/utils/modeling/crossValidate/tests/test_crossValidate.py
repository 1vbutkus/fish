# mypy: disable-error-code="assignment"
import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.modeling.crossValidate.crossValidate import CrossValidate
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.worker.worker import Worker


class TestCrossValidate(testutil.TestCase):
    xDf: pd.DataFrame
    ySr: pd.Series

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        nRows = 1000
        nCols = 9
        X = np.random.rand(nRows, nCols)
        y = (np.random.rand(nRows) > 0.5) * 1
        xDf = pd.DataFrame(X, index=range(1000, 1000 + nRows))
        xDf.columns = [f'x{el}' for el in xDf.columns]
        ySr = pd.Series(y)

        cls.xDf = xDf
        cls.ySr = ySr

    def test_regression(self) -> None:
        xDf = self.xDf
        ySr = self.ySr

        model = LeafModel.new_lgbmRegression(
            min_child_samples=10,
            n_estimators=10,
        )

        worker = Worker.new_thread()

        cvCaseDf = CrossValidate.get_cvCaseDf(model=model, xDf=xDf, ySr=ySr, cv=5, worker=worker)
        assert isinstance(cvCaseDf, pd.DataFrame)
        assert cvCaseDf.shape[0] == 5

        cvCaseDf = CrossValidate.get_cvMeanDf(model=model, xDf=xDf, ySr=ySr, cv=5, worker=worker)
        assert isinstance(cvCaseDf, pd.DataFrame)

    def test_classification(self) -> None:
        xDf = self.xDf
        ySr = self.ySr

        model = LeafModel.new_lgbmRegression(
            min_child_samples=10,
            n_estimators=10,
        )

        worker = Worker.new_thread()

        cvCaseDf = CrossValidate.get_cvCaseDf(model=model, xDf=xDf, ySr=ySr, cv=5, worker=worker)
        assert isinstance(cvCaseDf, pd.DataFrame)
        assert cvCaseDf.shape[0] == 5

        cvCaseDf = CrossValidate.get_cvMeanDf(model=model, xDf=xDf, ySr=ySr, cv=5, worker=worker)
        assert isinstance(cvCaseDf, pd.DataFrame)
