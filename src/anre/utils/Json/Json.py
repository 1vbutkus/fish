from functools import reduce
from typing import Any, Sequence

import orjson
from cachetools import cached

from anre.utils.fileSystem.fileSystem import FileSystem

RawDataType = bytes | str
JsonDataType = list[Any] | list[dict[str, Any]] | dict[str, Any] | int | float | str


class Json:
    @staticmethod
    def dumps(obj: JsonDataType, useIndent=False, useNumpy: bool = False) -> bytes:
        optionList = []

        if useIndent:
            optionList.append(orjson.OPT_INDENT_2)

        if useNumpy:
            optionList.append(orjson.OPT_SERIALIZE_NUMPY)

        if optionList:
            option = reduce(lambda x, y: x | y, optionList)
            returnObj = orjson.dumps(obj, option=option)
        else:
            returnObj = orjson.dumps(obj)

        return returnObj

    @staticmethod
    def dumps_to_str(obj: JsonDataType, useIndent=False, useNumpy: bool = False) -> str:
        return Json.dumps(obj, useIndent=useIndent, useNumpy=useNumpy).decode('ASCII')

    @staticmethod
    def loads(obj: RawDataType) -> JsonDataType:
        return orjson.loads(obj)

    @staticmethod
    def linesDumps(objList: list[Any], appendNewLine: bool = True) -> list[bytes]:
        if appendNewLine:
            obj = [orjson.dumps(obj, option=orjson.OPT_APPEND_NEWLINE) for obj in objList]
        else:
            obj = [orjson.dumps(obj) for obj in objList]
        return obj

    @staticmethod
    def lines_dumps_to_str(objList: list[Any], appendNewLine: bool = True) -> list[str]:
        obj = Json.linesDumps(objList, appendNewLine=appendNewLine)
        return [el.decode('ASCII') for el in obj]

    @staticmethod
    def lines_loads(obj_list: Sequence[RawDataType]) -> list[Any]:
        return [orjson.loads(obj) for obj in obj_list]

    @classmethod
    def dump(
        cls,
        obj: Any,
        path: str,
        overwrite: bool = False,
        archive: bool = False,
        useIndent=False,
        useNumpy=False,
    ) -> None:
        dumps = cls.dumps(obj, useIndent=useIndent, useNumpy=useNumpy)
        FileSystem.write_bytes(dumps=dumps, path=path, overwrite=overwrite, archive=archive)

    @classmethod
    def linesDump(
        cls, objList: list[Any], path: str, overwrite: bool = False, archive: bool = False
    ) -> None:
        dumps = cls.linesDumps(objList)
        FileSystem.write_bytes(dumps=dumps, path=path, overwrite=overwrite, archive=archive)

    @classmethod
    def linesLoad(cls, path: str) -> list[Any]:
        objBytesList = FileSystem.read_byte_lines(path=path)
        obj = [orjson.loads(objBytes) for objBytes in objBytesList]
        return obj

    @classmethod
    def load(cls, path: str, cache: bool = False):
        if cache:
            metadataStr = FileSystem.get_file_metadata_str_for_cache_reload(path)
            return cls._load_cache(path=path, metadataStr=metadataStr, cache=cache)
        else:
            return cls._load(path=path, cache=cache)

    @classmethod
    @cached({})
    def _load_cache(cls, path: str, metadataStr: str, cache: bool = False):
        # The metadataStr is used to skip caching when the file gets updated. If the files changes, the metadata
        # will change, and we will reread the file instead of returning an outdated copy.
        return cls._load(path=path, cache=cache)

    @classmethod
    def _load(cls, path: str, cache: bool = False) -> Any:
        objBytes = FileSystem.read_bytes(path=path, cache=cache)
        obj = orjson.loads(objBytes)
        return obj
