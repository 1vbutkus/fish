import datetime

import numpy as np
import pandas as pd
from parameterized import parameterized

from anre.utils import testutil
from anre.utils.time import functions
from anre.utils.time.convert import Convert as TimeConvert
from anre.utils.time.functions import split_date_ranges


class TestTimeFunctions(testutil.TestCase):
    dt: datetime.datetime
    xDtList: list[datetime.datetime]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        dt = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)
        xDtList = [
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 100000),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 366667),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 500000),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 999998),
        ]
        cls.dt = dt
        cls.xDtList = xDtList

    def test_unexpectedTypes(self) -> None:
        with self.assertRaises(NotImplementedError):
            functions.floor_dt(x=datetime.time())

        with self.assertRaises(NotImplementedError):
            functions.ceil_dt(x=datetime.time())

        with self.assertRaises(NotImplementedError):
            functions.time_mean(x=datetime.time())  # type: ignore[arg-type]

    def test_ceilAndFloor_const(self) -> None:
        dtOrgConst = self.dt

        for dt in [
            dtOrgConst,
            np.datetime64(dtOrgConst),
            pd.Timestamp(TimeConvert.dt2number(dtOrgConst)),
        ]:
            for precision in [0.01, 0.5, 1, 10]:
                floorDt = functions.floor_dt(dt, precision=precision)
                self.assertIsInstance(floorDt, datetime.datetime)
                assert floorDt.microsecond % int(precision * 1000000) == 0
                assert (
                    floorDt
                    == functions.floor_dt(floorDt, precision=precision)
                    == functions.ceil_dt(floorDt, precision=precision)
                )

                ceilDt = functions.ceil_dt(dt, precision=precision)
                self.assertIsInstance(ceilDt, datetime.datetime)
                assert ceilDt.microsecond % int(precision * 1000000) == 0
                assert (
                    ceilDt
                    == functions.floor_dt(ceilDt, precision=precision)
                    == functions.ceil_dt(ceilDt, precision=precision)
                )

                assert floorDt <= dt <= ceilDt

    def test_ceilAndFloor_series(self) -> None:
        xDtList = self.xDtList

        for precision in [0.01, 0.5, 1, 10]:
            sr = pd.Series(xDtList)
            floorDtSr = functions.floor_dt(sr, precision=precision)
            self.assertIsInstance(floorDtSr, pd.Series)
            self.assertTrue(all(floorDtSr.dt.microsecond % int(precision * 1000000) == 0))
            self.assertTrue(all(floorDtSr == functions.floor_dt(floorDtSr, precision=precision)))
            self.assertTrue(all(floorDtSr == functions.ceil_dt(floorDtSr, precision=precision)))

            ceilDtSr = functions.ceil_dt(sr, precision=precision)
            self.assertIsInstance(ceilDtSr, pd.Series)
            self.assertTrue(all(ceilDtSr.dt.microsecond % int(precision * 1000000) == 0))
            self.assertTrue(all(ceilDtSr == functions.floor_dt(ceilDtSr, precision=precision)))
            self.assertTrue(all(ceilDtSr == functions.ceil_dt(ceilDtSr, precision=precision)))

            self.assertTrue(all(floorDtSr <= sr))
            self.assertTrue(all(sr <= ceilDtSr))

    def test_ceilAndFloor_numpy(self) -> None:
        xDtList = self.xDtList

        for precision in [0.01, 0.5, 1, 10]:
            arr = pd.Series(xDtList).values
            floorDtArr = functions.floor_dt(arr, precision=precision)
            self.assertIsInstance(floorDtArr, np.ndarray)
            self.assertTrue(all(floorDtArr == functions.floor_dt(floorDtArr, precision=precision)))
            self.assertTrue(all(floorDtArr == functions.ceil_dt(floorDtArr, precision=precision)))

            ceilDtArr = functions.ceil_dt(arr, precision=precision)
            self.assertIsInstance(ceilDtArr, np.ndarray)
            self.assertTrue(all(ceilDtArr == functions.floor_dt(ceilDtArr, precision=precision)))
            self.assertTrue(all(ceilDtArr == functions.ceil_dt(ceilDtArr, precision=precision)))

            self.assertTrue(all(floorDtArr <= arr))
            self.assertTrue(all(arr <= ceilDtArr))

    def test_timeMean(self) -> None:
        xDtList = self.xDtList

        sr = pd.Series(xDtList)
        res1 = functions.time_mean(sr)
        res2 = functions.time_mean(sr.values)  # type: ignore[arg-type]
        self.assertTrue(res1 == res2)
        self.assertTrue(abs((sr - res1).dt.total_seconds().mean()) < 1e-5)

    def test_time_range(self) -> None:
        time_range = functions.get_time_range(
            datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 2), precision=3600
        )

        self.assertIsInstance(time_range, np.ndarray)
        self.assertEqual(
            list(time_range),
            [
                np.datetime64('2020-01-01T00:00:00.000000000'),
                np.datetime64('2020-01-01T01:00:00.000000000'),
                np.datetime64('2020-01-01T02:00:00.000000000'),
                np.datetime64('2020-01-01T03:00:00.000000000'),
                np.datetime64('2020-01-01T04:00:00.000000000'),
                np.datetime64('2020-01-01T05:00:00.000000000'),
                np.datetime64('2020-01-01T06:00:00.000000000'),
                np.datetime64('2020-01-01T07:00:00.000000000'),
                np.datetime64('2020-01-01T08:00:00.000000000'),
                np.datetime64('2020-01-01T09:00:00.000000000'),
                np.datetime64('2020-01-01T10:00:00.000000000'),
                np.datetime64('2020-01-01T11:00:00.000000000'),
                np.datetime64('2020-01-01T12:00:00.000000000'),
                np.datetime64('2020-01-01T13:00:00.000000000'),
                np.datetime64('2020-01-01T14:00:00.000000000'),
                np.datetime64('2020-01-01T15:00:00.000000000'),
                np.datetime64('2020-01-01T16:00:00.000000000'),
                np.datetime64('2020-01-01T17:00:00.000000000'),
                np.datetime64('2020-01-01T18:00:00.000000000'),
                np.datetime64('2020-01-01T19:00:00.000000000'),
                np.datetime64('2020-01-01T20:00:00.000000000'),
                np.datetime64('2020-01-01T21:00:00.000000000'),
                np.datetime64('2020-01-01T22:00:00.000000000'),
                np.datetime64('2020-01-01T23:00:00.000000000'),
                np.datetime64('2020-01-02T00:00:00.000000000'),
            ],
        )

    def test_time_range_equal(self) -> None:
        time_range = functions.get_time_range(
            datetime.datetime(2020, 1, 10), datetime.datetime(2020, 1, 10), precision=3600
        )

        self.assertIsInstance(time_range, np.ndarray)
        self.assertEqual(
            list(time_range),
            [
                np.datetime64('2020-01-10T00:00:00.000000000'),
            ],
        )

    def test_time_range_empty(self) -> None:
        time_range = functions.get_time_range(
            datetime.datetime(2020, 1, 10), datetime.datetime(2020, 1, 9), precision=3600
        )

        self.assertIsInstance(time_range, np.ndarray)
        self.assertEqual(list(time_range), [])

    @parameterized.expand([
        # Test name, from_dt, to_dt, step, expected_dates
        (
            "one_day_step_with_time_alignment",
            datetime.datetime(2023, 1, 1, 12, 30),
            datetime.datetime(2023, 1, 4, 15, 45),
            1,
            [
                datetime.datetime(2023, 1, 1),
                datetime.datetime(2023, 1, 2),
                datetime.datetime(2023, 1, 3),
                datetime.datetime(2023, 1, 4),
            ],
        ),
        (
            "two_day_step",
            datetime.datetime(2023, 1, 1),
            datetime.datetime(2023, 1, 5),
            2,
            [
                datetime.datetime(2023, 1, 1),
                datetime.datetime(2023, 1, 3),
                datetime.datetime(2023, 1, 5),
            ],
        ),
    ])
    def test_split_date_ranges_cases(self, name, from_dt, to_dt, step, expected_dates):
        dates = list(split_date_ranges(from_dt, to_dt, step=step))
        self.assertEqual(dates, expected_dates)

    def test_split_date_ranges_negative_step(self):
        with self.assertRaises(ValueError):
            list(
                split_date_ranges(
                    datetime.datetime(2023, 1, 1), datetime.datetime(2023, 1, 5), step=-1
                )
            )
