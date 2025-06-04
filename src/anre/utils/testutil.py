import os
import unittest
from typing import Callable


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ['FISH_TEST_RUN'] = '1'

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            del os.environ['FISH_TEST_RUN']
        except KeyError:
            pass


_UNSTABLE_ENV_VAR = 'FISH_RUN_UNSTABLE_TESTS'


def unstable(fn: Callable[..., None]) -> Callable[..., None]:
    if os.environ.get(_UNSTABLE_ENV_VAR):
        return fn

    return unittest.skip(f"Unstable test disabled, set ${_UNSTABLE_ENV_VAR} to run anyway")(fn)
