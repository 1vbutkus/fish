# mypy: disable-error-code="attr-defined"
from anre.utils import testutil
from anre.utils.modeling.timeSlice.pureSlice import PureSlice
from anre.utils.modeling.timeSlice.timeSlice import TimeSlice


class TestTimeSlice(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        pureSlice = PureSlice(
            sliceId=0,
            values=list(range(100, 150)),
            trainIds=list(range(10, 20)),
            testIds=list(range(20, 40)),
        )
        timeSlice = TimeSlice(pureSlice=pureSlice)
        cls.timeSlice = timeSlice

    def test_get_sliceId(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.get_sliceId()
        self.assertEqual(res, 0)

    def test_get_testValues(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.get_testValues()
        self.assertIsInstance(res, list)

    def test_get_trainValues(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.get_trainValues()
        self.assertIsInstance(res, list)

    def test_get_testIds(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.get_testIds()
        self.assertIsInstance(res, list)

    def test_get_trainIds(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.get_trainIds()
        self.assertIsInstance(res, list)

    def test_get_allIds(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.get_allIds()
        self.assertIsInstance(res, list)

    def test_get_values(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.get_values()
        self.assertIsInstance(res, list)

    def test__repr__(self) -> None:
        timeSlice = self.timeSlice
        res = timeSlice.__repr__()
        self.assertIsInstance(res, str)

        timeSlice.plot()
