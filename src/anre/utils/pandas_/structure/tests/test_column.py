import unittest

import numpy as np
import pandas as pd

from anre.utils.pandas_.structure.column.type import (
    Bool,
    DateTime64,
    Float64,
    Int64,
    Int64NA,
    IType,
    Numpy,
    Object,
    Pandas,
    String,
    TimeDelta64,
)


class TestIType(unittest.TestCase):
    def test_abstract_methods(self):
        with self.assertRaises(TypeError):
            IType()  # Can't instantiate abstract class


class TestNumpy(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series([1, 2, 3])

    def test_init_valid(self):
        Numpy(np.int64)
        Numpy(np.float64)

    def test_init_invalid(self):
        with self.assertRaises(AssertionError):
            Numpy("not a dtype")

    def test_is_type(self):
        self.assertTrue(Numpy(np.int64).is_type(self.sample_series.astype(np.int64)))
        self.assertFalse(Numpy(np.int64).is_type(self.sample_series.astype(np.float64)))

    def test_to_type(self):
        result = Numpy(np.float64).to_type(self.sample_series)
        self.assertEqual(result.dtype, np.float64)

    def test_get_name(self):
        self.assertEqual(Numpy(np.int64).get_name(), "<class 'numpy.int64'>")


class TestPandas(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series([1, 2, 3])

    def test_init_valid(self):
        Pandas(pd.Int64Dtype)

    def test_init_invalid(self):
        with self.assertRaises(AssertionError):
            Pandas("not a type")

    def test_is_type(self):
        self.assertTrue(Pandas(pd.Int64Dtype).is_type(self.sample_series.astype('Int64')))
        self.assertFalse(Pandas(pd.Int64Dtype).is_type(self.sample_series.astype(np.float64)))

    def test_to_type(self):
        result = Pandas(pd.Int64Dtype).to_type(self.sample_series)
        self.assertEqual(str(result.dtype), 'Int64')

    def test_get_name(self):
        self.assertEqual(Pandas(pd.Int64Dtype).get_name(), "Int64")


class TestBool(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series([True, False, True])

    def test_is_type(self):
        self.assertTrue(Bool().is_type(self.sample_series))
        self.assertFalse(Bool().is_type(pd.Series([1, 2, 3])))

    def test_to_type(self):
        result = Bool().to_type(pd.Series([1, 0, 1]))
        self.assertEqual(result.dtype, np.bool_)

    def test_get_name(self):
        self.assertEqual(Bool().get_name(), "<class 'numpy.bool'>")


class TestDateTime64(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series(['2020-01-01', '2020-01-02'])

    def test_is_type(self):
        self.assertTrue(DateTime64().is_type(pd.to_datetime(self.sample_series)))
        self.assertFalse(DateTime64().is_type(self.sample_series))

    def test_to_type(self):
        result = DateTime64().to_type(self.sample_series)
        self.assertEqual(result.dtype, np.dtype('datetime64[ns]'))

    def test_get_name(self):
        self.assertEqual(DateTime64().get_name(), "datetime64[ns]")


class TestString(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series(['a', 'b', 'c'])

    def test_is_type(self):
        self.assertTrue(String().is_type(self.sample_series))
        self.assertFalse(String().is_type(pd.Series([1, 2, 3])))

    def test_to_type(self):
        result = String().to_type(pd.Series([1, 2, 3]))
        self.assertEqual(result.dtype.type, np.object_)
        self.assertTrue(all(isinstance(x, str) for x in result))

    def test_get_name(self):
        self.assertEqual(String().get_name(), "numpy.object_ (string)")


class TestInt64(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series([1, 2, 3])

    def test_is_type(self):
        self.assertTrue(Int64().is_type(self.sample_series.astype(np.int64)))
        self.assertFalse(Int64().is_type(self.sample_series.astype(np.float64)))

    def test_to_type(self):
        result = Int64().to_type(self.sample_series.astype(np.float64))
        self.assertEqual(result.dtype, np.int64)

    def test_get_name(self):
        self.assertEqual(Int64().get_name(), "<class 'numpy.int64'>")


class TestInt64NA(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series([1, 2, 3])

    def test_is_type(self):
        self.assertTrue(Int64NA().is_type(self.sample_series.astype('Int64')))
        self.assertFalse(Int64NA().is_type(self.sample_series.astype(np.int64)))

    def test_to_type(self):
        result = Int64NA().to_type(self.sample_series)
        self.assertEqual(str(result.dtype), 'Int64')

    def test_get_name(self):
        self.assertEqual(Int64NA().get_name(), "Int64")


class TestFloat64(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series([1.0, 2.0, 3.0])

    def test_is_type(self):
        self.assertTrue(Float64().is_type(self.sample_series.astype(np.float64)))
        self.assertFalse(Float64().is_type(self.sample_series.astype(np.int64)))

    def test_to_type(self):
        result = Float64().to_type(self.sample_series.astype(np.int64))
        self.assertEqual(result.dtype, np.float64)

    def test_get_name(self):
        self.assertEqual(Float64().get_name(), "<class 'numpy.float64'>")


class TestObject(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series([[[1.0, 2.0], [3.0, 4.5]]])

    def test_is_type(self):
        self.assertTrue(Object().is_type(self.sample_series))

    def test_to_type(self):
        result = Object().to_type(self.sample_series)
        self.assertEqual(result.values.tolist(), [[[1.0, 2.0], [3.0, 4.5]]])

    def test_get_name(self):
        self.assertEqual(Object().get_name(), "object")


class TestTimeDelta64(unittest.TestCase):
    def setUp(self):
        self.sample_series = pd.Series(['1 day', '2 days'])

    def test_is_type(self):
        self.assertTrue(TimeDelta64().is_type(pd.to_timedelta(self.sample_series)))
        self.assertFalse(TimeDelta64().is_type(self.sample_series))

    def test_to_type(self):
        result = TimeDelta64().to_type(self.sample_series)
        self.assertEqual(result.dtype, np.dtype('timedelta64[ns]'))

    def test_get_name(self):
        self.assertEqual(TimeDelta64().get_name(), "timedelta64[ns]")
