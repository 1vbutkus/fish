import os
import tempfile
import unittest

import pandas as pd

from anre.utils.persistentWrap.dataframe_decorator import DataFrameDecorator


# Define a sample function to be decorated
def sample_function(arg1: int, arg2: str) -> pd.DataFrame:
    return pd.DataFrame({"arg1": [arg1], "arg2": [arg2]})


class TestDataFrameDecorator(unittest.TestCase):
    def setUp(self):
        self._cache_dir = tempfile.TemporaryDirectory()
        self._cache_path = self._cache_dir.name
        self.addCleanup(self._cache_dir.cleanup)

    def test_dataframe_decorator_caching(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        decorated_function = decorator(sample_function)

        df = decorated_function(arg1=1, arg2="test")
        file_path = os.path.join(self._cache_path, "test_1_test.parquet")
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(pd.read_parquet(file_path).equals(df))

        df_cached = decorated_function(arg1=1, arg2="test")
        self.assertTrue(df_cached.equals(df))

    def test_dataframe_decorator_file_path_generation(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        file_path = decorator._get_file_path({"arg1": 1, "arg2": "test"})
        self.assertEqual(file_path, os.path.join(self._cache_path, "test_1_test.parquet"))

    def test_dataframe_decorator_invalid_path_template(self):
        with self.assertRaises(AssertionError):
            DataFrameDecorator(path_template=None, cache_path="test_cache")

    def test_dataframe_decorator_missing_arguments(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        decorated_function = decorator(sample_function)
        with self.assertRaises(ValueError):
            decorated_function(arg1=1)

    def test_dataframe_decorator_extra_arguments(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        decorated_function = decorator(sample_function)
        with self.assertRaises(ValueError):
            decorated_function(arg1=1, arg2="test", extra="param")

    def test_ensure_path_generation(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        decorator(sample_function)
        file_path = decorator.ensure_path(arg1=1, arg2="test")
        self.assertEqual(file_path, os.path.join(self._cache_path, "test_1_test.parquet"))

    def test_ensure_path_file_creation(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        decorator(sample_function)
        file_path = decorator.ensure_path(arg1=2, arg2="create")
        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(file_path, os.path.join(self._cache_path, "test_2_create.parquet"))

    def test_ensure_path_existing_file(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        decorator(sample_function)

        initial_file_path = os.path.join(self._cache_path, "test_3_existing.parquet")
        pd.DataFrame({"arg1": [3], "arg2": ["existing"]}).to_parquet(initial_file_path)

        file_path = decorator.ensure_path(arg1=3, arg2="existing")
        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(file_path, initial_file_path)

    def test_skip_args_basic(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}.parquet", cache_path=self._cache_path, skip_args=["arg2"]
        )
        file_path = decorator._get_file_path({"arg1": 1, "arg2": "skip_me"})
        self.assertEqual(file_path, os.path.join(self._cache_path, "test_1.parquet"))

    def test_skip_args_default_empty(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}_{arg2}.parquet", cache_path=self._cache_path
        )
        file_path = decorator._get_file_path({"arg1": 1, "arg2": "test"})
        self.assertEqual(file_path, os.path.join(self._cache_path, "test_1_test.parquet"))

    def test_skip_args_e2e(self):
        decorator = DataFrameDecorator(
            path_template="test_{arg1}.parquet", cache_path=self._cache_path, skip_args=["arg2"]
        )
        decorated_function = decorator(sample_function)

        # Should work with arg1 only in path template
        df = decorated_function(arg1=1, arg2="test")
        file_path = os.path.join(self._cache_path, "test_1.parquet")
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(pd.read_parquet(file_path).equals(df))
