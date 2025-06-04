# mypy: disable-error-code="no-redef"
from anre.utils import testutil
from anre.utils.safeWrap.safeWrap import SafeWrap
from anre.utils.safeWrap.safeWrapResult import SafeWrapResult


class TestSafeWrapDecorator(testutil.TestCase):
    def test_wrapFun_basicFunctions(self) -> None:
        @SafeWrap.decorator(verbose=False)
        def foo(x, y):
            """Document"""
            if not x:
                raise NotImplementedError
            return x + y

        res = foo(x=1, y=1)
        assert isinstance(res, SafeWrapResult)
        assert res.success

        res = foo(x=0, y=1)
        assert isinstance(res, SafeWrapResult)
        assert not res.success

        @SafeWrap.decorator(verbose=False, default=0)
        def foo(x, y):
            """Document"""
            if not x:
                raise NotImplementedError
            return x + y

        res = foo(x=1, y=1)
        assert res == 2

        res = foo(x=0, y=1)
        assert res == 0
