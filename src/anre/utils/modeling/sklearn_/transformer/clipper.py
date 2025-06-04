# mypy: disable-error-code="assignment"
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

xLimType = float | list[float] | np.ndarray | None


class Clipper(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        a_min: xLimType = None,
        a_max: xLimType = None,
        q_min: xLimType = 0.005,
        q_max: xLimType = 0.995,
    ):
        a_min = self._convertInput(xLim=a_min)
        a_max = self._convertInput(xLim=a_max)
        q_min = self._convertInput(xLim=q_min)
        q_max = self._convertInput(xLim=q_max)

        self._validate(x_min=q_min, x_max=q_max)
        self._validate(x_min=a_min, x_max=a_max)

        self.q_min = q_min
        self.q_max = q_max
        self.a_min = a_min
        self.a_max = a_max

        self._is_fitted: bool = False

    def __sklearn_is_fitted__(self) -> bool:
        return self._is_fitted

    def fit(self, X, y=None):
        if self.a_min is None and self.q_min is not None:
            self.a_min = self._get_aLim(X=X, qLim=self.q_min)
        if self.a_max is None and self.q_max is not None:
            self.a_max = self._get_aLim(X=X, qLim=self.q_max)
        self._is_fitted = True
        return self

    def transform(self, X, y=None):
        return X.clip(self.a_min, self.a_max)

    @staticmethod
    def _convertInput(xLim):
        if isinstance(xLim, (list, tuple)):
            xLim = np.array(xLim)
        return xLim

    @staticmethod
    def _get_aLim(X, qLim):
        if isinstance(qLim, np.ndarray):
            assert qLim.shape[-1] == X.shape[-1]
            aLim = np.array([np.nanquantile(a=x, q=q) for x, q in zip(X.T, qLim)])
        else:
            aLim = np.nanquantile(a=X, q=qLim, axis=0)
        return aLim

    @staticmethod
    def _validate(x_min, x_max):
        assert x_min is None or isinstance(x_min, (float, int, np.ndarray))
        assert x_max is None or isinstance(x_max, (float, int, np.ndarray))

        if isinstance(x_min, np.ndarray):
            assert len(x_min.shape) == 1
        if isinstance(x_max, np.ndarray):
            assert len(x_max.shape) == 1
        if isinstance(x_min, np.ndarray) and isinstance(x_max, np.ndarray):
            assert x_min.shape == x_max.shape
        if isinstance(x_min, (float, int)) and isinstance(x_max, (float, int)):
            assert x_min <= x_max

        if x_min is not None and x_max is not None:
            ind = x_min <= x_max

            if isinstance(ind, np.ndarray):
                ind = ind | np.isnan(ind)
                assert all(ind)
            else:
                assert ind
