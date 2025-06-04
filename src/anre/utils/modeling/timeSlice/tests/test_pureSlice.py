# mypy: disable-error-code="attr-defined"
from anre.utils import testutil
from anre.utils.modeling.timeSlice.pureSlice import PureSlice


class TestPureSlice(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        pureSlice = PureSlice(
            sliceId=0,
            values=list(range(100, 150)),
            trainIds=list(range(10, 20)),
            testIds=list(range(20, 40)),
        )
        cls.pureSlice = pureSlice

    def test_get_sliceId(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.get_sliceId()
        self.assertEqual(res, 0)

    def test_get_testValues(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.get_testValues()
        self.assertIsInstance(res, list)

    def test_get_trainValues(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.get_trainValues()
        self.assertIsInstance(res, list)

    def test_get_testIds(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.get_testIds()
        self.assertIsInstance(res, list)

    def test_get_trainIds(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.get_trainIds()
        self.assertIsInstance(res, list)

    def test_get_allIds(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.get_allIds()
        self.assertIsInstance(res, list)

    def test_get_values(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.get_values()
        self.assertIsInstance(res, list)

    def test__repr__(self) -> None:
        pureSlice = self.pureSlice
        res = pureSlice.__repr__()
        self.assertIsInstance(res, str)
