"""Duomenu strukturos bazino objektas

Duomenustruktura moka sekti savoatributus, jie visiem matotomi, tikrinti tipus, neleisti keisti ir t.t.

Mes Cia pasirupiname grazu printu ir to_dict funkcija

Example of typical usage

from anre.utils.dataclass_type_validator import dataclass_validate
from dataclasses import dataclass
from anre.utils.dataStructure.general import GeneralBaseFrozen

@dataclass_validate
@dataclass(frozen=True, repr=False)
Foo(GeneralBaseFrozen):
    a = 1
    b = 2
"""

import copy
from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np
import pandas as pd
from dacite import Config, from_dict

from anre.utils.dotNest.dotNest import DotNest
from anre.utils.functions import checksum

_config = Config(strict=True)


class _GeneralBase:
    def __init__(self, **kwargs: Any) -> None:
        pass

    def __repr__(self) -> str:
        fieldStrList = []
        for fieldName, value in self.__dict__.items():
            if not fieldName.startswith('_'):
                if isinstance(value, pd.DataFrame):
                    _strRep = f'shape={value.shape}, columns={list(value.columns)}'
                    fieldStr = f'{value.__class__.__name__}({_strRep})'
                elif isinstance(value, pd.Series):
                    _strRep = f'shape={value.shape}'
                    fieldStr = f'{value.__class__.__name__}({_strRep})'
                elif isinstance(value, np.ndarray):
                    fieldStr = f'array({value})'
                elif hasattr(value, '__repl__'):
                    fieldStr = value.__repl__()
                else:
                    fieldStr = str(value)
                fieldStr = fieldStr.replace('\n', '\n    ')
                fieldRepl = f'    {fieldName} = {fieldStr},'
                fieldStrList.append(fieldRepl)
        fieldStrJoined = '\n'.join(fieldStrList)
        repr = f'{self.__class__.__name__}(\n{fieldStrJoined}\n)'
        return repr

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def new_fromNestDict(cls, nestDict: dict[str, Any]) -> '_GeneralBase':
        return from_dict(data_class=cls, data=nestDict, config=_config)

    @classmethod
    def from_dict(cls, dict_: dict) -> '_GeneralBase':
        return cls(**dict_)

    def get_hash(self) -> str:
        return checksum(self.to_dict())

    def new_update(self, updateDict: dict[str, Any] | None = None, **kwargs):
        if updateDict is None:
            updateDict = {}
        else:
            isinstance(updateDict, dict), 'updateDict is not dict'
            updateDict = copy.deepcopy(updateDict)

        assert not (dupKeys := set(updateDict) & set(kwargs)), (
            f'Duplicate entries from updateDict and kwargs. This could lead to ugly bug, please avoid doing this: {dupKeys}'
        )
        updateDict.update(kwargs)

        nestDict = self.to_dict()
        DotNest.update_nest(nest=nestDict, updateMap=updateDict)
        newConfig = self.new_fromNestDict(nestDict=nestDict)
        assert isinstance(newConfig, self.__class__)
        return newConfig


@dataclass(frozen=False, repr=False)
class GeneralBaseMutable(_GeneralBase):
    def __eq__(self, other: Any) -> bool:
        return self.get_hash() == other.get_hash()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def set(self, **kwargs: Any):
        return replace(self, **kwargs)


@dataclass(frozen=True, repr=False)
class GeneralBaseFrozen(_GeneralBase):
    def __eq__(self, other: Any) -> bool:
        return self.get_hash() == other.get_hash()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def set(self, **kwargs: Any):
        return replace(self, **kwargs)
