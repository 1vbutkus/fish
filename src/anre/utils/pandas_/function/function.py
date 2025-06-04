# mypy: disable-error-code="assignment,call-arg,operator,union-attr,var-annotated"
from typing import cast

import numpy as np
import pandas as pd

from anre.utils.time import functions as tf
from anre.utils.time.convert import Convert as TimeConvert


def change_ind(sr: pd.Series) -> pd.Series:
    return ~sr.eq(sr.shift(1))


def change_count(sr: pd.Series) -> pd.Series:
    return (~sr.eq(sr.shift(1))).cumsum()


def seq_from_change(sr: pd.Series) -> pd.Series:
    _change_ind = ~sr.eq(sr.shift(1))
    seq_sr = pd.Series(range(sr.shape[0]), index=sr.index)
    return seq_sr - seq_sr.loc[_change_ind].reindex(seq_sr.index, fill_value=0).cummax()


def add_epsilon_to_make_time_unique(ts_sr: pd.Series, eps_ns: int = 1) -> pd.Series:
    assert isinstance(ts_sr, pd.Series)
    assert ts_sr.is_monotonic_increasing
    assert ts_sr.index.is_unique
    ind_sr = ts_sr.eq(ts_sr.shift(1).values)  # type: ignore[arg-type]
    offset_sr = ind_sr * 0
    offset_sr.loc[ind_sr] = seq_from_change(ind_sr).loc[ind_sr] + eps_ns
    new_ts_sr = TimeConvert.number2dt(TimeConvert.dt2number(ts_sr) + offset_sr)
    assert new_ts_sr.is_unique, (
        'Results are not unique. Probably updated values collided to updates.'
    )
    return cast(pd.Series, new_ts_sr)


def keep_first_in_freq(ts_sr: pd.Series, freq: str = '1ms') -> pd.Series:
    assert isinstance(ts_sr, pd.Series)
    assert pd.api.types.is_datetime64_any_dtype(ts_sr.dtype)
    assert ts_sr.is_monotonic_increasing
    floor_ts_sr = ts_sr.dt.floor(freq)
    ind = ~floor_ts_sr.eq(floor_ts_sr.shift(1).values)  # type: ignore[arg-type]
    ### alternative
    # idx = floor_ts_sr.drop_duplicates(keep='first').index
    # ts_sr.loc[idx].copy()
    return ts_sr.loc[ind.values].copy()  # type: ignore[index]


def seq_in_group(sr: pd.Series) -> pd.Series:
    return sr.groupby(sr).transform(lambda sr: range(len(sr)))


def get_const_strike_mark_sr(is_const_sr: pd.Series, window: int) -> pd.Series:
    is_const_strike_sk = is_const_sr.rolling(window=window, center=False).min().fillna(0)
    const_strike_mark_sr = (
        is_const_strike_sk.iloc[::-1]
        .rolling(window=window, center=False, min_periods=0)
        .max()
        .iloc[::-1]
        > 0
    )
    return const_strike_mark_sr


def get_xgrid(
    sr_or_idx: pd.Series | pd.Index, precision: float | int = 1, include_floor: bool = False
) -> np.ndarray:
    """
    Generate a uniform grid of numeric or datetime values based on the input series or index.

    This function creates evenly spaced values (grid) between the minimum and maximum of the input
    Series or Index, adjusted according to the specified precision. It supports both numerical
    and datetime data types. If the `include_floor` option is set to True, the computation
    starts from the floor of the minimum; otherwise, from the ceiling.

    Parameters:
        sr_or_idx (pd.Series | pd.Index): Input data Series or Index. It should be of numeric or
            datetime type to generate the grid.
        precision (float | int, optional): Step size for the generated grid. Default is 1 for
            numeric inputs.
        include_floor (bool, optional): Indicates if the grid should include the floor of the
            minimum value. Defaults to False.

    Returns:
        np.ndarray: A 1-dimensional array containing the evenly spaced grid values.

    Raises:
        NotImplementedError: If the input Series or Index is neither numeric nor datetime.
    """
    if not isinstance(sr_or_idx, (pd.Series, pd.Index)):
        raise TypeError("Input must be a pandas Series or Index")

    assert precision > 0

    if pd.api.types.is_numeric_dtype(sr_or_idx.dtype):
        if include_floor:
            _min = np.floor(sr_or_idx.min() / precision) * precision
        else:
            _min = np.ceil(sr_or_idx.min() / precision) * precision
        _max = np.ceil(sr_or_idx.max() / precision) * precision
        xgrid = np.arange(_min, _max + precision / 2, precision)

    elif pd.api.types.is_datetime64_any_dtype(sr_or_idx.dtype):
        if include_floor:
            _min = tf.floor_dt(sr_or_idx.min(), precision=precision)
        else:
            _min = tf.ceil_dt(sr_or_idx.min(), precision=precision)
        _max = tf.ceil_dt(sr_or_idx.max(), precision=precision)
        xgrid = tf.get_time_range(_min, _max, precision=precision)

    else:
        raise NotImplementedError("The input Series or Index must be of numeric or datetime type")

    return xgrid


def compress_sr(sr: pd.Series) -> pd.Series:
    assert sr.index.is_monotonic_increasing, 'index must be sorted to apply compression.'
    if not sr.index.is_unique:
        sr = sr.loc[~sr.index.duplicated(keep='last')]
    ind = ~sr.eq(sr.shift(1).values)  # type: ignore[arg-type]
    if len(ind):
        ind.iloc[-1] = True  # the last element we still include
    sr = sr.loc[ind.values].copy()  # type: ignore[index]
    return sr


def map_side_to_int(sr: pd.Series) -> pd.Series:
    side_to_value = {'buy': 1, 'sell': -1}
    return sr.map(lambda side: side_to_value[side.lower()])


def calculate_position_from_quantities_and_side(
    quantity_sr: pd.Series, side_sr: pd.Series
) -> pd.Series:
    position_change_df = quantity_sr * map_side_to_int(side_sr)
    return position_change_df.cumsum()


def calculate_profit_from_trades(
    df: pd.DataFrame, initial_base_position: float, fee_asset_price: float
) -> pd.DataFrame:
    df = df.copy()
    df['basePosition'] = (
        calculate_position_from_quantities_and_side(df['baseQuantity'], df['side'])
        + initial_base_position
    )
    df['quotePosition'] = (
        calculate_position_from_quantities_and_side(df['quoteQuantity'], df['side']) * -1
    )
    df['tradeProfit'] = 0.0
    df['cumulativeProfit'] = 0.0
    if len(df) == 0:
        return df

    initial_value = (
        df['basePosition'].values[0] * df['price'].values[0] + df['quotePosition'].values[0]
    )
    df['cumulativeProfit'] = (
        -df['fee'] * fee_asset_price
        + df['basePosition'] * df['price']
        + df['quotePosition']
        - initial_value
    )

    df['tradeProfit'] = df['cumulativeProfit'].diff().fillna(0)

    return df


def __demo__():
    sr = pd.Series([
        1,
        1,
        2,
        2,
        2,
        3,
        3,
        3,
        1,
    ])
    change_count(sr)
    seq_from_change(sr.sort_values())
    seq_in_group(sr.sort_values())
