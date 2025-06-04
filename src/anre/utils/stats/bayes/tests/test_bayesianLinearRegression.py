# mypy: disable-error-code="operator"
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge

from anre.utils import testutil
from anre.utils.stats.bayes.bayesianLinearRegression import BayesianLinearRegression


class TestBayesianLinearRegression(testutil.TestCase):
    X: np.ndarray
    y: np.ndarray

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        dim = 3
        n = 100
        mu_real = np.random.normal(loc=10, scale=3, size=dim)
        X = np.reshape(np.random.normal(size=dim * n), shape=(n, dim)) * 2 + 3
        y = mu_real @ X.transpose() + 2 + np.random.normal(loc=0, scale=0.03, size=n)
        cls.X = X
        cls.y = y

    def test_smoke_numpy(self) -> None:
        X = self.X
        y = self.y

        xMean = np.mean(X, axis=0)
        yMean = np.mean(y, axis=0)
        bReg = BayesianLinearRegression()
        bReg.fit(X=X, y=y)
        yPred_np = bReg.predict(X=X)
        assert isinstance(yPred_np, np.ndarray)
        assert yPred_np.shape == (X.shape[0],)
        assert np.max(np.abs(xMean - np.mean(X, axis=0))) < 1e-7
        assert np.max(np.abs(yMean - np.mean(y, axis=0))) < 1e-7

        with self.assertRaises(AssertionError):
            bReg.fit(X=X, y=y)

    def test_smoke_pandas(self) -> None:
        X = self.X
        y = self.y

        xDf = pd.DataFrame(X)
        ySr = pd.Series(y)
        del X, y

        xMean = np.mean(xDf, axis=0)
        yMean = np.mean(ySr, axis=0)
        bReg = BayesianLinearRegression()
        bReg.fit(X=xDf, y=ySr)
        yPred = bReg.predict(X=xDf)
        assert isinstance(yPred, pd.Series)
        assert yPred.shape == (xDf.shape[0],)
        assert np.max(np.abs(xMean - np.mean(xDf, axis=0))) < 1e-7
        assert np.max(np.abs(yMean - np.mean(ySr, axis=0))) < 1e-7

        # mixing X order
        yPred2 = bReg.predict(X=xDf[[2, 1, 0]])
        assert np.max(np.abs(yPred2 - yPred)) < 1e-7

        # refit
        with self.assertRaises(AssertionError):
            bReg.fit(X=xDf, y=ySr)

        # drop names
        with self.assertRaises(AssertionError):
            _ = bReg.predict(X=xDf.values)

    def test_compare_numpyAndPandas(self) -> None:
        X = self.X
        y = self.y

        bReg_np = BayesianLinearRegression()
        bReg_np.fit(X=X, y=y)
        yPred_np = bReg_np.predict(X=X)

        xDf = pd.DataFrame(X)
        ySr = pd.Series(y)
        bReg_pd = BayesianLinearRegression()
        bReg_pd.fit(X=xDf, y=ySr)
        yPred_pd = bReg_pd.predict(X=xDf)

        assert np.max(np.abs(bReg_np.coef_ - bReg_pd.coef_)) < 1e-7
        assert np.max(np.abs(bReg_np.intercept_ - bReg_pd.intercept_)) < 1e-7
        assert np.max(np.abs(yPred_np - yPred_pd.values)) < 1e-7

    def test_compare_Ridge(self) -> None:
        X = self.X
        y = self.y
        colCount = X.shape[-1]

        for alpha in [0, 1, 2, 10]:
            for fit_intercept in [True, False]:
                ridReg = Ridge(alpha=alpha, fit_intercept=fit_intercept)
                ridReg.fit(X, y)
                yPred_rr = ridReg.predict(X=X)

                bReg = BayesianLinearRegression(
                    mu_0=np.zeros(colCount),
                    lambda_0=alpha * np.eye(colCount),
                    fit_intercept=fit_intercept,
                )
                bReg.fit(X=X, y=y)
                yPred_br = bReg.predict(X=X)

                assert np.max(np.abs(ridReg.coef_ - bReg.coef_)) < 1e-7
                assert np.max(np.abs(ridReg.intercept_ - bReg.intercept_)) < 1e-7
                assert np.max(np.abs(yPred_rr - yPred_br)) < 1e-7

    def test_compare_LinearRegression(self) -> None:
        X = self.X
        y = self.y

        for fit_intercept in [True, False]:
            linReg = LinearRegression(fit_intercept=fit_intercept)
            linReg.fit(X, y)
            yPred_lr = linReg.predict(X=X)

            bReg = BayesianLinearRegression(fit_intercept=fit_intercept)
            bReg.fit(X=X, y=y)
            yPred_br = bReg.predict(X=X)

            assert np.max(np.abs(linReg.coef_ - bReg.coef_)) < 1e-7
            assert np.max(np.abs(linReg.intercept_ - bReg.intercept_)) < 1e-7
            assert np.max(np.abs(yPred_lr - yPred_br)) < 1e-7
