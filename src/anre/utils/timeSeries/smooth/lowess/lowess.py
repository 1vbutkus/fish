import numpy as np
import pandas as pd
from statsmodels.nonparametric.smoothers_lowess import lowess as _lowess


class Lowess:
    @staticmethod
    def get_lowessSr(y, x=None, frac=0.85, breaks=None):
        """Upgraded lowess function that allows breaks

        Returns DF
        """

        if x is None:
            assert isinstance(y, pd.Series), (
                'If x is missing, then y must be pd.Series with meaningfull index'
            )
            x = y.index.values

        if breaks is None:
            lowessDf = pd.DataFrame(_lowess(y, x, frac=frac), columns=['x', 'y'])
            lowessSr = lowessDf.set_index('x')['y']
        else:
            pDf = pd.DataFrame({'y': y, 'x': x})

            bins = np.array([min(pDf['x']) - 1] + breaks + [max(pDf['x']) + 1])
            bins.sort()
            pDf['cutF'] = pd.cut(pDf['x'], bins)

            lowessDf = pDf.groupby('cutF', observed=False)[['x', 'y']].apply(
                lambda df: pd.DataFrame(_lowess(df['y'], df['x'], frac=frac), columns=['x', 'y'])
            )
            lowessDf.reset_index(drop=True, inplace=True)
            lowessDf.sort_values('x', inplace=True)
            lowessSr = lowessDf.set_index('x')['y']
        return lowessSr
