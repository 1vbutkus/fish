import copy
import operator
from functools import reduce
from typing import Any


class DDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__  # type: ignore[assignment]
    __delattr__ = dict.__delitem__  # type: ignore[assignment]

    def __init__(self, d: dict) -> None:
        """dot.notation access to dictionary attributes

        Example:
            ndict = {'a':{'b':1, 'c':{'d':2}}, 'e':'val', 'f':None}
            ddict = DDict(ndict)

            ddict.a.b
            DDict.getByDotKey_obj(ndict, 'a.c.d') # the fastes!
            DDict.getByDotKey_obj_alt(ndict, 'a.c.d')
            ddict.getByDotKey('a.c.d')
            ddict.getByDotKey_alt('a.c.d')
        """

        self.update(**dict((k, self.parse(v)) for k, v in d.items()))

    @classmethod
    def parse(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return cls(v)
        elif isinstance(v, list):
            return [cls.parse(i) for i in v]
        else:
            return v

    @staticmethod
    def getByDotKey_obj(obj: dict, ref: str, d: Any = None) -> Any:
        """Betkoki dict like masyva pasiekia dot notation budu"""
        keys = ref.split('.')
        val = obj
        try:
            for key in keys:
                val = val[key]
            return val
        except Exception:
            return d

    @staticmethod
    def getByDotKey_obj_alt(obj: dict, ref: str, d: Any = None) -> Any:
        """Betkoki dict like masyva pasiekia dot notation budu"""
        keys = ref.split('.')
        try:
            return reduce(operator.getitem, keys, obj)
        except Exception:
            return d

    def getByDotKey(self, ref: str, d: Any = None) -> Any:
        """Is dot notatio rakto grazina reiksme"""
        return self.getByDotKey_obj(obj=self, ref=ref, d=d)

    def getByDotKey_alt(self, ref: str) -> Any:
        """getByDotKey alternative

        Geriau nenaudoti, cia tik ziniu prasmei laikta
        """
        return eval(ref, locals()['self'])

    @classmethod
    def uppend_obj(cls, obj: dict, ref: str, val: Any) -> None:
        """Pagal ref nutiesia kele objekte ir iraso val reikme

        Note: keicia objekta
        """
        tmpObj = obj
        keys = ref.split('.')
        for key in keys[:-1]:
            tmpObj[key] = tmpObj.get(key, {})
            tmpObj = tmpObj[key]
        tmpObj[keys[-1]] = val

    def uppend(self, ref: str, val: Any) -> None:
        """Pagal ref nutiesia kele objekte ir iraso val reikme

        Note: keicia objekta
        """
        self.uppend_obj(obj=self, ref=ref, val=val)

    @staticmethod
    def delByDotKey_obj(obj: dict, ref: str) -> None:
        """Pagal raktus pabando istrinti atributus

        Note: modeifikuoja obj
        """
        keys = ref.split('.')
        val = obj
        try:
            for key in keys[:-1]:
                val = val[key]
            del val[keys[-1]]
        except Exception:
            pass

    @classmethod
    def delByDotKeys_obj(cls, obj: dict, remIds: list[str]) -> None:
        """Pagal raktus pabando istrinti atributus

        Note:modeifikuoja obj
        """
        for ref in remIds:
            cls.delByDotKey_obj(obj, ref)

    def delByDotKey(self, ref: str) -> None:
        """Istrina pagal ref

        Note: modifikuoja objektua
        """
        self.delByDotKey_obj(obj=self, ref=ref)

    def delByDotKeys(self, remIds: list[str]) -> None:
        """Istrina pagal ref

        Note: modifikuoja objektua
        """
        self.delByDotKeys_obj(obj=self, remIds=remIds)

        ###########################################################################

    @classmethod
    def subset_obj(cls, d: dict, ids: list[str]) -> dict:
        return {k: cls.getByDotKey_obj(d, k) for k in ids}

    def subset(self, ids: list[str]) -> dict:
        return self.subset_obj(self, ids=ids)

    @classmethod
    def subsetPath_obj(cls, d: dict, ids: list[str]) -> dict:
        vals = cls.subset_obj(d, ids=ids)
        res: dict = {}
        for ref, val in vals.items():
            cls.uppend_obj(res, ref=ref, val=val)
        return res

    def subsetPath(self, ids: list[str]) -> dict:
        return self.subsetPath_obj(d=self, ids=ids)

    @classmethod
    def subsetDiff_obj(cls, d: dict, remIds: list[str]) -> dict:
        obj = copy.deepcopy(d)
        cls.delByDotKeys_obj(obj=obj, remIds=remIds)
        return obj
