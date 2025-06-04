import numpy as np
import pandas as pd
from sklearn.model_selection import KFold


class Sampler:
    @staticmethod
    def ensureSize(df: pd.DataFrame, size: int, seed=None) -> pd.DataFrame:
        assert not df.empty
        assert size > 0

        if df.shape[0] >= size:
            resDf = df.sample(size, replace=False, random_state=seed)
        else:
            size_extra = size - df.shape[0]
            resDf = pd.concat(
                [
                    df,
                    df.sample(size_extra, replace=True, random_state=seed),
                ],
                axis=0,
            )

        assert resDf.shape[0] == size
        return resDf

    @staticmethod
    def sampleNumpy(X, size, replace: bool = False):
        assert X.shape[0]
        return X[np.random.choice(X.shape[0], size, replace=replace)]

    @classmethod
    def sampleNumpyOrPandas(cls, X, size, replace: bool = False):
        if isinstance(X, (pd.Series, pd.DataFrame)):
            return X.sample(n=size, replace=replace)
        elif isinstance(X, np.ndarray):
            return cls.sampleNumpy(X=X, size=size, replace=replace)
        else:
            raise ValueError

    @staticmethod
    def strataSample(df: pd.DataFrame, strataFields: list[str], sizeInStrata: int = 1, seed=None):
        assert set(strataFields) <= set(df.columns)
        return df.sample(frac=1.0, random_state=seed).groupby(strataFields).head(sizeInStrata)

    @staticmethod
    def strataSample_singleInStrata(df: pd.DataFrame, strataFields: list[str], seed=None):
        assert set(strataFields) <= set(df.columns)
        tempSortField = '_sortFieldForThisFunction_oiasjd78324kjnasd'
        assert tempSortField not in strataFields

        _fields = strataFields
        sdf = df[_fields].copy()

        randomState = np.random.RandomState(seed=seed)
        sdf[tempSortField] = randomState.random_sample(sdf.shape[0])
        _sampleDf = sdf.sort_values(tempSortField).drop_duplicates(_fields, keep='first')
        sampleDf = df.loc[_sampleDf.index].copy()
        return sampleDf

    @classmethod
    def sample_one_per_strata(cls, value_sr: pd.Series, strata_sr: pd.Series, seed=None):
        assert value_sr.index.equals(strata_sr.index)
        tdf = pd.concat({'value': value_sr, 'strata': strata_sr}, axis=1)
        tdf['rand'] = np.random.RandomState(seed=seed).random_sample(tdf.shape[0])
        _sampleDf = tdf.sort_values('rand').drop_duplicates('strata', keep='first')
        smpl_sr = _sampleDf['value'].copy()
        smpl_sr.name = value_sr.name
        return smpl_sr

    @staticmethod
    def balance_under_sampling(
        df: pd.DataFrame, strata_field: str | pd.Series, smpl_size=None, replace: bool = False
    ):
        if isinstance(strata_field, str):
            strata_sr = df[strata_field]
        elif isinstance(strata_field, pd.Series):
            strata_sr = strata_field
        else:
            raise ValueError
        assert isinstance(strata_sr, pd.Series)
        assert strata_sr.index.equals(df.index)

        value_counts = strata_sr.value_counts()
        if smpl_size is None:
            smpl_size = value_counts.min() * len(value_counts)

        _sampleSize = smpl_size // len(value_counts)
        if not replace:
            assert _sampleSize <= value_counts.min(), 'Sample size is too big. Use replace=True'

        _sdfList = []
        for val, counts in value_counts.items():
            ind = strata_sr == val
            sdf = df.loc[ind.values].sample(_sampleSize, replace=replace)  # type: ignore[index]
            _sdfList.append(sdf)
        res_df = pd.concat(_sdfList)
        res_df.sort_index(inplace=True)
        return res_df

    @staticmethod
    def balanceDf_oversampling(df, field, smplSize=None):
        valueCounts = df[field].value_counts()
        if smplSize is None:
            smplSize = valueCounts.max() * len(valueCounts)

        _sampleSize = smplSize // len(valueCounts)

        _sdfList = []
        for val, counts in valueCounts.items():
            ind = df[field] == val
            sdf = df.loc[ind].sample(_sampleSize, replace=True)
            _sdfList.append(sdf)
        resDf = pd.concat(_sdfList)
        resDf.sort_index(inplace=True)
        return resDf

    @staticmethod
    def get_splitCvGnr(sr: pd.Series, nSplits: int, shuffle: bool = False, seed=None):
        cv = KFold(n_splits=nSplits, shuffle=shuffle, random_state=seed)
        cvSplit = cv.split(sr)
        # train_index, test_index in next(cvSplit):
        for train_index, test_index in cvSplit:
            sr_train, sr_test = sr.iloc[train_index], sr.iloc[test_index]
            assert not set(sr_train) & set(sr_test)
            yield sr_train, sr_test

    ################################################################################################################################################################################

    @classmethod
    def _get_strataBins(cls, strataRangeArgs, rangeStart: float = 0.0):
        startSegment = rangeStart
        segmentList = []
        for rangeSegment, stepInRange in strataRangeArgs:
            _segment = cls._get_stepsSegments(startSegment, rangeSegment, stepInRange)
            assert len(_segment) > 0
            segmentList.append(_segment)
            startSegment = _segment[-1] + stepInRange

        sampleStrata = list(np.concatenate(segmentList))
        return sampleStrata

    @staticmethod
    def _get_stepsSegments(startSegment, rangeSegment, stepInRange):
        assert stepInRange > 0
        assert rangeSegment >= stepInRange
        stopSegment = startSegment + rangeSegment
        return np.arange(startSegment, stopSegment, stepInRange)
