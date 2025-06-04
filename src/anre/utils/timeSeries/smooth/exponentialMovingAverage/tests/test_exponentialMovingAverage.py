import datetime

import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.timeSeries.smooth.exponentialMovingAverage.exponentialMovingAverage import (
    ExponentialMovingAverage,
)


class TestEma(testutil.TestCase):
    def test_get_emaAr_oneObs(self) -> None:
        halflife = 0.5
        x = np.array([0])
        y = np.array([1])

        emaAr_act = ExponentialMovingAverage.get_emaAr_onIrregularTime(x=x, y=y, halflife=halflife)
        emaAr_exp = np.array([1.0])
        assert np.max(np.abs(emaAr_act - emaAr_exp)) < 1e-7

    def test_get_emaAr_fromIrregularTime_numbers(self) -> None:
        halflife = 0.5
        x = np.array([0, 1, 3, 7])
        y = np.array([1, 2, 0, 7])

        emaAr_act = ExponentialMovingAverage.get_emaAr_onIrregularTime(x=x, y=y, halflife=halflife)
        emaAr_exp = np.array([1.0, 1.75, 0.109375, 6.9730835])
        assert np.max(np.abs(emaAr_act - emaAr_exp)) < 1e-7

    def test_get_emaAr_fromIrregularTime_dt(self) -> None:
        halflife = 0.5
        x = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 0),
            datetime.datetime(2022, 7, 7, 13, 25, 1),
            datetime.datetime(2022, 7, 7, 13, 25, 3),
            datetime.datetime(2022, 7, 7, 13, 25, 7),
        ])
        y = np.array([1, 2, 0, 7])

        emaAr_act = ExponentialMovingAverage.get_emaAr_onIrregularTime(x=x, y=y, halflife=halflife)
        emaAr_exp = np.array([1.0, 1.75, 0.109375, 6.9730835])
        assert np.max(np.abs(emaAr_act - emaAr_exp)) < 1e-7
