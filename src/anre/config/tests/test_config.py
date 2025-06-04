import os

from anre.config.config import config as anre_config
from anre.utils import testutil


class TestTestEnv(testutil.TestCase):
    def test_testEnvIsMarked(self) -> None:
        assert 'FISH_TEST_RUN' in os.environ, 'Running test should be marked in os.environ'

    def test_environmentIsSet(self) -> None:
        assert anre_config.environment.get_is_run_test()

    def test_path(self) -> None:
        path_to_data_dir = anre_config.path.get_path_to_data_dir()
        assert os.path.exists(path_to_data_dir), f'File path do not exist: {path_to_data_dir=}'

        path_to_root_dir = anre_config.path.get_path_to_root_dir()
        assert os.path.exists(path_to_root_dir), f'File path do not exist: {path_to_root_dir=}'

        path_to_cache_dir = anre_config.path.get_path_to_cache_dir()
        assert os.path.exists(path_to_cache_dir), f'File path do not exist: {path_to_cache_dir=}'

    def test_get_creds(self) -> None:
        polymarket_creds = anre_config.creds.get_polymarket_creds()
        assert polymarket_creds is not None
