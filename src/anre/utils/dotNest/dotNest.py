# mypy: disable-error-code="assignment,var-annotated"
import re
from collections.abc import Mapping
from typing import Any, Callable, Iterable, Sequence, Set

import pandas as pd

# Galima ikveimo pasistemti:
# https://github.com/pawelzny/dotty_dict
# https://github.com/mbello/dict-deep/


class ErrorIfFailed:
    pass


class _Empty:
    pass


empty = _Empty()


# python __setitem__
# python __getitem__


class DotNest:
    """Deals with nested object (usually dict, but not only with them - it can be general objects)

    Supported keys:
     - ('a', 'b', 'c', 1, 'd', '1') - this is internal standart
     - 'a.b.c[1].d'  - 1 is int
     - 'a.b.c.1.d'   - '1' is str

    Supporting nested containers:
        Mapping
        list
    Note: any other will be counted as value, but we can access to any objects (that depends on getter), i.e. elements form np.array or tuple can be extracted

    Access functions (with default/error control):
        get, set, del, pop

    Transformation function
        nestToDot
        dotToNest

    Extras: ...

    Kad viskas puikiai veiktu nest turi buti dict, kurio key keliami reikalvimai:
        tipas turi buti str
        jame neturi buti sep simbolio

    Note: kaikurios funkcijos gali veikti ir be apribojimu.
    """

    _listElemPattern = re.compile(r'(.*)\[(\d+)\]$')

    def __init__(self, dataNest: dict | list, sep: str = '.', listToMap: bool = True) -> None:
        assert isinstance(sep, str)
        assert len(sep) == 1

        # this will fix, if any mixed case where given. And raise is this is not convertable.
        nest = self.convert_dotDict2nest(dataNest, sep=sep)
        nestDotDict = self.convert_nest2dotDict(nest, sep=sep, listToMap=listToMap)
        _nestAlt = self.convert_dotDict2nest(nestDotDict, sep=sep)
        assert dataNest == _nestAlt, 'Round trip is not getting the same results'
        del _nestAlt

        self.dataNest: dict | list = dataNest
        self._sep = sep
        self._sep = sep
        self._listToMap = listToMap

    def __getitem__(self, key: str) -> Any:
        return self.get(key=key)

    def get(self, key: str, default=ErrorIfFailed()) -> Any:
        assert type(key) is str, f'Parameters getter not implement for type {type(key)}'
        return self.nestGet(nest=self.dataNest, key=key, default=default, sep=self._sep)

    @property
    def dotDict(self) -> dict:
        return self.convert_nest2dotDict(
            nest=self.dataNest, sep=self._sep, listToMap=self._listToMap
        )

    @classmethod
    def nestGet(
        cls,
        nest,
        key: str | list[str | int],
        default: Any = ErrorIfFailed(),
        sep: str = '.',
        getter: Callable | None = None,
    ):
        getter = cls._getter_default if getter is None else getter
        keys: list[str | int] = cls._getSplit_keys(key=key, sep=sep)

        obj = nest
        try:
            for k in keys:
                obj = getter(obj, k)
            return obj
        except (KeyError, IndexError):
            if isinstance(default, ErrorIfFailed):
                raise
            else:
                return default

    @classmethod
    def nestSet(
        cls,
        nest,
        key: str | list[str | int],
        value: Any,
        sep: str = '.',
        getter: Callable | None = None,
        setter: Callable | None = None,
        extendIfMissing: bool = False,
    ):
        """Pagal ref nutiesia kele objekte ir iraso val reikme

        Note: keicia objekta
        """
        getter = cls._getter_default if getter is None else getter
        setter = cls._setter_default if setter is None else setter
        keys: list[str | int] = cls._getSplit_keys(key=key, sep=sep)

        currObj = nest
        for k in keys[:-1]:
            try:
                deeperObj = getter(currObj, k)
            except (KeyError, IndexError):
                if extendIfMissing:
                    deeperObj = {}
                    setter(currObj, key=k, value=deeperObj)
                else:
                    raise
            currObj = deeperObj

        lastKey = keys[-1]
        setter(currObj, key=lastKey, value=value)

    @classmethod
    def nestDel(
        cls,
        nest,
        key: str | list[str | int],
        raiseIfMissing=True,
        sep: str = '.',
        getter: Callable | None = None,
    ):
        """Pagal raktus pabando istrinti atributus

        Note: Gali buti, kad pasiektas objektas yra ne mutable, tokiu ateju bus erroras
        """
        getter = cls._getter_default if getter is None else getter
        keys = cls._getSplit_keys(key=key, sep=sep)

        obj = nest
        try:
            for k in keys[:-1]:
                obj = getter(obj, k)
            del obj[keys[-1]]
        except (KeyError, IndexError):
            if raiseIfMissing:
                raise

    @classmethod
    def nestPop(
        cls,
        nest,
        key: str | list[str | int],
        default: Any = ErrorIfFailed(),
        sep: str = '.',
        getter: Callable | None = None,
    ):
        """Pagal raktus pabando istrinti atributus

        Note: Gali buti, kad pasiektas objektas yra ne mutable, tokiu ateju bus erroras
        """
        getter = cls._getter_default if getter is None else getter
        keys = cls._getSplit_keys(key=key, sep=sep)

        obj = nest
        try:
            for k in keys[:-1]:
                obj = getter(obj, k)
            return obj.pop(keys[-1])
        except (KeyError, IndexError):
            if isinstance(default, ErrorIfFailed):
                raise
            else:
                return default

    @classmethod
    def get_mapRawKeys(cls, nest) -> Set:
        """Collect all keys of mapping"""

        keySet = set()

        def walk(d):
            if isinstance(d, Mapping):
                for k, v in d.items():
                    keySet.add(k)
                    walk(v)
            elif isinstance(d, list):
                for k, v in enumerate(d):
                    walk(v)

        walk(nest)
        return keySet

    @classmethod
    def get_countValues(cls, nest) -> int:
        """Value is any object but container (i.e. Maping, list)"""
        count = 0
        if isinstance(nest, Mapping):
            for k, v in nest.items():
                count += cls.get_countValues(v)
        elif isinstance(nest, list):
            for v in nest:
                count += cls.get_countValues(v)
        else:
            count += 1

        return count

    @classmethod
    def collect_values_fromNests(
        cls,
        dotKey: str,
        nestDicts: Iterable[Mapping],
        sep='.',
        default: Any = ErrorIfFailed(),
        getter: Callable | None = None,
    ) -> list[Any]:
        dotKey = cls._getSplit_keys(key=dotKey, sep=sep)
        getter = cls._getter_fast if getter is None else getter
        return [
            cls.nestGet(nest=nest, key=dotKey, getter=getter, default=default) for nest in nestDicts
        ]

    @classmethod
    def collect_valueDict(
        cls,
        nest,
        take_rename_dict: dict,
        sep='.',
        default: Any = ErrorIfFailed(),
        getter: Callable | None = None,
    ) -> dict:
        valueDict = {}
        for dotPath, label in take_rename_dict.items():
            obj = cls.nestGet(nest, key=dotPath, sep=sep, default=default, getter=getter)
            valueDict[label] = obj
        return valueDict

    @classmethod
    def convert_dotDict2nest(
        cls, mixedNest: Mapping[str, Any] | list, sep: str = '.', listToMap=True
    ) -> dict | list:
        """

        Note: this function can called on nest dict as well or mixtDict - to transform it to nest dict
        """

        def _convertMapIntToList(nestDict):
            # transform map: int -> Any into list[Any]
            assert isinstance(nestDict, dict)
            for k, v in nestDict.items():
                if isinstance(v, dict):
                    nestDict[k] = _convertMapIntToList(v)

            if bool(nestDict) and all([isinstance(key, int) for key in nestDict.keys()]):
                keys = list(nestDict.keys())
                keys.sort()
                assert keys == list(range(len(keys)))
                return [nestDict[k] for k in keys]

            return nestDict

        _nestDict = {}
        if isinstance(mixedNest, list):
            assert listToMap
            for key, value in enumerate(mixedNest):
                if isinstance(value, (Mapping, list)):
                    value = cls.convert_dotDict2nest(value, sep=sep, listToMap=listToMap)
                cls.nestSet(nest=_nestDict, key=[key], value=value, sep=sep, extendIfMissing=True)
        elif isinstance(mixedNest, Mapping):
            for key, value in mixedNest.items():
                if isinstance(value, Mapping):
                    value = cls.convert_dotDict2nest(value, sep=sep, listToMap=listToMap)
                elif isinstance(value, (Mapping, list)) and listToMap:
                    value = cls.convert_dotDict2nest(value, sep=sep, listToMap=listToMap)
                cls.nestSet(nest=_nestDict, key=key, value=value, sep=sep, extendIfMissing=True)  # type: ignore[arg-type]
        else:
            raise NotImplementedError(
                f'mixedNest must be Mapping or list, but got {type(mixedNest)}: {mixedNest=}'
            )

        nest = _convertMapIntToList(_nestDict)

        # there is possibility to shadow some values:
        assert cls.get_countValues(mixedNest) == cls.get_countValues(nest), (
            'Some values are shadowed by others.'
        )
        assert all([isinstance(key, str) for key in cls.get_mapRawKeys(nest)]), (
            'Some keys are not str, something wrong'
        )

        return nest

    @classmethod
    def convert_nest2dotDict(
        cls, nest: Mapping | list, sep='.', listToMap=True, _frontSep=None
    ) -> dict:
        """

        Note: this function can not be called on dotDict since seperator will creat probelms
        """

        _frontSep = '' if _frontSep is None else _frontSep
        resDict = {}
        if isinstance(nest, Mapping):
            for k, v in nest.items():
                assert isinstance(k, str), (
                    f'All keys must be strings. Got key={k}({type(k)}), val={v}'
                )
                assert sep not in k, f'sep(`{sep}`) are not allowed in keys. Bad key: {k}'
                if (isinstance(v, Mapping) or (isinstance(v, list) and listToMap)) and v:
                    for sk, sv in cls.convert_nest2dotDict(
                        v, sep=sep, listToMap=listToMap, _frontSep=sep
                    ).items():
                        resDict[f'{_frontSep}{k}{sk}'] = sv
                else:
                    resDict[f'{_frontSep}{k}'] = v

        elif isinstance(nest, list):
            assert listToMap
            for k, v in enumerate(nest):
                if isinstance(v, (Mapping, list)) and v:
                    for sk, sv in cls.convert_nest2dotDict(
                        v, sep=sep, listToMap=listToMap, _frontSep=sep
                    ).items():
                        resDict[f'[{k}]{sk}'] = sv
                else:
                    resDict[f'[{k}]'] = v

        return resDict

    @classmethod
    def compare(
        cls,
        aNest,
        bNest,
        ignoreList: list[str] | None = None,
        aName: str = 'base',
        bName: str = 'comp',
        convertToNestFirst: bool = False,
    ) -> pd.DataFrame:
        ignoreList = ignoreList if ignoreList else []
        if convertToNestFirst:
            aNest = cls.convert_dotDict2nest(aNest)
            bNest = cls.convert_dotDict2nest(bNest)
        aSr = (
            pd.Series(cls.convert_nest2dotDict(aNest))
            .drop(labels=ignoreList, errors='ignore')
            .sort_index()
        )
        bSr = (
            pd.Series(cls.convert_nest2dotDict(bNest))
            .drop(labels=ignoreList, errors='ignore')
            .sort_index()
        )
        eqSr = aSr.eq(bSr) | ((~aSr.eq(aSr)) & (~bSr.eq(bSr)))
        diffSr = eqSr[~eqSr]
        resDf = pd.DataFrame(
            list(zip(diffSr.index, aSr.reindex(diffSr.index), bSr.reindex(diffSr.index))),
            columns=['key', aName, bName],
        )
        resDf.set_index('key', inplace=True)
        return resDf

    @classmethod
    def update_nest(
        cls,
        nest: Mapping | list,
        updateMap: Mapping,
        sep: str = '.',
        getter: Callable | None = None,
        setter: Callable | None = None,
        extendIfMissing: bool = False,
    ):
        """Updatina nest

        Tipinis panaudojimas, kai updateMap key yra dotDict ir atnaujina reikme kaip reikia.
        Jei updateMap yra nest, tai bus atnaujinamas aukciausia lygyje - ir giliau nesileis - updateIdct vaikas bus uzrasytas kaip visa medzio saka.
        Jei reikia atnaujinti tik tas reikmes kuriu reikia, tai konvertuokite i dotDict'a
        """

        assert isinstance(updateMap, Mapping)
        for key, value in updateMap.items():
            cls.nestSet(
                nest=nest,
                key=key,
                value=value,
                sep=sep,
                getter=getter,
                setter=setter,
                extendIfMissing=extendIfMissing,
            )

    @staticmethod
    def _safeCompare(a, b) -> bool:
        if a is b:
            return True

        res = a == b
        if isinstance(res, Iterable):
            return all(res)
        else:
            return res

    @classmethod
    def _getSplit_keys(cls, key: str | list | tuple, sep='.') -> Sequence[str | int]:
        """Returns a collection of keys

        Key can be only str or int
        """
        if isinstance(key, str):
            keys = []
            _keysInit = key.split(sep=sep)
            for keyInit in _keysInit:
                _keys = cls._splitKeyByIndex(key=keyInit)
                keys.extend(_keys)
            return keys

        elif isinstance(key, list):
            return key

        else:
            raise ValueError(f'key must be str, list or tuple, but got {type(key)}: {key}')

    @classmethod
    def _splitKeyByIndex(cls, key: str) -> list[str | int]:
        keys: list[str | int] = []
        assert isinstance(key, str)
        if ('[' in key) and (']' in key):
            match = re.match(cls._listElemPattern, key)
            if match:
                assert match, 'If key contains brackets([]) we expect it is in form {parent}[{int}]'
                parent, keyInt = match.groups()
                if parent:
                    _keys = cls._splitKeyByIndex(key=parent)
                    keys.extend(_keys)
                keys.append(int(keyInt))
            else:
                keys.append(key)
        else:
            keys.append(key)

        return keys

    @staticmethod
    def _getter_default(obj: Any, key: str | int) -> Any:
        assert isinstance(key, str | int)
        if hasattr(obj, '__getitem__'):
            return obj[key]
        elif isinstance(key, str) and hasattr(obj, key):
            return getattr(obj, key)
        else:
            raise KeyError(f'key(`{key}`) not found in {obj}.')

    @staticmethod
    def _getter_fast(obj: Any, key: str | int) -> Any:
        return obj[key]

    @staticmethod
    def _setter_default(obj: Any, key: str | int, value: Any) -> Any:
        if isinstance(obj, list):
            assert isinstance(key, int), 'If obj is list, key must be int'
            _len = len(obj)
            if -_len <= key < _len:
                obj[key] = value
            elif key == _len:
                obj.append(value)
            else:
                raise IndexError

        elif hasattr(obj, '__setitem__'):
            obj[key] = value

        else:
            raise AssertionError('The element is not supporting __setitem__')
