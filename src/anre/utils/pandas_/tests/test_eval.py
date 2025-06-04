import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.pandas_.eval import Eval


class TestEval(testutil.TestCase):
    def test_eval_basicHappyPath(self) -> None:
        myDf = pd.DataFrame({'A': range(1, 6), 'B': range(10, 0, -2)})

        expSr = pd.Series([1, 2, 3, 4, 5])
        resSr = Eval.eval(df=myDf, expr='A')
        self.assertTrue(expSr.equals(resSr))
        resSr = Eval.get_fieldSr(df=myDf, field='A')
        self.assertTrue(expSr.equals(resSr))

        # test that Immutable
        resSr.iloc[0] = 0
        self.assertFalse(myDf['A'].equals(resSr))

        expSr = pd.Series([1, 2, 3, 3, 3])
        resSr = Eval.eval(df=myDf, expr='clip(A, 0, 3)')
        self.assertTrue(expSr.equals(resSr))

        expSr = pd.Series([1, 2, 3, 4, 2])
        resSr = Eval.eval(df=myDf, expr='minimum(A, B)')
        self.assertTrue(expSr.equals(resSr))

    def test_eval_negativeArguments(self) -> None:
        n = 10
        trainDf = pd.DataFrame({
            'y_target': np.random.normal(size=n),
            '_someVar': np.random.normal(size=n),
            'x1': np.random.normal(size=n),
            'x2': np.random.normal(size=n),
        })
        Eval.get_fieldSr(df=trainDf, field='clip(y_target, -1, 1)')
