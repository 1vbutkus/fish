# mypy: disable-error-code="call-overload"
import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.pandas_ import sample as pandas_sample


class TestEval(testutil.TestCase):
    def test_split_trainTest(self) -> None:
        X = pd.DataFrame(np.random.rand(1000, 3))
        y = pd.Series(np.random.rand(1000))
        groups = pd.Series(np.array([0, 1, 2, 3, 4] * 200))
        df = pd.concat(dict(X=X, y=y, groups=groups), axis=1)

        trainDf, testDf = pandas_sample.split_trainTest(
            df=df, groups=groups, useShuffleSplit=False, test_size=0.2
        )
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200
        assert not set(trainDf['groups'][1]) & set(testDf['groups'][1])

        trainDf, testDf = pandas_sample.split_trainTest(
            df=df, groups=groups, useShuffleSplit=True, test_size=0.2
        )
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200
        assert not set(trainDf.groups[1]) & set(testDf.groups[1])

        trainDf, testDf = pandas_sample.split_trainTest(df=df, useShuffleSplit=False, test_size=0.2)
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200
        assert set(trainDf.groups[1]) & set(testDf.groups[1])

        trainDf, testDf = pandas_sample.split_trainTest(df=df, useShuffleSplit=True, test_size=0.2)
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200
        assert set(trainDf.groups[1]) & set(testDf.groups[1])

        trainDf, testDf = pandas_sample.split_trainTest(
            df=df, groups=groups, useShuffleSplit=False, test_size=0.2
        )
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200

        trainDf, testDf = pandas_sample.split_trainTest(
            df=df, groups=groups, useShuffleSplit=True, test_size=0.2
        )
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200

        trainDf, testDf = pandas_sample.split_trainTest(df=df, useShuffleSplit=False, test_size=0.2)
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200

        trainDf, testDf = pandas_sample.split_trainTest(df=df, useShuffleSplit=True, test_size=0.2)
        assert trainDf.X.shape[0] == 800
        assert testDf.X.shape[0] == 200
