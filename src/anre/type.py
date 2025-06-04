from typing import Any, Literal, Union, get_args, get_origin

import numpy as np
import pandas as pd


class Type:
    RealNumber = int | float
    BasicType = float | int | str | bool
    X = pd.DataFrame | np.ndarray
    y = pd.Series | np.ndarray
    Xy = pd.DataFrame | pd.Series | np.ndarray

    @classmethod
    def isinstance(cls, obj: Any, __type_or_tuple) -> bool:
        if isinstance(__type_or_tuple, tuple):
            return any([cls._isinstance_single(obj, __type) for __type in __type_or_tuple])
        else:
            return cls._isinstance_single(obj, __type_or_tuple)

    @classmethod
    def _isinstance_single(cls, obj: Any, type_) -> bool:
        origin = get_origin(type_)
        if origin is None:
            return isinstance(obj, type_)
        elif origin == Union:
            return isinstance(obj, type_)
        elif origin == Literal:
            if not isinstance(obj, cls.BasicType):
                return False
            return obj in get_args(type_)
        elif origin is tuple:
            args = get_args(type_)
            if not isinstance(obj, tuple):
                return False
            if len(args) != len(obj):
                return False
            return all([
                cls._isinstance_single(subObj, subArg) for subObj, subArg in zip(obj, args)
            ])
        else:
            raise NotImplementedError
