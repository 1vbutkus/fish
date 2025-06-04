import datetime

import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.fun.exponentialMovingAverageFunction import ExponentialMovingAverageFunction


class TestEma(testutil.TestCase):
    def test_smoothness(self) -> None:
        halflife = 0.9
        x = np.array([0, 1, 3, 7])
        y = np.array([1, 2, 0, 7])

        emaFun = ExponentialMovingAverageFunction.new_fromStepChanges(x=x, y=y, halflife=halflife)

        newX = np.arange(-0.5, 9, 0.25)
        emaAr_act = emaFun(newX)
        emaAr_exp = np.array([
            np.nan,
            np.nan,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.1751394056646975,
            1.3196049999128117,
            1.4387689758453135,
            1.5370626438563548,
            1.6181412172713392,
            1.6850197375262816,
            1.7401851934920392,
            1.7856890042867317,
            1.4729444933739682,
            1.2149738702273623,
            1.002184068697605,
            0.8266621465392778,
            0.6818810295088857,
            0.5624567912666676,
            0.46394844313215045,
            0.38269278854292405,
            0.3156682010053505,
            0.2603822598940293,
            0.21477906565055802,
            0.17716278774330038,
            0.1461346023920378,
            0.12054067498204932,
            0.09942925280727184,
            0.08201527256492122,
            1.2936270061253548,
            2.2930377807736413,
            3.117412346335131,
            3.7974064404390893,
            4.358306773046174,
            4.820971354763325,
            5.202605136616427,
        ])
        assert np.all(np.isnan(emaAr_act) == np.isnan(emaAr_exp))
        assert np.max(np.abs(np.nan_to_num(emaAr_act - emaAr_exp, nan=0))) < 1e-6
        # plt.plot(newX, emaAr_act)
        # plt.show()

    def test_get_emaFunction_fromStepChanges_numbers(self) -> None:
        halflife = 0.5
        x = np.array([0, 1, 3, 7])
        y = np.array([1, 2, 0, 7])

        emaFun = ExponentialMovingAverageFunction.new_fromStepChanges(x=x, y=y, halflife=halflife)

        emaAr_act = emaFun(x)
        emaAr_exp = np.array([1.0, 1.0, 1.9375, 0.007568359375])
        assert np.all(np.isnan(emaAr_act) == np.isnan(emaAr_exp))
        assert np.max(np.abs(np.nan_to_num(emaAr_act - emaAr_exp, nan=0))) < 1e-6

        newX = np.arange(-0.5, 9, 0.7)
        emaAr_act = emaFun(newX)
        emaAr_exp = np.array([
            np.nan,
            1.0,
            1.0,
            1.5647247184,
            1.8350615112,
            1.9375,
            0.7341752119,
            0.2782003829,
            0.1054182323,
            0.0399460403,
            0.0151367188,
            1.7007277611,
            4.9919513192,
            6.2390918371,
        ])
        assert np.all(np.isnan(emaAr_act) == np.isnan(emaAr_exp))
        assert np.max(np.abs(np.nan_to_num(emaAr_act - emaAr_exp, nan=0))) < 1e-6

        newX = np.arange(-0.5, 9, 0.25)
        emaAr_act = emaFun(newX)
        emaAr_exp = np.array([
            np.nan,
            np.nan,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.29289322,
            1.5,
            1.64644661,
            1.75,
            1.8232233,
            1.875,
            1.91161165,
            1.9375,
            1.37001939,
            0.96875,
            0.68500969,
            0.484375,
            0.34250485,
            0.2421875,
            0.17125242,
            0.12109375,
            0.08562621,
            0.06054688,
            0.04281311,
            0.03027344,
            0.02140655,
            0.01513672,
            0.01070328,
            0.00756836,
            2.05560417,
            3.50378418,
            4.52780208,
            5.25189209,
            5.76390104,
            6.12594604,
            6.38195052,
        ])
        assert np.all(np.isnan(emaAr_act) == np.isnan(emaAr_exp))
        assert np.max(np.abs(np.nan_to_num(emaAr_act - emaAr_exp, nan=0))) < 1e-6

    def test_get_emaFunction_fromStepChanges_dt(self) -> None:
        halflife = 0.5
        x = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 0),
            datetime.datetime(2022, 7, 7, 13, 25, 1),
            datetime.datetime(2022, 7, 7, 13, 25, 3),
            datetime.datetime(2022, 7, 7, 13, 25, 7),
        ])
        y = np.array([1, 2, 0, 7])

        emaFun = ExponentialMovingAverageFunction.new_fromStepChanges(x=x, y=y, halflife=halflife)
        newX = pd.Series([x[0] + datetime.timedelta(seconds=sh) for sh in np.arange(-0.5, 9, 0.7)])
        emaAr_act = emaFun(newX)
        emaAr_exp = np.array([
            np.nan,
            1.0,
            1.0,
            1.5647246608,
            1.8350615003,
            1.9375,
            0.7341751634,
            0.2782003461,
            0.1054182462,
            0.0399460429,
            0.0151367188,
            1.7007281114,
            4.9919515847,
            6.2390917365,
        ])
        assert np.all(np.isnan(emaAr_act) == np.isnan(emaAr_exp))
        assert np.max(np.abs(np.nan_to_num(emaAr_act - emaAr_exp, nan=0))) < 1e-6

    def test_get_emaFunction_fromStepChanges_dt_high_precision(self) -> None:
        halflife = 0.5
        x = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 0),
            datetime.datetime(2022, 7, 7, 13, 25, 1),
            datetime.datetime(2022, 7, 7, 13, 25, 1),
            datetime.datetime(2022, 7, 7, 13, 25, 7),
        ])
        x.iloc[2] += np.timedelta64(1, 'ns')
        y = np.array([1, 2, 0, 7])
        assert x.is_unique

        emaFun = ExponentialMovingAverageFunction.new_fromStepChanges(x=x, y=y, halflife=halflife)
        newX = pd.Series([x[0] + datetime.timedelta(seconds=sh) for sh in np.arange(-0.5, 9, 0.7)])
        emaAr_act = emaFun(newX)
        emaAr_exp = np.array([
            np.nan,
            1.0,
            1.0,
            0.4352753391946498,
            0.16493849974965102,
            0.0625,
            0.023683069786187172,
            0.008974204711958533,
            0.0034005885874581754,
            0.0012885820292941608,
            0.00048828125,
            1.6951773918767772,
            4.9898482554955885,
            6.238294723507702,
        ])
        assert np.all(np.isnan(emaAr_act) == np.isnan(emaAr_exp))
        assert np.max(np.abs(np.nan_to_num(emaAr_act - emaAr_exp, nan=0))) < 1e-6
