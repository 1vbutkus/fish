# mypy: disable-error-code="attr-defined"
import numpy as np
import pandas as pd
from scipy import signal

from anre.utils import testutil
from anre.utils.stats import stats


class TestStats(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        n = 1000
        _x = np.random.normal(size=n)
        x = np.concatenate([_x, _x + 4])
        y = 20 + 3 * x + np.random.normal(size=2 * n)
        df = pd.DataFrame(dict(x=x, y=y))
        cls.df = df

    def test_get_gaussianKdeSr(self) -> None:
        df = self.df
        gaussianKdeSr = stats.get_gaussianKdeSr(x=df['x'])
        self.assertIsInstance(gaussianKdeSr, pd.Series)

    def test_get_meanAndStdDf_viaKnn(self) -> None:
        df = self.df

        newX = pd.Series(np.linspace(df['x'].min(), df['x'].max()), name='x').to_frame()
        meanAndStdDf = stats.get_meanAndStdDf_viaKnn(
            X=df[['x']].values, y=df['y'].values, newX=newX.values, nNeighbors=20
        )
        # meanAndStdDf['x'] = newX['x']
        # meanAndStdDf.plot.scatter(x='x', y='mean')
        self.assertIsInstance(meanAndStdDf, pd.DataFrame)

    def test_get_mean_estimates_adjusted_by_autocorrelation(self) -> None:
        a = [1, -0.99]
        b = [1]
        eps = np.random.normal(size=10000)
        x = pd.Series(signal.lfilter(b, a, eps))
        mean_estimates_sr = stats.get_mean_estimates_adjusted_by_autocorrelation(x=x)
        assert isinstance(mean_estimates_sr, pd.Series)

    def test_get_effective_sample_size(self) -> None:
        a = [1, -0.99]
        b = [1]
        eps = np.random.normal(size=10000)
        x = pd.Series(signal.lfilter(b, a, eps))
        effective_sample_size = stats.get_effective_sample_size(x=x)
        assert effective_sample_size < 10000
        effective_sample_size = stats.get_effective_sample_size(x=x, method='multi', nlags=1000)
        assert effective_sample_size < 10000
