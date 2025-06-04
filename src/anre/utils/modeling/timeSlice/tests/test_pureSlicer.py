# mypy: disable-error-code="attr-defined"
from anre.utils import testutil
from anre.utils.modeling.timeSlice.pureSlice import PureSlice
from anre.utils.modeling.timeSlice.pureSlicer import PureSlicer


class TestPureSlicer(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        values = list(range(100, 150))
        trainSize = 20
        testSize = 5
        shiftStep = -5
        testInitPoss = 10

        internalSlicer = PureSlicer(
            values=values,
            trainSize=trainSize,
            testSize=testSize,
            shiftStep=shiftStep,
            testInitPoss=testInitPoss,
        )
        cls.internalSlicer = internalSlicer

    def test_get_sliceIds(self) -> None:
        internalSlicer = self.internalSlicer
        sliceIds = list(internalSlicer.get_sliceIds())
        self.assertEqual(sliceIds, [0, 1])

    def test_get_pureSlice(self) -> None:
        internalSlicer = self.internalSlicer

        pureSlice = internalSlicer.get_pureSlice(sliceId=0)
        self.assertIsInstance(pureSlice, PureSlice)
        self.assertEqual(set(pureSlice.get_testIds()), {5, 6, 7, 8, 9})
        self.assertEqual(set(pureSlice.get_testValues()), {105, 106, 107, 108, 109})
        self.assertEqual(
            set(pureSlice.get_testIds()).union(set(pureSlice.get_trainIds())), set(range(25))
        )
        self.assertEqual(
            set(pureSlice.get_testIds()).intersection(set(pureSlice.get_trainIds())), set()
        )

        pureSlice = internalSlicer.get_pureSlice(sliceId=1)
        self.assertIsInstance(pureSlice, PureSlice)
        self.assertEqual(set(pureSlice.get_testIds()), {0, 1, 2, 3, 4})
        self.assertEqual(set(pureSlice.get_testValues()), {100, 101, 102, 103, 104})
        self.assertEqual(
            set(pureSlice.get_testIds()).union(set(pureSlice.get_trainIds())), set(range(25))
        )
        self.assertEqual(
            set(pureSlice.get_testIds()).intersection(set(pureSlice.get_trainIds())), set()
        )

    def test_get_sliceCount(self) -> None:
        res = PureSlicer.get_sliceCount(
            countValue=50,
            testSize=10,
            shiftStep=5,
            testInitPoss=0,
            sliceCountCap=None,
        )
        self.assertEqual(res, 9)
