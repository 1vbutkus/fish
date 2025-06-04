# mypy: disable-error-code="union-attr"
import datetime
from typing import Any, Mapping

import numpy as np
import pandas as pd

from anre.utils.fun.lastValueStepFunction import LastValueStepFunction
from anre.utils.functions import convert_x2npArray, convert_y2expectedObj

# Mapping is not covariant with regards to key
ConcatFunctionMap = (
    Mapping[int, LastValueStepFunction]
    | Mapping[float, LastValueStepFunction]
    | Mapping[datetime.datetime, LastValueStepFunction]
)


class _Full:
    def __init__(self, fill_value, dtype) -> None:
        self._fill_value = fill_value
        self._dtype = dtype

    def __call__(self, x, **kwargs: Any) -> np.ndarray:
        return np.full(len(x), self._fill_value, dtype=self._dtype)


class ConcatFunction:
    @classmethod
    def new_from_lastValueStepFunctions(cls, fun_map: ConcatFunctionMap):
        assert fun_map
        assert all([isinstance(fun, LastValueStepFunction) for fun in fun_map.values()])
        assert len(pd.Series([fun.nan for fun in fun_map.values()]).unique()) == 1
        assert len(set([fun.dtypeY for fun in fun_map.values()])) == 1
        assert len(pd.Series([fun.fill_value for fun in fun_map.values()]).unique()) == 1

        fun: LastValueStepFunction = list(fun_map.values())[0]
        fill_value = fun.nan
        dtype = fun.dtypeY
        return cls(fun_map=fun_map, fill_value=fill_value, dtype=dtype)

    def __init__(
        self,
        fun_map: ConcatFunctionMap,
        fill_value=np.nan,
        dtype=float,
    ):
        mapTrs = convert_x2npArray(list(fun_map.keys()))
        partBins = np.sort(mapTrs)
        partFunMap = {
            di: fn
            for di, fn in zip(np.searchsorted(partBins, mapTrs, side='right'), fun_map.values())
        }
        assert 0 not in partFunMap
        assert 1 in partFunMap
        partFunMap[0] = _Full(fill_value=fill_value, dtype=dtype)  # type: ignore[assignment]

        self._partFunMap = partFunMap
        self._partBins = partBins

    def __call__(self, x, **kwargs: Any):
        return self._get_funValue_atX(x=x, **kwargs)

    def _get_funValue_atX(self, x, **kwargs: Any):
        if pd.api.types.is_scalar(x):
            isScalar = True
            x = pd.Series([x])

        else:
            isScalar = False

        xAr = convert_x2npArray(x)
        xFix = convert_y2expectedObj(y=xAr, x=x)
        assert isinstance(xFix, np.ndarray | pd.Series)
        isSeries = isinstance(xFix, pd.Series)
        partAr = np.searchsorted(self._partBins, xAr, side='right')
        partUnAr = np.unique(partAr)

        yNew = self._partFunMap[0](xFix)  # This one if fill values
        for part in partUnAr:
            ind = partAr == part
            _xSubset = xFix.loc[ind] if isSeries else xFix[ind]
            _localOutputAr = self._partFunMap[part](_xSubset, **kwargs)
            assert _localOutputAr.shape[0] == np.sum(ind)
            yNew[ind] = _localOutputAr

        yNew = convert_y2expectedObj(y=yNew, x=x)

        if isScalar:
            return yNew[0]

        return yNew
