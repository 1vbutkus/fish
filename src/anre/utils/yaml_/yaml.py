from typing import Any

import yaml
from cachetools import cached

from anre.utils.fileSystem.fileSystem import FileSystem


class Yaml:
    @classmethod
    def load(cls, path: str, cache: bool = False) -> Any:
        if cache:
            metadataStr = FileSystem.get_file_metadata_str_for_cache_reload(path)
            return cls._load_cache(path=path, metadataStr=metadataStr, cache=cache)
        else:
            return cls._load(path=path, cache=cache)

    @classmethod
    def save(cls, data: Any, path: str) -> None:
        with open(path, 'w') as outfile:
            yaml.safe_dump(data, outfile)

    @classmethod
    @cached({})
    def _load_cache(cls, path: str, metadataStr: str, cache: bool = False) -> Any:
        # The metadataStr is used to skip caching when the file gets updated. If the files changes, the metadata
        # will change, and we will reread the file instead of returning an outdated copy.
        return cls._load(path=path, cache=cache)

    @classmethod
    def _load(cls, path: str, cache: bool) -> Any:
        yamlData = FileSystem.read_to_str(path=path, mode='r', cache=cache)
        try:
            return yaml.safe_load(yamlData)
        except Exception as e:
            msg = f'Error loading yaml: {path}'
            raise ValueError(msg) from e
