# mypy: disable-error-code="assignment"
from typing import Iterable

import numpy as np
import pandas as pd

from anre.utils.functions import convert_x2npArray
from anre.utils.time.convert import Convert as TimeConvert


class ExponentialMovingAverage:
    @staticmethod
    def get_alphaOfIrregularTime(timeDelta: pd.Series | np.ndarray | float, halflife: float):
        return 1.0 - np.exp(np.log(0.5) * timeDelta / halflife)

    @classmethod
    def get_emaSr_fromSr(cls, sr: pd.Series, halflife) -> pd.Series:
        assert isinstance(sr, pd.Series)
        assert sr.index.is_monotonic_increasing
        _sr = sr.dropna()
        if len(_sr) > 0:
            emaSr = pd.Series(
                ExponentialMovingAverage.get_emaAr_onIrregularTime(
                    x=_sr.index, y=_sr, halflife=halflife
                ),
                index=_sr.index,
                name=sr.name,
            )
        else:
            emaSr = pd.Series([np.nan] * len(_sr), index=_sr.index, dtype=np.float64, name=sr.name)

        return emaSr.reindex(sr.index)

    @classmethod
    def get_emaDf_fromDf(cls, df: pd.DataFrame, halflife) -> pd.DataFrame:
        assert isinstance(df, pd.DataFrame)
        emaDf = pd.concat(
            [cls.get_emaSr_fromSr(sr=sr, halflife=halflife) for _, sr in df.items()], axis=1
        )
        emaDf = emaDf.reindex(df.index)
        return emaDf

    @classmethod
    def get_emaAr_onIrregularTime(cls, x: Iterable, y: Iterable, halflife: float) -> np.ndarray:
        """Calculates exponential moving average then observations are made on irregular time

        The time between elements are treated as unobserved period, the longer it is, more weight goes to last observation

        First element is initial value

        Returns np.ndarray with length len(x)
        """

        assert halflife > 0, 'halflife must be positive'
        tx = convert_x2npArray(x=x)
        ty = convert_x2npArray(x=y).astype(float)
        assert not np.any(pd.isna(tx)), 'x values cant be nan'
        assert np.all(tx[:-1] <= tx[1:]), 'We expect monotonically increasing x values'
        assert len(tx) == len(ty)
        assert len(tx) > 0

        if pd.api.types.is_datetime64_any_dtype(tx):
            tx = TimeConvert.dt2seconds(tx)

        timeDelta = np.diff(tx).astype(float)
        alphaAr = cls.get_alphaOfIrregularTime(timeDelta=timeDelta, halflife=halflife)

        initValue = ty[0]
        if len(ty) > 1:
            _emaAr = cls.get_emaAr_fromAlphaAndY(alphaAr=alphaAr, yAr=ty[1:], initValue=initValue)
        else:
            _emaAr = np.array([])
        emaAr = np.concatenate(([initValue], _emaAr), dtype=_emaAr.dtype)
        return emaAr

    @staticmethod
    def get_emaAr_fromAlphaAndY(
        alphaAr: np.ndarray, yAr: np.ndarray, initValue: float | None = None
    ) -> np.ndarray:
        assert isinstance(alphaAr, np.ndarray)
        assert isinstance(yAr, np.ndarray)
        assert len(alphaAr) == len(yAr)
        assert len(yAr) > 0

        initValue = yAr[0] if pd.isna(initValue) else initValue

        muValue = initValue
        muValueList = []
        for alpha, xValue in zip(alphaAr, yAr):
            muValue = alpha * xValue + (1 - alpha) * muValue
            muValueList.append(muValue)

        return np.array(muValueList)
