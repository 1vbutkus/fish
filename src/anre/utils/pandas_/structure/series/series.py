# mypy: disable-error-code="union-attr"
from collections import Counter

import pandas as pd

from anre.utils.pandas_.structure.column.column import Column
from anre.utils.pandas_.structure.index.index import Index
from anre.utils.prettyprint.prettyprint import PrettyPrint


class Series:
    def __init__(self, name: str, indexes: list[Index], column: Column) -> None:
        self._name = name
        self._indexes = indexes
        self._column = column

        assert not (
            duplicateIndexes := [
                name
                for name, count in Counter([x.get_name() for x in self._indexes]).items()
                if count > 1
            ]
        ), f"{duplicateIndexes=} in '{name}' series definition"

    def get_name(self) -> str:
        return self._name

    def get_indexes(self) -> list[Index]:
        return self._indexes

    def get_column(self) -> Column:
        return self._column

    def get_emptyPandasSeries(self) -> pd.Series:
        index = Index.Many.get_pandasIndexOrMultiIndex(indexes=self.get_indexes())
        pandasSeries = self.get_column().get_emptyPandasSeries(index=index)
        return pandasSeries

    def get_validatedPandasSeries(
        self, sr: pd.Series, setColumnType: bool = True, skipValidation: bool = False
    ) -> pd.Series:
        if len(sr.index) == 0:
            return self.get_emptyPandasSeries()

        if setColumnType:
            sr = self.set_pandasSeriesColumnType(sr=sr)

        if not skipValidation:
            failures = self.get_constraintFailures(sr=sr)
            assert not failures, PrettyPrint.get_listStr(failures)

        return sr

    def set_pandasSeriesColumnType(self, sr: pd.Series) -> pd.Series:
        sr = sr.copy()
        sr = self.get_column().get_updatedTypePandasSeries(sr=sr)
        return sr

    def get_constraintFailures(self, sr: pd.Series) -> list[str]:
        failures = Index.Many.get_constraintFailures(
            expectedIndexes=self.get_indexes(),
            pandasIndex=sr.index,
        )

        if (actColName := sr.name) != (expColName := self.get_column().get_name()):
            failures.append(f"expected column name: {expColName}, actual column name: {actColName}")
        else:
            failures += self.get_column().get_constraintFailures(sr)

        return [f"structure error found in series '{self.get_name()}': {f}" for f in failures]
