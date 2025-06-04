import datetime
import time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.time.convert import Convert as TimeConvert


class TestConvert(testutil.TestCase):
    xDtList: list[datetime.datetime]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        xDtList = [
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 100000),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 366667),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 500000),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 999998),
        ]
        cls.xDtList = xDtList

    def test_matplotlib(self):
        dt_list = [
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 100000),
            datetime.datetime(2019, 4, 1, 5, 40, 47, 366667),
        ]

        a = TimeConvert.dt2matplotlib(dt_list[0])
        b = TimeConvert.matplotlib2dt(a)
        assert dt_list[0] == b

        sr = pd.Series(dt_list)
        a = TimeConvert.dt2matplotlib(sr)
        b = TimeConvert.matplotlib2dt(a)
        assert np.array_equal(sr.values, b)

    def test_strConstant(self) -> None:
        dtOrgConst = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)
        self.assertEqual(
            TimeConvert.dt2str(x=dtOrgConst), TimeConvert.dt2str(x=np.datetime64(dtOrgConst))
        )
        self.assertEqual(
            TimeConvert.dt2str(x=dtOrgConst),
            TimeConvert.dt2str(x=pd.Timestamp(TimeConvert.dt2number(dtOrgConst))),
        )

    def test_datetime2seconds(self) -> None:
        dt = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)
        seconds = TimeConvert.datetime2seconds(dt)

        assert isinstance(seconds, float)

        dt2 = TimeConvert.seconds2datetime(seconds)
        assert abs((dt - dt2).total_seconds()) < 1e-4

    def test_dt2seconds(self) -> None:
        dt = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)

        seconds1 = TimeConvert.dt2seconds(dt)
        seconds2 = TimeConvert.datetime2seconds(dt)
        assert abs(seconds1 - seconds2) < 1e-7

        dt1 = TimeConvert.seconds2datetime(seconds1)
        assert dt == dt1
        dt2 = TimeConvert.seconds2dt(seconds1)
        assert dt == dt2

        dt3 = dt + datetime.timedelta(seconds=3)
        seconds3 = TimeConvert.dt2seconds(dt3)
        assert 3 - 1e-7 <= seconds3 - seconds1 <= 3 + 1e-7

    def test_datetime2seconds2(self) -> None:
        seconds = 1580211731.641
        dt = TimeConvert.seconds2datetime(seconds)
        assert isinstance(dt, datetime.datetime)
        seconds2 = TimeConvert.datetime2seconds(dt)
        assert abs(seconds - seconds2) < 1e-4

        # compatability with time.time
        seconds, dt = time.time(), datetime.datetime.utcnow()
        seconds2 = TimeConvert.datetime2seconds(dt)
        assert abs(seconds - seconds2) < 1e-4

    def test_unexpectedTypes(self) -> None:
        with self.assertRaises(NotImplementedError):
            TimeConvert.dt2str(x=datetime.time())  # type: ignore[call-overload]

        with self.assertRaises(NotImplementedError):
            TimeConvert.str2dt(x=datetime.time())  # type: ignore[call-overload]

        with self.assertRaises(NotImplementedError):
            TimeConvert.number2dt(x=datetime.time())  # type: ignore[call-overload]

        with self.assertRaises(NotImplementedError):
            TimeConvert.dt2number(x=datetime.time())  # type: ignore[call-overload]

        with self.assertRaises(NotImplementedError):
            TimeConvert.dt2NaiveUtcDt(x=datetime.time())  # type: ignore[call-overload]

        with self.assertRaises(NotImplementedError):
            TimeConvert.dt2awareDt(x=datetime.time(), tzStr='Europe/Berlin')  # type: ignore[call-overload]

    def test_constant(self) -> None:
        ### const
        dtOrgConst = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)
        for _dtOrgConst in [
            dtOrgConst,
            np.datetime64(dtOrgConst),
            pd.Timestamp(TimeConvert.dt2number(dtOrgConst)),
        ]:
            dtNumber = TimeConvert.dt2number(x=_dtOrgConst)  # type: ignore[call-overload]
            dtStr = TimeConvert.dt2str(x=_dtOrgConst)  # type: ignore[call-overload]

            # different numbers formats, ints
            for _dtNumber in [dtNumber, int(dtNumber), np.int64(dtNumber)]:
                _dt = TimeConvert.number2dt(x=_dtNumber)
                self.assertEqual(type(dtOrgConst), type(_dt))
                self.assertEqual(dtOrgConst, _dt)

            # float is not exactly
            for _dtNumber in [dtNumber, float(dtNumber), np.float64(dtNumber)]:
                _dt = TimeConvert.number2dt(x=_dtNumber)
                self.assertEqual(type(dtOrgConst), type(_dt))
                self.assertTrue(abs(TimeConvert.timedelta2nanoseconds(dtOrgConst - _dt)) <= 1500)

            # from string
            _dt = TimeConvert.str2dt(x=dtStr)
            self.assertEqual(type(dtOrgConst), type(_dt))
            self.assertEqual(dtOrgConst, _dt)

    def test_series_number(self) -> None:
        xDtList = self.xDtList

        xNumerList = [TimeConvert.dt2number(x=xDt) for xDt in xDtList]
        xInput = pd.Series(xDtList)

        res = TimeConvert.dt2number(x=xInput)
        self.assertEqual(type(res), type(xInput))
        self.assertEqual(list(res), xNumerList)
        backToInput = TimeConvert.number2dt(x=res)
        self.assertEqual(type(backToInput), type(xInput))
        self.assertTrue(backToInput.equals(xInput))

    def test_series_str(self) -> None:
        xDtList = self.xDtList

        xStrList = [TimeConvert.dt2str(x=xDt) for xDt in xDtList]
        xInput = pd.Series(xDtList)

        res = TimeConvert.dt2str(x=xInput)
        self.assertEqual(type(res), type(xInput))
        self.assertEqual(list(res), xStrList)
        backToInput = TimeConvert.str2dt(x=res)
        self.assertEqual(type(backToInput), type(xInput))
        self.assertTrue(backToInput.equals(xInput))

    def test_index_number(self) -> None:
        xDtList = self.xDtList

        xNumerList = [TimeConvert.dt2number(x=xDt) for xDt in xDtList]
        xInput = pd.Index(xDtList)

        res = TimeConvert.dt2number(x=xInput)
        self.assertIsInstance(res, pd.Index)
        self.assertEqual(list(res), xNumerList)
        backToInput = TimeConvert.number2dt(x=res)
        self.assertEqual(type(backToInput), type(xInput))
        self.assertTrue(backToInput.equals(xInput))  # type: ignore[arg-type]

    def test_index_str(self) -> None:
        xDtList = self.xDtList

        xStrList = [TimeConvert.dt2str(x=xDt) for xDt in xDtList]
        xInput = pd.Index(xDtList)

        res = TimeConvert.dt2str(x=xInput)
        self.assertIsInstance(res, pd.Index)
        self.assertEqual(list(res), xStrList)
        backToInput = TimeConvert.str2dt(x=res)
        self.assertEqual(type(backToInput), type(xInput))
        self.assertTrue(backToInput.equals(xInput))

    def test_array(self) -> None:
        xDtList = self.xDtList

        xNumerList = [TimeConvert.dt2number(x=xDt) for xDt in xDtList]
        xInput: np.ndarray = pd.Series(xDtList).values  # type: ignore[assignment]

        # array:number
        res = TimeConvert.dt2number(x=xInput)
        self.assertEqual(type(res), type(xInput))
        self.assertEqual(list(res), xNumerList)
        backToInput = TimeConvert.number2dt(x=res)
        self.assertEqual(type(backToInput), type(xInput))
        self.assertTrue(all(backToInput == xInput))

        # series:str - not supported

    def test_dt2awareDt_const(self) -> None:
        dt = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)
        dt_a: datetime.datetime = TimeConvert.dt2awareDt(x=dt, tzStr='Europe/Berlin')
        dt_b = datetime.datetime(2022, 7, 7, 15, 25, 19, 927026, tzinfo=ZoneInfo('Europe/Berlin'))
        self.assertIsInstance(dt_a, datetime.datetime)
        self.assertEqual(dt_a.tzinfo, ZoneInfo('Europe/Berlin'))
        self.assertEqual(dt_a, dt_b)

        dt_c = TimeConvert.dt2awareDt(x=dt_a, tzStr='Europe/Berlin')
        self.assertEqual(dt_a, dt_c)

        # back to input
        dt2 = TimeConvert.dt2NaiveUtcDt(x=dt_c)
        self.assertEqual(dt, dt2)

    def test_dt2NaiveUtcDt_const(self) -> None:
        _dt = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)
        dt_a: datetime.datetime = TimeConvert.dt2NaiveUtcDt(x=_dt)
        self.assertTrue(dt_a.tzname() is None)

        _dt = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026, tzinfo=ZoneInfo('UTC'))
        dt_b: datetime.datetime = TimeConvert.dt2NaiveUtcDt(x=_dt)
        self.assertTrue(dt_b.tzname() is None)
        self.assertEqual(dt_a, dt_b)

        _dt = datetime.datetime(2022, 7, 7, 15, 25, 19, 927026, tzinfo=ZoneInfo('Europe/Berlin'))
        dt_c: datetime.datetime = TimeConvert.dt2NaiveUtcDt(x=_dt)
        self.assertTrue(dt_c.tzname() is None)
        self.assertEqual(dt_a, dt_c)

    def test_seriesVsConst(self) -> None:
        dt1 = datetime.datetime(2022, 1, 7, 13, 25, 19, 927026)
        dt2 = datetime.datetime(2022, 7, 7, 13, 25, 19, 927026)
        dtSr = pd.Series([
            dt1,
            dt2,
        ])

        awareDtSr: pd.Series = TimeConvert.dt2awareDt(x=dtSr, tzStr='Europe/Berlin')
        dt1Aware = TimeConvert.dt2awareDt(x=dt1, tzStr='Europe/Berlin')
        dt2Aware = TimeConvert.dt2awareDt(x=dt2, tzStr='Europe/Berlin')

        assert awareDtSr.iloc[0].to_pydatetime() == dt1Aware
        assert awareDtSr.iloc[1].to_pydatetime() == dt2Aware

    def test_dt2awareDt_series(self) -> None:
        dtSr = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2022, 7, 7, 13, 59, 19, 927026),
        ])
        awareDtSr: pd.Series = TimeConvert.dt2awareDt(x=dtSr, tzStr='Europe/Berlin')
        self.assertIsInstance(awareDtSr, pd.Series)
        self.assertTrue(awareDtSr.dt.tz is not None)

        # back to input
        dtSr2: pd.Series = TimeConvert.dt2NaiveUtcDt(x=awareDtSr)
        self.assertTrue(dtSr.equals(dtSr2))

    def test_dt2NaiveUtcDt_series(self) -> None:
        dtSr = pd.Series([
            datetime.datetime(2022, 7, 7, 13, 25, 19, 927026),
            datetime.datetime(2022, 7, 7, 13, 59, 19, 927026),
        ])
        dtSr2: pd.Series = TimeConvert.dt2NaiveUtcDt(x=dtSr)
        self.assertIsInstance(dtSr2, pd.Series)
        self.assertTrue(dtSr2.dt.tz is None)
        self.assertTrue(dtSr.equals(dtSr2))
