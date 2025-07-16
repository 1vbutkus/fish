import time
from typing import Any

from anre.utils import testutil
from anre.utils.iterationProcess.iterationProcessLocal import IterationProcessLocal


class TestIterationProcessLocal(testutil.TestCase):
    def test_basic(self) -> None:
        proc = IterationProcessLocal.new()
        assert not proc.isAlive()
        proc.stop()
        assert not proc.isAlive()
        proc.start()
        assert proc.isAlive()
        proc.stop(wait=True)
        assert not proc.isAlive()

        proc.get_iterationTakesTimeMean()

    def test_customProc_happyPath(self) -> None:
        class CustomProc(IterationProcessLocal):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.iterCount = 0
                self.failCount = 0
                self.isFinalError = False

            def iteration(self):
                self.iterCount += 1

                if self.iterCount == 3:
                    raise ValueError('Temp error')

                if self.iterCount > 5:
                    raise ValueError('Infinite error')

            def run_ifTempFail(self, error: BaseException, *args: Any, **kwargs: Any):
                self.failCount += 1

            def run_ifFinalFail(self, error: BaseException, *args: Any, **kwargs: Any):
                self.isFinalError = True

        proc = CustomProc.new(wait=0.1, sleepInFailList=[0.01, 0.02])
        proc.start()
        assert proc.isAlive()
        time.sleep(2)
        assert not proc.isAlive()

        assert proc.iterCount == 8
        assert proc.failCount == 3
        assert proc.isFinalError

    def test_customProc_errorIn_runInFinalFail(self) -> None:
        class CustomProc(IterationProcessLocal):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.iterCount = 0
                self.finalError = False

            def iteration(self):
                self.iterCount += 1
                if self.iterCount > 3:
                    raise ValueError('Temp error')

            def run_ifFinalFail(self, error: BaseException, *args: Any, **kwargs: Any):
                self.finalError = True
                raise RuntimeError('Final error.')

        proc = CustomProc.new(wait=0.1, sleepInFailList=[0.01, 0.02])
        proc.start()
        time.sleep(1)
        assert not proc.isAlive()
        assert proc.finalError

    def test_customProc_errorIn_runInIterFail(self) -> None:
        class CustomProc(IterationProcessLocal):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.iterCount = 0
                self.interError = False

            def iteration(self):
                self.iterCount += 1
                if self.iterCount == 3:
                    raise ValueError('Temp error')

            def run_ifTempFail(self, error: BaseException, *args: Any, **kwargs: Any):
                self.interError = True
                raise RuntimeError

        proc = CustomProc.new(wait=0.1, sleepInFailList=[0.01, 0.02])
        proc.start()
        time.sleep(1)
        assert not proc.isAlive()
        assert proc.interError
