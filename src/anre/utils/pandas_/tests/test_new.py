import pandas as pd

from anre.utils import pandas_ as pdu
from anre.utils import testutil


class TestEval(testutil.TestCase):
    def test_get_expandGridDf(self) -> None:
        expandGridDf = pdu.new.get_expandGridDf({'A': [1, 2, 3], 'B': ['a', 'b']})
        assert isinstance(expandGridDf, pd.DataFrame)
        assert expandGridDf.shape == (6, 2)

    def test_get_randomDf(self) -> None:
        df = pdu.new.get_randomDf(shape=(6, 2))
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (6, 2)

    def test_get_regressionDf(self) -> None:
        df = pdu.new.get_regressionDf()
        assert isinstance(df, pd.DataFrame)
