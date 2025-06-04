import itertools

import numpy as np
import pandas as pd


def get_expandGridDf(dataDict: dict) -> pd.DataFrame:
    rows = itertools.product(*dataDict.values())
    return pd.DataFrame.from_records(rows, columns=dataDict.keys())


def get_randomDf(shape: tuple = (10, 5), dtype=float, prefix: str = 'x', seed=None) -> pd.DataFrame:
    assert isinstance(shape, (tuple, list))
    assert isinstance(prefix, str)
    assert len(shape) == 2

    columns = [f"{prefix}{i}" for i in range(shape[-1])]
    if dtype is float:
        randomState = np.random.RandomState(seed=seed)
        return pd.DataFrame(randomState.randn(*shape), columns=columns, dtype=dtype)
    else:
        raise NotImplementedError


def get_regressionDf(n=100, intercept=0, coefs=(-1, 0, 1), scale=1, seed=None):
    shape = (n, len(coefs) + 1)
    regressionDf = get_randomDf(shape=shape, seed=seed)
    epsSr = regressionDf.iloc[:, -1] * scale
    regressionDf.drop(columns=[epsSr.name], inplace=True)
    regressionDf['y'] = (
        intercept
        + np.dot(np.array([coefs]), regressionDf.values.transpose()).reshape(-1)
        + epsSr.values
    )
    return regressionDf
