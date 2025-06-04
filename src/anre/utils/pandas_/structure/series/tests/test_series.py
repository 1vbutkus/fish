import anre.utils.pandas_.structure.column.type as ct
import anre.utils.pandas_.structure.index.type as it
from anre.utils import testutil
from anre.utils.pandas_.structure.column.column import Column
from anre.utils.pandas_.structure.index.index import Index
from anre.utils.pandas_.structure.series.series import Series


class TestSeries(testutil.TestCase):
    allIndexes: list[Index]
    allColumns: list[Column]
    seriesList: list[Series]

    def test_get_emptySeries_allIndexes_forAllColumns(self) -> None:
        allIndexes = [
            Index(name=str(type.__name__) + '_index', type=type()) for type in it.all_type_classes
        ]
        allColumns = [Column(name=str(type.__name__), type=type()) for type in ct.all_type_classes]

        seriesList = [
            Series(name=column.get_name(), indexes=allIndexes, column=column)
            for column in allColumns
        ]

        for series in seriesList:
            sr = series.get_emptyPandasSeries()

            # comparing lists of indexes directly does not work so do it in a loop
            expIndexes = [x.get_emptyPandasIndex() for x in allIndexes]
            actIndexes = list(sr.index.levels)  # type: ignore[attr-defined]
            self.assertEqual(len(expIndexes), len(actIndexes))
            for level, (expIndex, actIndex) in enumerate(zip(expIndexes, actIndexes)):
                self.assertTrue(
                    expIndex.equals(actIndex),
                    f'level    : {level}\nexpected : {expIndex}\nactual   : {actIndex}',
                )

            self.assertEqual(series.get_name(), sr.name)
