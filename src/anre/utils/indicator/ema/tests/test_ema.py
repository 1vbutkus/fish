import pandas as pd

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.indicator.ema.ema import Ema


class TestEma(testutil.TestCase):
    def test_get_expandGridDf(self) -> None:
        df = pdu.new.get_randomDf(shape=(7, 3))
        df.loc[4, 'x0'] = pd.NA
        df.loc[4, 'x1'] = pd.NA
        df.loc[5, 'x1'] = pd.NA

        ema = Ema(halflifes=[10, 20], adjust=True)
        ema1 = df.apply(ema.updateReturn, axis=1)
        ema2 = pd.concat(
            [df.ewm(halflife=10, adjust=True).mean(), df.ewm(halflife=20, adjust=True).mean()],
            axis=1,
        )
        assert (ema1.values - ema2).abs().max().max() < 1e-10  # type: ignore[attr-defined]
