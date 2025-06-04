import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.timeSeries.smooth.lowess.lowess import Lowess


class TestLowess(testutil.TestCase):
    def test_lowess(self) -> None:
        n = 10000
        x = np.linspace(0, 5, n)
        y = np.sin(x) + 0.1 * np.random.normal(size=n) - (x > 2)
        ySr = pd.Series(y, index=x)
        frac = 0.2
        breaks = [2]

        lowessSr1 = Lowess.get_lowessSr(y=ySr, frac=frac, breaks=None)
        self.assertIsInstance(lowessSr1, pd.Series)

        lowessSr2 = Lowess.get_lowessSr(y=ySr, frac=frac, breaks=breaks)
        self.assertIsInstance(lowessSr2, pd.Series)

        # ySr.plot()
        # lowessSr1.plot()
        # lowessSr2.plot()
