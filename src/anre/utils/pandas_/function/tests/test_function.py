import datetime

import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.pandas_.function import function as pdf


class TestGetXGrid(testutil.TestCase):
    def test_get_xgrid_numeric_without_floor(self) -> None:
        sr = pd.Series([1.2, 2.5, 5.8])
        precision = 0.5
        result = pdf.get_xgrid(sr_or_idx=sr, precision=precision, include_floor=False)
        expected = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0])
        assert np.array_equal(result, expected)

    def test_get_xgrid_numeric_with_floor(self) -> None:
        sr = pd.Series([3.7, 4.2, 5.9])
        precision = 1
        result = pdf.get_xgrid(sr_or_idx=sr, precision=precision, include_floor=True)
        expected = np.array([3.0, 4.0, 5.0, 6.0])
        assert np.array_equal(result, expected)

    def test_get_xgrid_datetime_without_floor1(self) -> None:
        sr = pd.Series([
            datetime.datetime(2022, 1, 1, 12, 0, 0),
            datetime.datetime(2022, 1, 1, 12, 0, 13),
        ])
        precision = 10  # seconds
        result = pdf.get_xgrid(sr_or_idx=sr, precision=precision, include_floor=False)
        expected = pd.to_datetime([
            "2022-01-01 12:00:00",
            "2022-01-01 12:00:10",
            "2022-01-01 12:00:20",
        ]).values
        assert np.array_equal(result, expected)

    def test_get_xgrid_datetime_without_floor2(self) -> None:
        sr = pd.Series([
            datetime.datetime(2022, 1, 1, 12, 0, 1),
            datetime.datetime(2022, 1, 1, 12, 0, 13),
        ])
        precision = 10  # seconds
        result = pdf.get_xgrid(sr_or_idx=sr, precision=precision, include_floor=False)
        expected = pd.to_datetime([
            "2022-01-01 12:00:10",
            "2022-01-01 12:00:20",
        ]).values
        assert np.array_equal(result, expected)

    def test_get_xgrid_datetime_with_floor(self) -> None:
        sr = pd.Series([
            datetime.datetime(2022, 1, 1, 12, 0, 5),
            datetime.datetime(2022, 1, 1, 12, 1, 0),
        ])
        precision = 60  # seconds
        result = pdf.get_xgrid(sr_or_idx=sr, precision=precision, include_floor=True)
        expected = pd.to_datetime([
            "2022-01-01 12:00:00",
            "2022-01-01 12:01:00",
        ]).values
        assert np.array_equal(result, expected)

    def test_get_xgrid_invalid_type(self) -> None:
        sr = pd.Series(["a", "b", "c"])
        with self.assertRaises(NotImplementedError):
            pdf.get_xgrid(sr_or_idx=sr)


class TestEval(testutil.TestCase):
    def test_get_const_strike_mark_sr(self) -> None:
        window = 3
        sr = pd.Series([0.1, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0])
        is_const_sr = sr.eq(sr.shift(1))
        const_strike_mark_sr = pdf.get_const_strike_mark_sr(is_const_sr=is_const_sr, window=window)
        const_strike_mark_sr_exp = pd.Series([
            False,
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
        ])
        assert const_strike_mark_sr.equals(const_strike_mark_sr_exp)

        window = 3
        sr = pd.Series([0.1, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5])
        is_const_sr = sr.eq(sr.shift(1))
        const_strike_mark_sr = pdf.get_const_strike_mark_sr(is_const_sr=is_const_sr, window=window)
        const_strike_mark_sr_exp = pd.Series([
            False,
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
        ])
        assert const_strike_mark_sr.equals(const_strike_mark_sr_exp)

        window = 3
        sr = pd.Series([0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5])
        is_const_sr = sr.eq(sr.shift(1))
        const_strike_mark_sr = pdf.get_const_strike_mark_sr(is_const_sr=is_const_sr, window=window)
        const_strike_mark_sr_exp = pd.Series([
            False,
            True,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
        ])
        assert const_strike_mark_sr.equals(const_strike_mark_sr_exp)

    def test_keep_first_in_freq(self) -> None:
        ts_sr = pd.Series([
            datetime.datetime(
                2022,
                7,
                7,
                13,
                25,
                19,
            ),
            datetime.datetime(2022, 7, 7, 13, 25, 19, 100000),
            datetime.datetime(2022, 7, 7, 13, 25, 20, 200000),
            datetime.datetime(2022, 7, 7, 13, 25, 20, 400000),
            datetime.datetime(
                2022,
                7,
                7,
                13,
                25,
                21,
            ),
        ])
        ts_1s_sr = pdf.keep_first_in_freq(ts_sr, freq='1s')
        exp_sr = ts_sr.loc[pd.Index([0, 2, 4])]
        assert ts_1s_sr.equals(exp_sr)


class TestCalculateProfitFromTrades(testutil.TestCase):
    def _assert_result_table_structure(self, df: pd.DataFrame, result_df: pd.DataFrame) -> None:
        self.assertFalse(df is result_df)  # df should not be modified
        for column in [
            'basePosition',
            'quotePosition',
            'tradeProfit',
            'cumulativeProfit',
        ]:
            self.assertIn(column, result_df.columns)

    def test_calculate_profit_from_trades_basic(self) -> None:
        df = pd.DataFrame({
            'baseQuantity': [1.0, 2.0, 1.5, 1.0],
            'quoteQuantity': [10000.0, 22000.0, 15000.0, 9000.0],
            'side': ['buy', 'buy', 'sell', 'sell'],
            'price': [10000.0, 11000.0, 10000.0, 9000.0],
            'fee': [10.0, 20.0, 15.0, 10.0],
            'quote_coin': ['USDT', 'USDT', 'USDT', 'USDT'],
            'fee_asset': ['USDT', 'USDT', 'USDT', 'USDT'],
        })

        result_df = pdf.calculate_profit_from_trades(df, 0, 1)

        self._assert_result_table_structure(df, result_df)

        self.assertTrue(np.allclose(result_df['basePosition'].values, [1.0, 3.0, 1.5, 0.5]))  # type: ignore[arg-type]
        self.assertTrue(
            np.allclose(result_df['quotePosition'].values, [-10000.0, -32000.0, -17000.0, -8000.0])  # type: ignore[arg-type]
        )

        self.assertEqual(list(result_df['cumulativeProfit'].values), [-10, 980, -2015, -3510])
        self.assertEqual(list(result_df['tradeProfit'].values), [0.0, 990.0, -2995.0, -1495.0])

    def test_calculate_profit_from_trades_initial_position(self) -> None:
        df = pd.DataFrame({
            'baseQuantity': [1.0, 2.0, 1.5, 1.0],
            'quoteQuantity': [10000.0, 22000.0, 15000.0, 9000.0],
            'side': ['buy', 'buy', 'sell', 'sell'],
            'price': [10000.0, 11000.0, 10000.0, 9000.0],
            'fee': [10.0, 20.0, 15.0, 10.0],
            'quote_coin': ['USDT', 'USDT', 'USDT', 'USDT'],
            'fee_asset': ['USDT', 'USDT', 'USDT', 'USDT'],
        })

        result_df = pdf.calculate_profit_from_trades(df, 1, 1)

        self._assert_result_table_structure(df, result_df)

        self.assertEqual(list(result_df['basePosition'].values), [2.0, 4.0, 2.5, 1.5])
        self.assertEqual(
            list(result_df['quotePosition'].values), [-10000.0, -32000.0, -17000.0, -8000.0]
        )
        self.assertEqual(
            list(result_df['cumulativeProfit'].values), [-10.0, 1980.0, -2015.0, -4510.0]
        )
        self.assertEqual(list(result_df['tradeProfit'].values), [0.0, 1990.0, -3995.0, -2495.0])

    def test_calculate_profit_from_trades_with_position_flips(self) -> None:
        # Create a test DataFrame with position flips (from long to short and vice versa)
        df = pd.DataFrame({
            'baseQuantity': [1.0, 2.0, 4.0, 2.0, 3.0],
            'quoteQuantity': [10000.0, 20000.0, 44000.0, 18000.0, 33000.0],
            'side': ['buy', 'buy', 'sell', 'sell', 'buy'],
            'price': [10000.0, 10000.0, 11000.0, 9000.0, 11000.0],
            'fee': [10.0, 20.0, 40.0, 20.0, 30.0],
            'quote_coin': ['USDT', 'USDT', 'USDT', 'USDT', 'USDT'],
            'fee_asset': ['USDT', 'USDT', 'USDT', 'USDT', 'USDT'],
        })

        result_df = pdf.calculate_profit_from_trades(df, 0, 1)

        self._assert_result_table_structure(df, result_df)

        self.assertTrue(np.allclose(result_df['basePosition'].values, [1.0, 3.0, -1.0, -3.0, 0.0]))  # type: ignore[arg-type]
        self.assertTrue(
            np.allclose(
                result_df['quotePosition'].values,  # type: ignore[arg-type]
                [-10000.0, -30000.0, 14000.0, 32000.0, -1000.0],
            )
        )

        self.assertEqual(
            list(result_df['cumulativeProfit'].values), [-10.0, -20.0, 2960.0, 4980.0, -1030.0]
        )
        self.assertEqual(
            list(result_df['tradeProfit'].values), [0.0, -10.0, 2980.0, 2020.0, -6010.0]
        )

    def test_calculate_profit_from_trades_with_reverse_position_flips(self) -> None:
        # Create a test DataFrame starting with sells (short position) and flipping to buys (long position)
        df = pd.DataFrame({
            'baseQuantity': [2.0, 1.0, 4.0, 2.0, 3.0],
            'quoteQuantity': [20000.0, 9000.0, 36000.0, 22000.0, 36000.0],
            'side': ['sell', 'sell', 'buy', 'buy', 'sell'],
            'price': [10000.0, 9000.0, 9000.0, 11000.0, 12000.0],
            'fee': [20.0, 10.0, 40.0, 20.0, 30.0],
            'quote_coin': ['USDT', 'USDT', 'USDT', 'USDT', 'USDT'],
            'fee_asset': ['USDT', 'USDT', 'USDT', 'USDT', 'USDT'],
        })

        result_df = pdf.calculate_profit_from_trades(df, 0, 1)

        self._assert_result_table_structure(df, result_df)

        self.assertTrue(np.allclose(result_df['basePosition'].values, [-2.0, -3.0, 1.0, 3.0, 0.0]))  # type: ignore[arg-type]
        self.assertTrue(
            np.allclose(
                result_df['quotePosition'].values,  # type: ignore[arg-type]
                [20000.0, 29000.0, -7000.0, -29000.0, 7000.0],
            )
        )

        self.assertEqual(
            list(result_df['cumulativeProfit'].values), [-20.0, 1990.0, 1960.0, 3980.0, 6970.0]
        )
        self.assertEqual(
            list(result_df['tradeProfit'].values), [0.0, 2010.0, -30.0, 2020.0, 2990.0]
        )

    def test_calculate_profit_from_trades_empty_dataframe(self) -> None:
        df = pd.DataFrame({
            'baseQuantity': [],
            'quoteQuantity': [],
            'side': [],
            'price': [],
            'fee': [],
            'quote_coin': [],
            'fee_asset': [],
        })

        result_df = pdf.calculate_profit_from_trades(df, 0, 1)

        self._assert_result_table_structure(df, result_df)
        self.assertEqual(len(result_df), 0)
