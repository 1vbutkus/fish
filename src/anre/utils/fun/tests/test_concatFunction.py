# mypy: disable-error-code="assignment"
import datetime

import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.fun.concatFunction import ConcatFunction
from anre.utils.fun.lastValueStepFunction import LastValueStepFunction


class TestLastValueStepFunction(testutil.TestCase):
    def test_numeric_to_numeric(self) -> None:
        fun_map = {
            1.1: LastValueStepFunction.new_with_data_processing(pd.Series([1.1, 1.1])),
            3.3: lambda x: x * 0 + 3.2,
            2.3: LastValueStepFunction.new_with_data_processing(pd.Series([2.3])),
        }
        fun = ConcatFunction(fun_map=fun_map, fill_value=np.nan, dtype=float)
        x = np.array([-1, 0.2, 1.2, 2.5, 4.2, 5, 10.1])
        res_act = fun(x)
        res_exp = np.array([np.nan, np.nan, 1.1, 2.3, 3.2, 3.2, 3.2])
        assert all((res_act == res_exp) | (np.isnan(res_act) & np.isnan(res_exp)))

    def test_numeric_to_numeric_seriesOnly(self) -> None:
        def wrap(fun):
            def newFun(x):
                assert isinstance(x, pd.Series)
                return fun(x)

            return newFun

        fun_map = {
            1.1: wrap(LastValueStepFunction.new_with_data_processing(pd.Series([1.1, 1.1]))),
            3.3: wrap(lambda x: x * 0 + 3.2),
            2.3: wrap(LastValueStepFunction.new_with_data_processing(pd.Series([2.3]))),
        }
        fun = ConcatFunction(fun_map=fun_map, fill_value=np.nan, dtype=float)
        x = np.array([-1, 0.2, 1.2, 2.5, 4.2, 5, 10.1])
        with self.assertRaises(AssertionError):
            _ = fun(x)

        x = pd.Series(x)
        res_act = fun(x)

        res_exp = pd.Series(np.array([np.nan, np.nan, 1.1, 2.3, 3.2, 3.2, 3.2]))
        assert res_act.equals(res_exp)

    def test_dt_to_numeric(self) -> None:
        fun_map = {
            datetime.datetime(2022, 7, 1): LastValueStepFunction.new_with_data_processing(
                pd.Series([1.1, 1.1])
            ),
            datetime.datetime(2022, 7, 3): lambda x: np.full(len(x), 3.3),
            datetime.datetime(2022, 7, 2): LastValueStepFunction.new_with_data_processing(
                pd.Series([2.3])
            ),
        }
        fun = ConcatFunction(fun_map=fun_map, fill_value=np.nan, dtype=float)
        x = [
            datetime.datetime(2022, 7, 1),
            datetime.datetime(2022, 7, 2),
            datetime.datetime(2022, 7, 3),
        ]
        res_act = fun(x)
        res_exp = np.array([1.1, 2.3, 3.3])
        assert all((res_act == res_exp) | (np.isnan(res_act) & np.isnan(res_exp)))

    def test_dt_to_dt(self) -> None:
        x = y = pd.Series([
            datetime.datetime(2022, 7, 1),
            datetime.datetime(2022, 7, 2),
            datetime.datetime(2022, 7, 3),
        ])

        fun_map = {
            datetime.datetime(2022, 7, 1): LastValueStepFunction.new(x=x, y=y),
            datetime.datetime(2022, 7, 2): LastValueStepFunction.new(x=x, y=y),
            datetime.datetime(2022, 7, 3): LastValueStepFunction.new(x=x, y=y),
        }
        fun = ConcatFunction(fun_map=fun_map, fill_value=np.nan, dtype=np.dtype('datetime64[ns]'))
        res_act = fun(x)
        res_exp = np.array(
            [
                datetime.datetime(2022, 7, 1),
                datetime.datetime(2022, 7, 2),
                datetime.datetime(2022, 7, 3),
            ],
            dtype=np.dtype('datetime64[ns]'),
        )
        assert all((res_act == res_exp) | (np.isnan(res_act) & np.isnan(res_exp)))

        res_act = fun(x - datetime.timedelta(seconds=1))
        res_exp = np.array(
            [None, datetime.datetime(2022, 7, 1), datetime.datetime(2022, 7, 2)],
            dtype=np.dtype('datetime64[ns]'),
        )
        assert all((res_act == res_exp) | (np.isnan(res_act) & np.isnan(res_exp)))

    def test_dt_to_dt_from_lastValueStepFunctions(self) -> None:
        x = y = pd.Series([
            datetime.datetime(2022, 7, 1),
            datetime.datetime(2022, 7, 2),
            datetime.datetime(2022, 7, 3),
        ])

        fun_map = {
            datetime.datetime(2022, 7, 1): LastValueStepFunction.new(x=x, y=y),
            datetime.datetime(2022, 7, 2): LastValueStepFunction.new(x=x, y=y),
            datetime.datetime(2022, 7, 3): LastValueStepFunction.new(x=x, y=y),
        }
        fun = ConcatFunction.new_from_lastValueStepFunctions(fun_map=fun_map)
        res_act = fun(x)
        res_exp = np.array(
            [
                datetime.datetime(2022, 7, 1),
                datetime.datetime(2022, 7, 2),
                datetime.datetime(2022, 7, 3),
            ],
            dtype=np.dtype('datetime64[ns]'),
        )
        assert all((res_act == res_exp) | (np.isnan(res_act) & np.isnan(res_exp)))

        res_act = fun(x - datetime.timedelta(seconds=1))
        res_exp = np.array(
            [None, datetime.datetime(2022, 7, 1), datetime.datetime(2022, 7, 2)],
            dtype=np.dtype('datetime64[ns]'),
        )
        assert all((res_act == res_exp) | (np.isnan(res_act) & np.isnan(res_exp)))
