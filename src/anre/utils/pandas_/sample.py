import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, ShuffleSplit, train_test_split


def split_trainTest(
    df: pd.DataFrame,
    groups: pd.Series | np.ndarray | None = None,
    useShuffleSplit: bool = False,
    seed=None,
    **kwargs,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if groups is not None:
        assert isinstance(groups, (pd.Series, np.ndarray))
        if isinstance(groups, np.ndarray):
            groups = pd.Series(groups, index=df.index)
        assert groups.index.equals(df.index)

    if useShuffleSplit:
        if groups is not None:
            splitter = GroupShuffleSplit(random_state=seed, **kwargs)
            split = splitter.split(df.index, groups=groups)
            _trainInx, _testInx = next(split)
            trainDf = df.iloc[_trainInx]
            testDf = df.iloc[_testInx]

        else:
            splitter = ShuffleSplit(random_state=seed, **kwargs)
            split = splitter.split(df.index)
            _trainInx, _testInx = next(split)
            trainDf = df.iloc[_trainInx]
            testDf = df.iloc[_testInx]

    else:
        if groups is not None:
            groupsUnique = groups.unique()
            trainGr, testGr = train_test_split(groupsUnique, random_state=seed, **kwargs)
            ind = groups.isin(trainGr)
            trainDf = df.loc[ind]
            ind = groups.isin(testGr)
            testDf = df.loc[ind]

        else:
            _trainInx, _testInx = train_test_split(df.index, random_state=seed, **kwargs)
            trainDf = df.loc[_trainInx]
            testDf = df.loc[_testInx]

    return trainDf, testDf
