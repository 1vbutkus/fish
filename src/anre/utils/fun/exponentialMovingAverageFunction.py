import numpy as np
import pandas as pd

from anre.utils.fun.lastValueStepFunction import LastValueStepFunction
from anre.utils.functions import convert_x2npArray
from anre.utils.time.convert import Convert as TimeConvert
from anre.utils.timeSeries.smooth.exponentialMovingAverage.exponentialMovingAverage import (
    ExponentialMovingAverage,
)


class ExponentialMovingAverageFunction:
    @classmethod
    def new_sr(cls, sr: pd.Series, halflife: float, initValue: float | None = None):
        assert isinstance(sr, pd.Series)
        return cls.new_fromStepChanges(
            x=sr.index.values,
            y=sr.values,  # type: ignore[arg-type]
            halflife=halflife,
            initValue=initValue,  # type: ignore[arg-type]
        )

    @classmethod
    def new_fromStepChanges(
        cls,
        x: np.ndarray | pd.Series,
        y: np.ndarray | pd.Series,
        halflife: float,
        initValue: float | None = None,
    ):
        """Get emaFunction that can be used to calculate smoothed values of step function

        Note: the time between elements in NOT unobserved - contrary, it is known constant,thus the smoothed value should aproach it

        """

        assert halflife > 0, 'halflife must be positive'
        assert isinstance(x, (np.ndarray, pd.Series))
        assert isinstance(y, (np.ndarray, pd.Series))

        tx = convert_x2npArray(x=x)
        ty = convert_x2npArray(x=y)
        del x, y
        assert not np.any(pd.isna(tx)), 'x values cant be nan'
        assert np.all(tx[:-1] < tx[1:]), 'We expect monotonically increasing x values'
        assert len(tx) == len(ty)
        assert len(tx) > 0

        initValue = ty[0] if pd.isna(initValue) else initValue
        if pd.api.types.is_datetime64_any_dtype(tx):
            tx_sec = TimeConvert.dt2seconds(tx)
        else:
            tx_sec = tx

        timeDelta = np.diff(tx_sec).astype(float)
        alphaAr = ExponentialMovingAverage.get_alphaOfIrregularTime(
            timeDelta=timeDelta, halflife=halflife
        )
        emaAr = ExponentialMovingAverage.get_emaAr_fromAlphaAndY(
            alphaAr=alphaAr, yAr=ty[:-1], initValue=initValue
        )
        muAr = np.concatenate(([initValue], emaAr), dtype=emaAr.dtype)

        ### compose functions
        yFun = LastValueStepFunction.new(x=tx, y=ty, fill_value=ty[0])
        lastUpdateMuFun = LastValueStepFunction.new(x=tx, y=muAr)
        lastUpdateXFun = LastValueStepFunction.new(x=tx, y=tx_sec)
        return cls(
            yFun=yFun,
            lastUpdateMuFun=lastUpdateMuFun,
            lastUpdateXFun=lastUpdateXFun,
            halflife=halflife,
        )

    def __call__(self, x):
        return self._get_funValue_atX(x=x)

    def __init__(
        self,
        yFun: LastValueStepFunction,
        lastUpdateMuFun: LastValueStepFunction,
        lastUpdateXFun: LastValueStepFunction,
        halflife: float,
    ):
        self._yFun = yFun
        self._lastUpdateMuFun = lastUpdateMuFun
        self._lastUpdateXFun = lastUpdateXFun
        self._halflife = halflife

    @property
    def halflife(self) -> float:
        return self._halflife

    def _alphaFun(self, timeDelta):
        return ExponentialMovingAverage.get_alphaOfIrregularTime(
            timeDelta=timeDelta, halflife=self._halflife
        )

    def _xDeltaFun(self, x, x_sec, update_asap: bool):
        return (x_sec - self._lastUpdateXFun(x, update_asap=update_asap).astype(float)).astype(
            float
        )

    def _get_funValue_atX(self, x: np.ndarray | pd.Series):
        tx = convert_x2npArray(x=x)
        if pd.api.types.is_datetime64_any_dtype(tx):
            tx_sec = TimeConvert.dt2seconds(tx)
        else:
            tx_sec = tx
        y = self._yFun(tx, update_asap=True)
        lastMu = self._lastUpdateMuFun(tx, update_asap=True)
        xDelta = np.nan_to_num(self._xDeltaFun(x=tx, x_sec=tx_sec, update_asap=True), nan=0)
        alpha = self._alphaFun(xDelta)
        ema = alpha * y + (1 - alpha) * lastMu
        return ema.astype(float)
