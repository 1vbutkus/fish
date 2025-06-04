from anre.utils import testutil
from anre.utils.dotNest.dotNest import DotNest


class TestInternals(testutil.TestCase):
    def test_split_happyPath(self) -> None:
        assert DotNest._getSplit_keys('a.b.c') == ['a', 'b', 'c']
        assert DotNest._getSplit_keys('a.b[0].c') == ['a', 'b', 0, 'c']
        assert DotNest._getSplit_keys('a.b.0.c') == ['a', 'b', '0', 'c']
        assert DotNest._getSplit_keys('[0].1.b.c') == [0, '1', 'b', 'c']
        assert DotNest._getSplit_keys('a[0].1.b.c') == ['a', 0, '1', 'b', 'c']
        assert DotNest._getSplit_keys('a[0]|1|b.|c', sep='|') == ['a', 0, '1', 'b.', 'c']

        assert DotNest._getSplit_keys(['a', '1']) == ['a', '1']

    def test_splitAssert(self) -> None:
        # with self.assertRaises(AssertionError):
        #     DotNest._getSplit_keys('a[b]')
        #
        # with self.assertRaises(AssertionError):
        #     DotNest._getSplit_keys('a[')

        with self.assertRaises(ValueError):
            DotNest._getSplit_keys(5)  # type: ignore[arg-type]
