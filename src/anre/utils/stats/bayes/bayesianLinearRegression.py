# mypy: disable-error-code="assignment,operator"
from typing import Any

import numpy as np
import pandas as pd


class BayesianLinearRegression:
    def __init__(
        self, mu_0=None, lambda_0=None, alpha_0=None, betta_0=None, fit_intercept=True
    ) -> None:
        self.fit_intercept = fit_intercept
        self.n_features = None
        self.feature_names = None

        self.mu_0 = mu_0
        self.lambda_0 = lambda_0
        self.alpha_0 = alpha_0
        self.betta_0 = betta_0

        self.mu_n = None
        self.lambda_n = None
        self.alpha_n = None
        self.betta_n = None

        self.coef_ = None
        self.intercept_ = None

        self._fitCount = 0

    def new_rebuild(self, **kwargs: Any):
        kw = dict(
            mu_0=self.mu_0,
            lambda_0=self.lambda_0,
            alpha_0=self.alpha_0,
            betta_0=self.betta_0,
            fit_intercept=self.fit_intercept,
        )
        kw.update(kwargs)
        return self.__class__(**kw)

    @staticmethod
    def _get_defaults(n_features, mu_0, lambda_0, alpha_0, betta_0):
        mu_0 = np.zeros(shape=(n_features,)) if mu_0 is None else mu_0
        lambda_0 = np.zeros(shape=(n_features, n_features)) if lambda_0 is None else lambda_0
        alpha_0 = 1 if alpha_0 is None else alpha_0
        betta_0 = 1 if betta_0 is None else betta_0
        return mu_0, lambda_0, alpha_0, betta_0

    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray):
        assert self._fitCount == 0, 'Model was already. If want to reset model, use new_rebuild'

        if hasattr(X, 'columns'):
            self.feature_names = X.columns

        X, y = self._checkAndConvert_data(X=X, y=y)
        self.n_features = X.shape[1]
        X, y, X_offset, y_offset = self._process_data(X=X, y=y, fit_intercept=self.fit_intercept)

        mu_0, lambda_0, alpha_0, betta_0 = self._get_defaults(
            n_features=self.n_features,
            mu_0=self.mu_0,
            lambda_0=self.lambda_0,
            alpha_0=self.alpha_0,
            betta_0=self.betta_0,
        )

        self.mu_n, self.lambda_n, self.alpha_n, self.betta_n = self._update(
            mu_0=mu_0,
            lambda_0=lambda_0,
            alpha_0=alpha_0,
            betta_0=betta_0,
            X=X,
            y=y,
        )

        self.coef_ = self.mu_n
        self.intercept_ = y_offset - np.dot(X_offset, self.coef_.T)  # type: ignore[attr-defined]

        self._fitCount += 1

    def predict(self, X):
        assert self._fitCount > 0
        assert len(X.shape) == 2
        assert X.shape[1] == self.n_features
        if self.feature_names is not None:
            assert hasattr(X, 'columns'), (
                'Model was fitted with names, thus it must be used this way.'
            )
            assert set(X.columns) == set(self.feature_names)
            X = X[self.feature_names]
        return self.coef_ @ X.transpose() + self.intercept_

    def get_sigmaMean(self) -> float:
        if self.alpha_n > 1:
            sigmaMean = self.betta_n / (self.alpha_n - 1)
        else:
            sigmaMean = np.nan
        return sigmaMean

    def get_sigmaMap(self) -> float:
        assert self.n_features is not None
        sigmaMap = self.betta_n / (self.alpha_n + 1 + len(self.n_features) / 2)
        return sigmaMap

    @staticmethod
    def _update(mu_0, lambda_0, alpha_0, betta_0, X, y):
        n = y.shape[0]
        lambda_n = X.transpose() @ X + lambda_0
        sigma_n = np.linalg.inv(lambda_n)
        mu_n = sigma_n @ (lambda_0 @ mu_0 + X.transpose() @ y)
        alpha_n = alpha_0 + n / 2
        betta_n = (
            betta_0
            + (
                y.transpose() @ y
                + mu_0.transpose() @ lambda_0 @ mu_0
                - mu_n.transpose() @ lambda_n @ mu_n
            )
            / 2
        )
        return mu_n, lambda_n, alpha_n, betta_n

    @staticmethod
    def _checkAndConvert_data(X, y) -> tuple[np.ndarray, np.ndarray]:
        assert isinstance(X, (pd.DataFrame, np.ndarray))
        assert isinstance(y, (pd.Series, np.ndarray))

        if isinstance(X, pd.DataFrame):
            X = X.values

        if isinstance(y, (pd.DataFrame, pd.Series)):
            y = y.values

        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)

        assert len(X.shape) == 2
        assert len(y.shape) == 1
        assert X.shape[0] == y.shape[0]

        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=X.dtype)

        return X, y

    @staticmethod
    def _process_data(
        X: np.ndarray, y: np.ndarray, fit_intercept: bool
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        if fit_intercept:
            X_offset = np.average(X, axis=0)
            X = X - X_offset

            y_offset = np.average(y, axis=0)
            y = y - y_offset
        else:
            X_offset = np.zeros(X.shape[1], dtype=X.dtype)
            if y.ndim == 1:
                y_offset = X.dtype.type(0)
            else:
                y_offset = np.zeros(y.shape[1], dtype=X.dtype)

        return X, y, X_offset, y_offset
