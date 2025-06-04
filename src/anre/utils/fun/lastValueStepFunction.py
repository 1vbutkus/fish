# mypy: disable-error-code="call-overload"
import datetime
import warnings
from typing import Literal, Sized

import numpy as np
import pandas as pd

from anre.utils.functions import convert_x2npArray, convert_y2expectedObj
from anre.utils.pandas_.function.function import compress_sr
from anre.utils.time import functions as tf


class LastValueStepFunction:
    @classmethod
    def new_from_sr(
        cls,
        sr: pd.Series,
        keep: Literal["first", "last"] | None = None,
        fill_value=None,
        default_update_asap: bool = True,
        compress: bool = True,
    ):
        warnings.warn('LastValueStepFunction.new_from_sr is deprecated', DeprecationWarning)
        assert isinstance(sr, pd.Series)
        return cls.new_with_data_processing(
            x=sr.index,
            y=sr.values,
            fill_value=fill_value,
            default_update_asap=default_update_asap,
            keep=keep,
            compress=compress,
        )

    @classmethod
    def new_with_data_processing(
        cls,
        x: Sized | pd.Series,
        y: Sized | None = None,
        *,
        fill_value=None,
        default_update_asap: bool = True,
        x_validation: bool = True,
        keep: Literal["first", "last"] | None = None,
        compress: bool = True,
    ):
        if y is None:
            assert isinstance(x, pd.Series), 'If y is not given, x must be pd.Series'
            y = x.values
            x = x.index

        assert len(x) == len(y), 'The length of x and y is not matching.'
        # fix input to proper format
        tx: np.ndarray = cls._prepare_x(x=x, validate=x_validation)
        ty: np.ndarray = cls._prepare_y(y=y)
        del x, y

        sr = pd.Series(ty, index=pd.Index(tx, dtype=tx.dtype), dtype=ty.dtype)
        sr = cls.prepare_construction_input(sr=sr, compress=compress, keep=keep)

        return cls.new(
            x=sr.index,
            y=sr.values,
            fill_value=fill_value,
            default_update_asap=default_update_asap,
            x_validation=x_validation,
        )

    @classmethod
    def new(
        cls,
        x: Sized | pd.Series,
        y: Sized | None = None,
        *,
        fill_value=None,
        default_update_asap: bool = True,
        x_validation: bool = True,
    ) -> 'LastValueStepFunction':
        if y is None:
            assert isinstance(x, pd.Series), 'If y is not given, x must be pd.Series'
            y = x.values
            x = x.index

        assert len(x) == len(y), 'The length of x and y is not matching.'

        # fix input to proper format
        tx: np.ndarray = cls._prepare_x(x=x, validate=x_validation)
        ty: np.ndarray = cls._prepare_y(y=y)
        del x, y

        ### fix dtype and make it compatible with fill_value
        if pd.api.types.is_numeric_dtype(tx.dtype):
            # we convert to float because after construction, users can give any numeric values,
            # in search algorithm 2==2.5 if input is integer
            x_dtype = np.dtype('float64')
            if tx.dtype is not x_dtype:
                tx = tx.astype(x_dtype)

        # find good fillValue
        fill_value = (
            cls._get_nan_value_from_dtype(dtype=ty.dtype) if fill_value is None else fill_value
        )
        # check if dtypeY should be corrected
        if pd.api.types.is_numeric_dtype(ty.dtype) and not pd.api.types.is_integer(fill_value):
            # if it is number, but not integer, we force to be float64 (no other options)
            y_dtype = np.dtype('float64')
            if ty.dtype is not y_dtype:
                ty = ty.astype(y_dtype)

        return cls(
            x=tx,
            y=ty,
            fill_value=fill_value,
            default_update_asap=default_update_asap,
            default_validate_x=True,
        )

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        fill_value,
        default_update_asap: bool = True,
        default_validate_x: bool = True,
    ):
        assert isinstance(x, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert isinstance(default_update_asap, bool)
        assert isinstance(default_validate_x, bool)
        assert x.ndim == 1, 'x must be 1D array.'
        assert x.shape == y.shape, 'The length of x and y is not matching.'

        # x must be sorted and unique. If it is not the case, we can try to transform it
        # it turns out pd is the fastest way to do so.
        sr = pd.Series(y, index=pd.Index(x, dtype=x.dtype), dtype=y.dtype)
        assert sr.index.is_monotonic_increasing, 'x values are not sorted'
        assert sr.index.is_unique, (
            'x values are not unique. This creates ambiguity. Please use .prepare_construction_input'
        )
        # check fill_value compatability
        if pd.api.types.is_numeric_dtype(y.dtype):
            assert pd.api.types.is_number(fill_value)
            if pd.api.types.is_integer(y.dtype):
                assert pd.api.types.is_integer(fill_value)
        if pd.api.types.is_datetime64_any_dtype(y.dtype):
            assert pd.api.types.is_datetime64_any_dtype(fill_value) or isinstance(
                fill_value, datetime.datetime
            ), f'Fill value has bad type. Expecting to get datetime, but got `{type(fill_value)}`'

        self._x: np.ndarray = x
        self._y: np.ndarray = y
        self._fill_value = fill_value
        self._default_update_asap: bool = default_update_asap
        self._default_validate_x: bool = default_validate_x

    def __call__(self, x, update_asap: bool | None = None, validate_x: bool | None = None):
        update_asap = self._default_update_asap if update_asap is None else update_asap
        validate_x = self._default_validate_x if validate_x is None else validate_x
        return self._get_funValue_atX(x=x, update_asap=update_asap, validate_x=validate_x)

    @property
    def nan(self):
        return self._get_nan_value_from_dtype(dtype=self._y.dtype)

    @property
    def dtypeY(self):
        return self._y.dtype

    @property
    def dtypeX(self):
        return self._x.dtype

    @property
    def fill_value(self):
        return self._fill_value

    @classmethod
    def prepare_construction_input(
        cls, sr: pd.Series, compress: bool, keep: Literal["first", "last"] | None = None
    ) -> pd.Series:
        assert keep is None or keep in ["first", "last"], (
            f'keep must be `first` or `last`, but got: {keep}'
        )
        assert sr.index.is_monotonic_increasing, 'x values are not sorted'

        # x duplicated
        if not sr.index.is_unique:
            if keep:
                ind = sr.index.duplicated(keep=keep)
                sr = sr.loc[~ind]
                del ind

            else:
                nunique_sr = sr.groupby(sr.index).nunique(dropna=False)
                if nunique_sr.max() == 1:
                    ind = sr.index.duplicated(keep='last')
                    sr = sr.loc[~ind]
                    del ind

                else:
                    raise RuntimeError(
                        'x axis has duplicate and ambiguous y values, but no keep was given.'
                    )
            if compress:
                sr = compress_sr(sr)

        return sr

    def _get_funValue_atX(self, x, update_asap: bool, validate_x: bool):
        if pd.api.types.is_scalar(x):
            isScalar = True
            txNew = self._prepare_x(x=np.array([x], dtype=self._x.dtype), validate=validate_x)
        else:
            isScalar = False
            txNew = self._prepare_x(x=x, validate=validate_x)

        if len(self._x) == 0:
            fillValue = self.nan if self._fill_value is None else self._fill_value
            size = len(txNew)
            yNew = np.full(size, fillValue)

        else:
            side = 'right' if update_asap else 'left'
            xis = np.searchsorted(self._x, txNew, side=side) - 1
            is_outside = xis < 0
            xis = np.maximum(0, xis)
            yNew = self._y.take(xis)
            if np.any(is_outside):
                yNew[is_outside] = self._fill_value

        if isScalar:
            return yNew[0]

        return convert_y2expectedObj(y=yNew, x=x)

    @classmethod
    def _prepare_x(cls, x, validate: bool) -> np.ndarray:
        tx = convert_x2npArray(x=x)
        if validate:
            assert not np.any(pd.isna(tx)), 'x values cant be nan'
        return tx

    @classmethod
    def _prepare_y(cls, y) -> np.ndarray:
        ty = convert_x2npArray(x=y)
        return ty

    @staticmethod
    def _get_nan_value_from_dtype(dtype):
        if pd.api.types.is_numeric_dtype(dtype):
            fillValueDefault = np.nan
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            fillValueDefault = np.datetime64("NaT")
        else:
            fillValueDefault = None
        return fillValueDefault

    @classmethod
    def get_grid_values(cls, sr: pd.Series, precision: float = 1.0) -> pd.Series:
        if pd.api.types.is_numeric_dtype(sr.index.dtype):
            _min = (np.floor(sr.index.min() / precision) + 1) * precision
            _max = np.ceil(sr.index.max() / precision) * precision
            grid_x = np.arange(_min, _max + precision / 2, precision)

        elif pd.api.types.is_datetime64_any_dtype(sr.index.dtype):
            _min = tf.floor_dt(sr.index.min(), precision=precision) + datetime.timedelta(
                seconds=precision
            )
            _max = tf.ceil_dt(sr.index.max(), precision=precision)
            grid_x = tf.get_time_range(_min, _max, precision=precision)

        else:
            raise NotImplementedError

        fun = cls.new_with_data_processing(sr, keep='last')
        yar = fun(grid_x)
        ysr = pd.Series(yar, index=grid_x, dtype=yar.dtype)
        return ysr

    @classmethod
    def reduce_resolution(cls, sr: pd.Series, precision: float = 1.0) -> pd.Series:
        ysr = cls.get_grid_values(
            sr=sr,
            precision=precision,
        )
        ind = ~ysr.eq(ysr.shift(1).values)  # type: ignore[arg-type]
        ind.iloc[-1] = True
        new_sr = ysr.loc[ind.values].copy()  # type: ignore[index]
        return new_sr

    def to_series(self) -> pd.Series:
        return pd.Series(self._y, index=pd.Index(self._x, dtype=self._x.dtype), dtype=self._y.dtype)


def _benchmark_lastValueStepFunction():
    import datetime
    import time

    from anre.utils.time.functions import get_time_range

    start = datetime.datetime(2000, 1, 1, 9, 0, 0)
    end = datetime.datetime(2020, 1, 1, 9, 0, 10)
    ts_sr = pd.Series(get_time_range(start, end, precision=0.5))
    print(len(ts_sr) / 1000_000)
    a_sr = 10 + pd.Series(np.random.rand(len(ts_sr)), index=ts_sr)
    b_sr = 10 + pd.Series(np.random.rand(len(ts_sr)), index=ts_sr + np.timedelta64(222, 'us'))

    def _align_and_divide(a_sr, b_sr):
        union_index = a_sr.index.union(b_sr.index, sort=True)
        a_fun = LastValueStepFunction.new(x=a_sr.index, y=a_sr.values, x_validation=False)
        b_fun = LastValueStepFunction.new(x=b_sr.index, y=b_sr.values, x_validation=False)
        ratio = a_fun(union_index).div(b_fun(union_index).values)
        return ratio

    start_time = time.time()
    ratio = _align_and_divide(a_sr=a_sr, b_sr=b_sr)
    finish_time = time.time()
    print(f'Time: {(finish_time - start_time) / 60} minutes')
    len(ratio) / 1e9
