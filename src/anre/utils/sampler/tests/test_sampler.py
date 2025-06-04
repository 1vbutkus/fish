# mypy: disable-error-code="assignment"
import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.sampler.sampler import Sampler


class TestSampler(testutil.TestCase):
    df: pd.DataFrame

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        df = pd.DataFrame(np.random.normal(0, size=(1000, 4)), columns=list('ABCD'))
        df['_someId'] = np.random.randint(0, 6, size=1000)
        cls.df = df

    def test_sampleNumpy(self) -> None:
        X = np.random.normal(0, size=(100, 4))
        smplX = Sampler.sampleNumpy(X, size=10)
        self.assertEqual(smplX.shape, (10, 4))

    def test_sampleNumpyOrPandas(self) -> None:
        X = np.random.normal(0, size=(100, 4))
        smplX = Sampler.sampleNumpyOrPandas(X, size=10)
        self.assertEqual(smplX.shape, (10, 4))

        X = pd.DataFrame(np.random.normal(0, size=(100, 4)))
        smplX = Sampler.sampleNumpyOrPandas(X, size=10)
        self.assertEqual(smplX.shape, (10, 4))

    def test_get_splitCvGnr(self) -> None:
        sr = pd.Series(list('ABCDEFGH'))
        splitCvGnr = Sampler.get_splitCvGnr(sr, nSplits=3)
        splitCv = list(splitCvGnr)
        self.assertEqual(len(splitCv), 3)

        sr = pd.Series(list('ABCDEFGH'))
        splitCvGnr = Sampler.get_splitCvGnr(sr, nSplits=3, shuffle=True)
        splitCv = list(splitCvGnr)
        self.assertEqual(len(splitCv), 3)

    def test_ensureSize(self) -> None:
        df = self.df

        sdf = Sampler.ensureSize(df=df, size=6)
        self.assertEqual(sdf.shape[0], 6)

        sdf = Sampler.ensureSize(df=df, size=1000)
        self.assertEqual(sdf.shape[0], 1000)

    def test_strataSample(self) -> None:
        df = self.df

        sdf = Sampler.strataSample(df=df, strataFields=['_someId'], sizeInStrata=2)
        self.assertTrue(10 <= sdf.shape[0] <= 12)

    def test_strataSample_singleInStrata(self) -> None:
        df = self.df

        sdf = Sampler.strataSample_singleInStrata(df=df, strataFields=['_someId'])
        self.assertEqual(sdf.shape[0], 6)

    def test_balanceDf_underSampling(self) -> None:
        df = self.df

        sdf = Sampler.balance_under_sampling(df=df, strata_field='_someId')
        valueCounts = sdf['_someId'].value_counts()
        self.assertEqual(valueCounts.nunique(), 1)

    def test_balanceDf_oversampling(self) -> None:
        df = self.df

        sdf = Sampler.balanceDf_oversampling(df=df, field='_someId')
        valueCounts = sdf['_someId'].value_counts()
        self.assertEqual(valueCounts.nunique(), 1)
