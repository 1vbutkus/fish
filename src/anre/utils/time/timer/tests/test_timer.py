import datetime
import unittest

from anre.utils.time.convert import Convert
from anre.utils.time.timer.iTimer import ITimer
from anre.utils.time.timer.timerDouble import TimerDouble
from anre.utils.time.timer.timerNaive import TimerNaive
from anre.utils.time.timer.timerPseudo import TimerPseudo
from anre.utils.time.timer.timerReal import TimerReal


class TestTimer(unittest.TestCase):
    def test_smokeTest(self):
        timers = [TimerReal(), TimerNaive(), TimerDouble(timerOriginal=TimerNaive()), TimerPseudo()]
        for timer in timers:
            self._test_smoke(timer=timer)

    def test_cache(self):
        timer1 = TimerReal()
        timer2 = TimerReal()
        timer1.update(force=True)
        assert timer1.offsetSec == timer2.offsetSec

    def test_basic_pseudoTimer(self):
        timer = TimerPseudo()

        resDt1 = timer.nowDt()
        self.assertIsInstance(resDt1, datetime.datetime)

        resS1 = timer.nowS()
        self.assertIsInstance(resS1, float)

        resDt2 = timer.nowDt()
        self.assertIsInstance(resDt2, datetime.datetime)
        self.assertEqual(resDt1, resDt2)

        resS2 = timer.nowS()
        self.assertIsInstance(resS2, float)
        self.assertEqual(resS1, resS2)

        timer.set_currentTime(shiftSec=1)
        resDt3 = timer.nowDt()
        self.assertIsInstance(resDt3, datetime.datetime)
        self.assertTrue(resDt3 > resDt2)
        self.assertTrue((resDt3 - resDt2).total_seconds() == 1)

        resS3 = timer.nowS()
        self.assertIsInstance(resS3, float)
        self.assertTrue(resS3 - resS2 == 1)

        timer.set_currentTime(nowDt=resDt3)
        resDt4 = timer.nowDt()
        self.assertEqual(resDt4, resDt3)

        resS4 = timer.nowS()
        self.assertEqual(resS4, resS3)

        resDt, resSeconds = timer.nowDt(), timer.nowS()
        self.assertIsInstance(resDt, datetime.datetime)
        self.assertIsInstance(resSeconds, float)
        secondsFromDt = Convert.datetime2seconds(resDt)
        assert abs(resSeconds - secondsFromDt) < 1e-4

    def _test_smoke(self, timer: ITimer):
        resDt, resSeconds = timer.nowDt(), timer.nowS()
        self.assertIsInstance(resDt, datetime.datetime)
        self.assertIsInstance(resSeconds, float)
        secondsFromDt = Convert.datetime2seconds(resDt)
        self.assertAlmostEqual(resSeconds, secondsFromDt, places=4)
