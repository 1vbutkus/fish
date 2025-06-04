import pandas as pd

from anre.utils import pandas_ as pdu
from anre.utils import testutil
from anre.utils.indicator.ema.emaSingle import EmaSingle


class TestEmaSingle(testutil.TestCase):
    def test_get_expandGridDf(self) -> None:
        df = pdu.new.get_randomDf(shape=(7, 3))
        df.loc[4, 'x0'] = pd.NA
        df.loc[4, 'x1'] = pd.NA
        df.loc[5, 'x1'] = pd.NA

        emaSingle = EmaSingle(halflife=10, adjust=True)
        ema1 = df.apply(emaSingle.updateReturn, axis=1)
        ema2 = df.ewm(halflife=10, adjust=True).mean()
        assert (ema1 - ema2).abs().max().max() < 1e-10

        emaSingle = EmaSingle(halflife=10, adjust=False)
        ema1 = df.apply(emaSingle.updateReturn, axis=1)
        ema2 = df.ewm(halflife=10, adjust=False).mean()
        assert (ema1 - ema2).abs().max().max() < 1e-10
