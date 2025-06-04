# mypy: disable-error-code="func-returns-value"
import time

from anre.utils import testutil
from anre.utils.fun.returnValueThread import ReturnValueThread


def square(x):
    time.sleep(1)
    return x**2


class TestLastValueStepFunction(testutil.TestCase):
    def test_numeric_to_numeric(self) -> None:
        value = 4
        thread1 = ReturnValueThread(target=square, args=(value,))
        thread1.start()
        result = thread1.join()
        assert result == value**2
