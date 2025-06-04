import numpy as np
import pandas as pd

import anre.utils.pandas_.structure.column.type as ct
import anre.utils.pandas_.structure.index.type as it
from anre.utils import testutil
from anre.utils.pandas_.structure.column.column import Column
from anre.utils.pandas_.structure.constraint.constraint import ContainsOnly, Positive
from anre.utils.pandas_.structure.dataframe.dataframe import DataFrame
from anre.utils.pandas_.structure.index.index import Index


class TestDataFrame(testutil.TestCase):
    idx_None: Index
    idx_intIdx_positive_index: Index
    idx_intIdx_containOnly_index: Index
    col_strCol: Column
    col_intCol: Column
    col_intCol_positive: Column
    col_floatCol: Column

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.idx_None = Index(name=None, type=it.Range())
        cls.idx_intIdx_positive_index = Index(
            name='intIdx_positive_index', type=it.Int64(), constraints=[Positive()]
        )
        cls.idx_intIdx_containOnly_index = Index(
            name='intIdx_containOnly_index',
            type=it.Int64(),
            constraints=[ContainsOnly([1, 2, 3])],
        )

        cls.col_strCol = Column(name='strCol', type=ct.String())
        cls.col_intCol = Column(name='intCol', type=ct.Int64())
        cls.col_intCol_positive = Column(
            name='intCol_positive', type=ct.Int64(), constraints=[Positive()]
        )
        cls.col_floatCol = Column(name='floatCol', type=ct.Float64())

    def test_passingDuplicatedIndexesShouldRaise(self) -> None:
        with self.assertRaises(Exception):
            DataFrame(
                name='test',
                indexes=[self.idx_intIdx_positive_index, self.idx_intIdx_positive_index],
                columns=[self.col_strCol],
            )

    def test_passingDuplicatedColumnsShouldRaise(self) -> None:
        with self.assertRaises(Exception):
            DataFrame(
                name='test', indexes=[self.idx_None], columns=[self.col_strCol, self.col_strCol]
            )

    def test_get_emptyDataFrame(self) -> None:
        dataFrame = DataFrame(
            name='df', indexes=[self.idx_None], columns=[self.col_strCol, self.col_intCol]
        )
        df = dataFrame.get_emptyPandasDataFrame()
        self.assertEqual(type(df.index), pd.RangeIndex)
        self.assertEqual(['strCol', 'intCol'], list(df.columns))

    def test_get_emptyDataFrame_shouldIncludeOptionalColumns(self) -> None:
        dataFrame = DataFrame(
            name='df',
            indexes=[self.idx_None],
            columns=[self.col_strCol, self.col_intCol],
            optionalColumns=[self.col_floatCol],
        )
        df = dataFrame.get_emptyPandasDataFrame()
        self.assertEqual(type(df.index), pd.RangeIndex)
        self.assertEqual(['strCol', 'intCol', 'floatCol'], list(df.columns))

    def test_get_emptyDataFrame_withAllowedUndefinedColumns_shouldNotIncludeAnyUndefinedColumns(
        self,
    ):
        dataFrame = DataFrame(
            name='df',
            indexes=[self.idx_None],
            columns=[self.col_strCol, self.col_intCol],
            optionalColumns=[self.col_floatCol],
            allowUndefinedColumns=True,
        )
        df = dataFrame.get_emptyPandasDataFrame()
        self.assertEqual(type(df.index), pd.RangeIndex)
        self.assertEqual(['strCol', 'intCol', 'floatCol'], list(df.columns))

    def test_get_emptyDataFrame_allIndexesAndAllColumns(self) -> None:
        allIndexes = [
            Index(name=str(type.__name__) + '_index', type=type()) for type in it.all_type_classes
        ]
        allColumns = [Column(name=str(type.__name__), type=type()) for type in ct.all_type_classes]

        dataFrame = DataFrame(name='rainbow', indexes=allIndexes, columns=allColumns)
        rainbowDf = dataFrame.get_emptyPandasDataFrame()

        # comparing lists of indexes directly does not work so do it in a loop
        expIndexes = [x.get_emptyPandasIndex() for x in allIndexes]
        actIndexes = list(rainbowDf.index.levels)  # type: ignore[attr-defined]
        self.assertEqual(len(expIndexes), len(actIndexes))
        for level, (expIndex, actIndex) in enumerate(zip(expIndexes, actIndexes)):
            self.assertTrue(
                expIndex.equals(actIndex),
                f'level    : {level}\nexpected : {expIndex}\nactual   : {actIndex}',
            )

        self.assertListEqual([x.get_name() for x in allColumns], list(rainbowDf.columns))

    def test_get_dataFrameConstraintFailures_returnEmptyIfNoConstraintsViolated(self) -> None:
        dataFrame1 = DataFrame(
            name='df', indexes=[self.idx_None], columns=[self.col_strCol, self.col_intCol]
        )
        df1 = pd.DataFrame({'strCol': ['a', 'b', 'c'], 'intCol': [-1, 0, 1]})

        failures1 = dataFrame1.get_constraintFailures(df1)
        self.assertEqual(0, len(failures1), failures1)

        dataFrame2 = DataFrame(
            name='df', indexes=[self.idx_intIdx_containOnly_index], columns=[self.col_strCol]
        )
        df2 = pd.DataFrame(
            {'strCol': ['a', 'b', 'c']},
            index=pd.Index([1, 2, 3], name='intIdx_containOnly_index', dtype=np.int64),
        )
        failures2 = dataFrame2.get_constraintFailures(df2)
        self.assertEqual(0, len(failures2), failures2)

    def test_get_dataFrameConstraintFailures_returnNotEmptyIfConstraintsViolated_forColumn(
        self,
    ) -> None:
        dataFrame = DataFrame(
            name='df', indexes=[self.idx_None], columns=[self.col_strCol, self.col_intCol_positive]
        )
        df = pd.DataFrame({'strCol': ['a', 'b', 'c'], 'intCol_positive': [-1, 0, 1]})

        failures = dataFrame.get_constraintFailures(df)
        self.assertEqual(1, len(failures), failures)

    def test_get_dataFrameConstraintFailures_returnNotEmptyIfConstraintsViolated_forIndex(
        self,
    ) -> None:
        dataFrame = DataFrame(
            name='df', indexes=[self.idx_intIdx_positive_index], columns=[self.col_strCol]
        )
        df = pd.DataFrame(
            {'strCol': ['a', 'b', 'c']},
            index=pd.Index([-2, 0, 1], name='intIdx_positive_index', dtype=pd.Int64Dtype()),
        )
        failures = dataFrame.get_constraintFailures(df)
        self.assertEqual(1, len(failures), failures)

    def test_dtype(self) -> None:
        dataFrame = DataFrame(
            name='df', indexes=[self.idx_intIdx_positive_index], columns=[self.col_strCol]
        )
        df = pd.DataFrame(
            {'strCol': ['a', 'b', 'c']},
            index=pd.Index([-2, 0, 1], name='intIdx_positive_index', dtype=pd.Int64Dtype()),
        )
        failures = dataFrame.get_constraintFailures(df)
        self.assertEqual(1, len(failures), failures)
