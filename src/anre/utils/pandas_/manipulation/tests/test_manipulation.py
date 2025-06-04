import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.pandas_.manipulation.manipulation import Manipulation


class TestEval(testutil.TestCase):
    def test_lookup(self) -> None:
        df = pd.DataFrame({'A': range(1, 6), 'B': range(10, 0, -2)})

        rowIdx = [0, 2, 4, 10]
        colIdx = ['A', 'A', 'B', 'C']

        actSr = Manipulation.lookup_byIndex(df=df, rowIdx=rowIdx, colIdx=colIdx)
        expSr = pd.Series([1.0, 3.0, 2.0, np.nan], index=[(0, 'A'), (2, 'A'), (4, 'B'), (10, 'C')])
        self.assertTrue(actSr.equals(expSr))

        colIdx = ['A', 'A', 'B', 'C', 'B']
        actSr = Manipulation.columnLookup_byIndex(df=df, colIdx=colIdx)
        expSr = pd.Series(
            [1.0, 2.0, 6.0, np.nan, 2.0], index=[(0, 'A'), (1, 'A'), (2, 'B'), (3, 'C'), (4, 'B')]
        )
        self.assertTrue(actSr.equals(expSr))

    def test_addIndexLevel(self) -> None:
        df = pd.DataFrame(index=list('abc'), data={'A': range(3), 'B': range(3)})
        df.columns = Manipulation.add_indexLevel(df.columns, value='C')
        df.columns = Manipulation.add_indexLevel(df.columns, value='D', name='D-name')
        df.columns = Manipulation.add_indexLevel(df.columns, value='E2', n=2)
        df.columns = Manipulation.add_indexLevel(df.columns, value='Top', name='OnTop', onTop=True)
        df.columns = Manipulation.add_indexLevel(df.columns, value=1, name='Number')

        columns = pd.MultiIndex.from_tuples(
            [('Top', 'A', 'C', 'D', 'E2', 'E2', '1'), ('Top', 'B', 'C', 'D', 'E2', 'E2', '1')],
            names=['OnTop', None, None, 'D-name', None, None, 'Number'],
        )
        assert df.columns.equals(columns)

    def test_get_lagDf(self) -> None:
        xSr = pd.Series(range(8), index=list('ABCDEFGH'))
        lagDf = Manipulation.get_lagDf(xSr=xSr)
        assert isinstance(lagDf, pd.DataFrame)
        assert lagDf.index.equals(xSr.index)
