import os
from typing import Any

from anre.utils.fileSystem import FileSystem
from anre.utils.yaml_.yaml import Yaml

_exeFilePath = os.path.dirname(__file__)
assert _exeFilePath != ''
_systemRootDir = os.path.abspath(os.path.normpath(os.path.join(_exeFilePath, '../../..')))
assert os.path.exists(_systemRootDir)


######################################### environment ###############################################


class _Environment:
    @classmethod
    def get_is_run_test(cls) -> bool:
        return 'FISH_TEST_RUN' in os.environ


########################################## path #####################################################


class _Path:
    _systemRootDir = _systemRootDir

    @classmethod
    def get_path_to_root_dir(cls, *args: Any) -> str:
        return os.path.join(cls._systemRootDir, *args)

    @classmethod
    def get_path_to_quickdata_dir(cls, *args: Any) -> str:
        return cls.get_path_to_root_dir('quickdata', *args)

    @classmethod
    def get_path_to_data_dir(cls, *args: Any) -> str:
        return os.path.join('/mnt/D/fish', *args)

    @classmethod
    def get_path_to_cache_dir(cls, *args: Any) -> str:
        return cls.get_path_to_data_dir('_cache', *args)

    @classmethod
    def get_path_to_resource_dir(cls, *args: Any) -> str:
        return cls.get_path_to_root_dir('resource', *args)





######################################### cred #####################################################


class _Cred:
    def __init__(self, path: _Path) -> None:
        self._path: _Path = path

    def get_credentials_path(self) -> str:
        return self._path.get_path_to_root_dir('_private', 'cred.yaml')

    def load_credentials(self) -> dict[str, Any]:
        return Yaml.load(path=self.get_credentials_path(), cache=True)['Cred']

    @staticmethod
    def get_mlflow_uri() -> str:
        raise NotImplementedError

    def get_polymarket_creds(self):
        return self.load_credentials()['polymarket']


class Config:
    def __init__(self) -> None:
        self.path = _Path()
        self.cred = _Cred(path=self.path)
        self.environment = _Environment()

        self._create_cache_folder()

    def _create_cache_folder(self) -> None:
        path_to_cache_dir = self.path.get_path_to_cache_dir()
        if not os.path.exists(path_to_cache_dir):
            FileSystem.create_folder(path_to_cache_dir)
            print("Created cache directory:", path_to_cache_dir)

        path_to_data_dir = self.path.get_path_to_data_dir()
        assert os.path.exists(path_to_data_dir), f'outer resource dir not fount: {path_to_data_dir}'


config = Config()
