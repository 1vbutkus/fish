import _pickle as pkl
import hashlib
from typing import Any


class Hash:
    @classmethod
    def get_dictHash(cls, dict_: dict) -> str:
        """Special function that dont care about an order of first level items"""
        return cls._get_hashStr_basic(
            sorted([
                (cls._get_hashStr_basic(k), cls._get_hashStr_basic(v)) for k, v in dict_.items()
            ])
        )
        # alternative from internet, that do not need sorting
        # cls._get_hashStr_basic(reduce(xor, map(cls._get_hashInt_basic, dict_.items()), 0))

    @classmethod
    def get_hash(cls, obj: Any) -> str:
        if isinstance(obj, dict):
            return cls.get_dictHash(dict_=obj)
        else:
            return cls._get_hashStr_basic(obj=obj)

    @classmethod
    def get_strHashInt(cls, str_: str, lim=16) -> int:
        assert isinstance(str_, str)
        assert lim > 1
        return cls.convert_hexdigToInt(cls._get_hashStr_basic(obj=str_))

    @staticmethod
    def convert_hexdigToInt(hexdig: str, lim=16) -> int:
        return int(hexdig[:lim], 16)

    @staticmethod
    def _get_hashStr_basic(obj: Any) -> str:
        if isinstance(obj, str):
            return hashlib.md5(obj.encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(pkl.dumps(obj)).hexdigest()

    @classmethod
    def _get_hashInt_basic(cls, obj) -> int:
        return int(cls._get_hashStr_basic(obj), 16)
