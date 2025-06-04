# mypy: disable-error-code="assignment"
import pandas as pd

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.pandas_.manipulation.constantMotionTransformation import (
    ConstantMotionTransformation,
)


class TestEval(testutil.TestCase):
    df: pd.DataFrame
    transFields: list[str]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        n = 1000
        df = pdu.new.get_randomDf(shape=(n, 3))
        df.index = range(n)
        transFields = ['x1', 'x2']

        cls.df = df
        cls.transFields = transFields

    def test_validate_constantMotion(self) -> None:
        df = self.df

        res = ConstantMotionTransformation.validate_constantMotion(df, stepSize=1)
        self.assertTrue(res)

        with self.assertRaises(AssertionError):
            res = ConstantMotionTransformation.validate_constantMotion(df, stepSize=2)

    def test_get_emaDf(self) -> None:
        df = self.df
        transFields = self.transFields

        res = ConstantMotionTransformation.get_emaDf(
            df, transFields=transFields, halflifes=[10, 20]
        )
        self.assertIsInstance(res, pd.DataFrame)
        self.assertEqual(res.shape, (df.shape[0], 4))
        self.assertFalse(res.isna().any().any())

    def test_get_rollExtDf(self) -> None:
        df = self.df
        transFields = self.transFields

        res = ConstantMotionTransformation.get_rollExtDf(df, transFields=transFields, wins=[10, 20])
        self.assertIsInstance(res, pd.DataFrame)
        self.assertEqual(res.shape, (df.shape[0], 8))
        self.assertFalse(res.isna().loc[20:].any().any())

    def test_get_rollMedianExtDf(self) -> None:
        df = self.df
        transFields = self.transFields

        res = ConstantMotionTransformation.get_rollMedianExtDf(
            df, transFields=transFields, medWins=[30], extWins=[10, 20]
        )
        self.assertIsInstance(res, pd.DataFrame)
        self.assertEqual(res.shape, (df.shape[0], 8))
        self.assertFalse(res.isna().loc[30:].any().any())
