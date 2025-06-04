# mypy: disable-error-code="assignment,var-annotated"
import datetime
import pickle

import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.fun.lastValueStepFunction import LastValueStepFunction


class TestLastValueStepFunction(testutil.TestCase):
    def test_new_fromSr(self) -> None:
        sr = pd.Series([1, 2, 3])
        fun = LastValueStepFunction.new_with_data_processing(x=sr, fill_value=0)
        _sr = fun(sr.index)
        self.assertTrue(_sr.equals(sr))
        self.assertEqual(_sr.dtype, sr.dtype)

        sr = pd.Series([1, 2, 3, 3, 3, 3])
        fun = LastValueStepFunction.new_with_data_processing(x=sr, fill_value=0)
        _sr = fun(sr.index)
        self.assertTrue(_sr.equals(sr))
        self.assertEqual(_sr.dtype, sr.dtype)

        fun2 = pickle.loads(pickle.dumps(fun))
        _sr = fun2(sr.index)
        self.assertTrue(_sr.equals(sr))
        self.assertEqual(_sr.dtype, sr.dtype)

    def test_integer_happyPath(self) -> None:
        x = y = pd.Series([1, 2, 3])
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=0)

        _y = fun(x)
        self.assertTrue(_y.equals(y))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(x + 0.5)
        self.assertTrue(_y.equals(y))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(x, update_asap=False)
        self.assertTrue(_y.equals(y - 1))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(x + 0.0001, update_asap=False)
        self.assertTrue(_y.equals(y))
        self.assertEqual(_y.dtype, y.dtype)

        self.assertEqual(fun(0), 0)
        self.assertEqual(fun(2), 2)
        self.assertEqual(fun(2.5), 2)

        self.assertEqual(fun(0, update_asap=False), 0)
        self.assertEqual(fun(2, update_asap=False), 1)
        self.assertEqual(fun(2.5, update_asap=False), 2)

        sr = fun.to_series()
        assert sr.equals(pd.Series(y.values, index=pd.Index(x.values)))

    def test_float_happyPath(self) -> None:
        x = y = pd.Series([1.0, 2.0, 3.0])
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=0.0)

        _y = fun(x)
        self.assertTrue(_y.eq(y).all())
        self.assertEqual(_y.dtype, np.float64)

        _y = fun(x + 0.5)
        self.assertTrue(_y.eq(y).all())

        _y = fun(x, update_asap=False)
        self.assertTrue(_y.eq(y - 1).all())

        _y = fun(x + 0.0001, update_asap=False)
        self.assertTrue(_y.eq(y).all())

        self.assertAlmostEqual(fun(0), 0)
        self.assertAlmostEqual(fun(2), 2)
        self.assertAlmostEqual(fun(2.5), 2)

        self.assertAlmostEqual(fun(0, update_asap=False), 0)
        self.assertAlmostEqual(fun(2, update_asap=False), 1)
        self.assertAlmostEqual(fun(2.5, update_asap=False), 2)

        sr = fun.to_series()
        assert sr.equals(pd.Series(y.values, index=pd.Index(x.values)))

    def test_dt_happyPath(self) -> None:
        x = y = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2022, 7, 7, 13, 25, 20, 927026),
            datetime.datetime(2022, 7, 7, 13, 25, 21, 927026),
        ])
        fillValue = datetime.datetime(2022, 7, 7, 13, 25, 18, 927026)
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=fillValue)
        _y = fun(x)
        self.assertTrue(_y.equals(y))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(x + datetime.timedelta(seconds=0.5))
        self.assertTrue(_y.equals(y))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(x, update_asap=False)
        self.assertTrue(_y.equals(y - datetime.timedelta(seconds=1)))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(x + datetime.timedelta(seconds=0.0001), update_asap=False)
        self.assertTrue(_y.equals(y))
        self.assertEqual(_y.dtype, y.dtype)

        self.assertEqual(fun(x[0]), y.values[0])
        self.assertEqual(fun(x[1]), y.values[1])
        self.assertEqual(fun(x[1] + datetime.timedelta(seconds=0.5)), y.values[1])

        self.assertEqual(fun(x[0], update_asap=False), pd.Series([fillValue]).values[0])
        self.assertEqual(fun(x[1], update_asap=False), y.values[0])
        self.assertEqual(
            fun(x[1] + datetime.timedelta(seconds=0.5), update_asap=False), y.values[1]
        )

        sr = fun.to_series()
        assert sr.equals(pd.Series(y.values, index=pd.Index(x.values)))

    def test_str_happyPath(self) -> None:
        x = y = pd.Series(['a', 'c', 'e'])
        fillValue = 'z'
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=fillValue)

        _y = fun(x)
        self.assertTrue(_y.equals(y))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(pd.Series(['b', 'd']))
        self.assertTrue(_y.equals(pd.Series(['a', 'c'])))
        self.assertEqual(_y.dtype, y.dtype)

        _y = fun(x, update_asap=False)
        self.assertTrue(_y.equals(pd.Series(['z', 'a', 'c'])))
        self.assertEqual(_y.dtype, y.dtype)

        self.assertEqual(fun(x[0]), y.values[0])
        self.assertEqual(fun(x[1]), y.values[1])
        self.assertEqual(fun('b'), y.values[0])

        self.assertEqual(fun(x[0], update_asap=False), fillValue)
        self.assertEqual(fun(x[1], update_asap=False), y.values[0])
        self.assertEqual(fun('b', update_asap=False), y.values[0])

    def test_fillValue_numbers(self) -> None:
        x = y = pd.Series([1, 2, 3])

        fun = LastValueStepFunction.new(x=x, y=y)
        _y = fun(x)
        self.assertTrue(_y.eq(y).all())

        fun = LastValueStepFunction.new(x=x, y=y, fill_value=np.nan)
        _y = fun(x)
        self.assertTrue(_y.eq(y).all())

        with self.assertRaises(AssertionError):
            _ = LastValueStepFunction.new(x=x, y=y, fill_value=pd.NaT)

        assert fun.to_series().equals(pd.Series(y.values, index=x, dtype=np.float64))

    def test_fillValue_datetime(self) -> None:
        x = y = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2022, 7, 7, 13, 25, 20, 927026),
            datetime.datetime(2022, 7, 7, 13, 25, 21, 927026),
        ])

        fun = LastValueStepFunction.new(x=x, y=y)
        _y = fun(x)
        self.assertTrue(_y.eq(y).all())

        fun = LastValueStepFunction.new(x=x, y=y, fill_value=np.datetime64("NaT"))
        _y = fun(x)
        self.assertTrue(_y.eq(y).all())

        with self.assertRaises(AssertionError):
            _ = LastValueStepFunction.new(x=x, y=y, fill_value=np.nan)

    def test_fillValue_str(self) -> None:
        x = y = pd.Series(['a', 'c', 'e'])
        fillValue = 'z'

        fun = LastValueStepFunction.new(x=x, y=y)
        _y = fun(x)
        self.assertTrue(_y.eq(y).all())

        fun = LastValueStepFunction.new(x=x, y=y, fill_value=fillValue)
        _y = fun(x)
        self.assertTrue(_y.eq(y).all())

    def test_differentObj_numbers(self) -> None:
        x = y = pd.Series([1, 2, 3])

        for _xInput in [x, x.values, list(x), x.astype(float), pd.Index(x), pd.array(x)]:  # type: ignore[arg-type]
            for _xPrep in [x, x.values, list(x), x.astype(float), pd.array(x)]:  # type: ignore[arg-type]
                for _yPrep in [y, y.values, list(y), y.astype(float), pd.array(x)]:  # type: ignore[arg-type]
                    fun = LastValueStepFunction.new(x=_xPrep, y=_yPrep)
                    _y = fun(_xInput)
                    self.assertTrue(np.all(_y == y.values))

    def test_differentObj_datetime(self) -> None:
        x = y = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2022, 7, 7, 13, 25, 20, 927026),
            datetime.datetime(2022, 7, 7, 13, 25, 21, 927026),
        ])

        for _xInput in [x, x.values]:
            for _xPrep in [x, x.values, list(x), pd.Index(x)]:
                for _yPrep in [y, y.values, list(y)]:
                    fun = LastValueStepFunction.new(x=_xPrep, y=_yPrep)
                    _y = fun(_xInput)
                    self.assertTrue(np.all(_y == y.values))

    def test_duplicate(self) -> None:
        x = [0, 1, 1, 1, 2, 3, 4, 5]
        y = [0, 1, 1, 1, 2, 3, 4, 5]
        with self.assertRaises(AssertionError):
            fun = LastValueStepFunction.new(x=x, y=y)

        sr = LastValueStepFunction.prepare_construction_input(
            sr=pd.Series(y, index=x),
            compress=False,
        )
        fun = LastValueStepFunction.new_with_data_processing(x=sr)

        _y = fun(x)
        self.assertTrue(np.all(_y == y))

    def test_yConst(self) -> None:
        x = [1, 2, 3, 4, 5, 6]
        y = [1, 2, 2, 2, 2, 6]
        fun = LastValueStepFunction.new(x=x, y=y)
        _y = fun(x)
        self.assertTrue(np.all(_y == y))

    def test_empty_list(self) -> None:
        x = []
        y = []
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=None)
        _y = fun(x)
        self.assertTrue(len(_y) == 0)

        self.assertTrue(fun(5) is None or np.isnan(fun(5)))
        self.assertTrue(np.all(np.isnan(fun([5, 5]).astype(float))))

    def test_empty_series(self) -> None:
        x = y = pd.Series([], dtype=np.float64)
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=None)
        _y = fun(x)
        self.assertTrue(len(_y) == 0)

        self.assertTrue(pd.isna(fun(5)))
        self.assertTrue(np.all(np.isnan(fun([5, 5]).astype(float))))

    def test_pdArray(self) -> None:
        x = pd.array([1, 2, 3, 4, 5, 6])
        y = pd.array([1, 2, 3, 4, 5, 6])
        fun = LastValueStepFunction.new(x=x, y=y)
        _y = fun(x)
        self.assertTrue(np.all(_y == y))

        x = pd.Series(pd.array([1, 2, 3, 4, 5, 6]))
        y = pd.Series(pd.array([1, 2, 3, 4, 5, 6]))
        fun = LastValueStepFunction.new(x=x, y=y)
        _y = fun(x)
        self.assertTrue(np.all(_y == y.values))  # type: ignore[attr-defined]

        x = pd.array([1, 2, 3, 4, 5, 6])
        y = pd.array([1, 2, 3, 4, 5, 6])
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=0)
        _y = fun(x)
        self.assertTrue(np.all(_y == y))

        x = pd.Series(pd.array([1, 2, 3, 4, 5, 6]))
        y = pd.Series(pd.array([1, 2, 3, 4, 5, 6]))
        fun = LastValueStepFunction.new(x=x, y=y, fill_value=0)
        _y = fun(x)
        self.assertTrue(np.all(_y == y.values))  # type: ignore[attr-defined]

    def test_withNa(self) -> None:
        x = pd.Series([1, 2, 3, 4, 5, 6])
        y = pd.Series([1, 2, 3, np.nan, 5, 6])
        fun = LastValueStepFunction.new(x=x, y=y)
        _y = fun(x)
        self.assertTrue(y.equals(_y))

    def test_duplication_with_na(self) -> None:
        sr = pd.Series([1, 2, 3, np.nan], [1, 2, 3, 3])
        with self.assertRaises(RuntimeError):
            _ = LastValueStepFunction.prepare_construction_input(sr, compress=False)
