from typing import Any

import pandas as pd


class Compare:
    @staticmethod
    def get_columnDtypeNeqDict_ofOverlapFields(baseDf: pd.DataFrame, compDf: pd.DataFrame) -> dict:
        """Compare dtypes offields

        Returns dict with dtypes that are not equal

        Only overlaped fields are considered.
        """
        baseSet = set(baseDf.columns)
        compSet = set(compDf.columns)
        commonSet = baseSet & compSet
        columnDtypeNeqDict = {}
        for field in commonSet:
            baseSr = baseDf[field]
            compSr = compDf[field]
            if baseSr.dtype != compSr.dtype:
                columnDtypeNeqDict[field] = (baseSr.dtype, compSr.dtype)
        return columnDtypeNeqDict

    @classmethod
    def get_rowPrimary_intersectProportionInUnion(cls, mergeSideCountSr: pd.Series) -> float:
        return mergeSideCountSr.get('both', 0) / mergeSideCountSr.sum()

    @classmethod
    def get_rowPrimary_sideProportionInUnion(cls, mergeSideCountSr: pd.Series) -> dict[str, float]:
        """count(row in single df) / count(union(row in dfs))

        result dict. Example:
            {'base': 0.375, 'comp': 0.75}
        """
        return {
            'base': (mergeSideCountSr.get('left_only', 0) + mergeSideCountSr.get('both', 0))
            / mergeSideCountSr.sum(),
            'comp': (mergeSideCountSr.get('right_only', 0) + mergeSideCountSr.get('both', 0))
            / mergeSideCountSr.sum(),
        }

    @staticmethod
    def get_columnName_compareCategoryStr(baseDf: pd.DataFrame, compDf: pd.DataFrame) -> str:
        """Returns the category of columns comparison

        result in ['MATCH', 'ZERO', 'SUBSET', 'OVERLAP']
        """

        assert isinstance(baseDf, pd.DataFrame)
        assert isinstance(compDf, pd.DataFrame)

        baseSet = set(baseDf.columns)
        compSet = set(compDf.columns)
        if baseSet == compSet:
            return 'MATCH'

        elif not (baseSet & compSet):
            return 'ZERO'

        elif (baseSet <= compSet) or (baseSet >= compSet):
            return 'SUBSET'

        elif baseSet & compSet:
            return 'OVERLAP'

        else:
            raise NotImplementedError

    @classmethod
    def get_rowPrimary_compareCategoryStr(cls, mergeSideCountSr: pd.Series) -> str:
        """Returns the category of rows comparison

        result in ['MATCH', 'ZERO', 'SUBSET', 'OVERLAP']
        """
        _eqBothSr = mergeSideCountSr.eq('both')
        if _eqBothSr.all():
            return 'MATCH'

        elif not _eqBothSr.any():
            return 'ZERO'

        elif not {'left_only', 'right_only'} <= set(mergeSideCountSr.unique()):
            return 'SUBSET'

        elif _eqBothSr.any():
            return 'OVERLAP'

        else:
            raise NotImplementedError

    @staticmethod
    def get_mergeSideCountSr(
        baseDf: pd.DataFrame, compDf: pd.DataFrame, primaryColumns: list[Any]
    ) -> pd.Series:
        """Return count of rows in merged df by  source side.

        Example of results:
        right_only    30
        left_only     12
        both           6
        """

        assert isinstance(primaryColumns, list)
        baseDf = baseDf[primaryColumns]
        compDf = compDf[primaryColumns]

        assert baseDf.shape[1] == compDf.shape[1] == len(primaryColumns)
        assert not baseDf.duplicated().any()
        assert not compDf.duplicated().any()

        rowPrimaryMergeDf = pd.merge(baseDf, compDf, how='outer', on=primaryColumns, indicator=True)
        mergeSideCountSr = rowPrimaryMergeDf['_merge'].value_counts()

        return mergeSideCountSr
