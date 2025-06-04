# mypy: disable-error-code="union-attr"
from collections import Counter

import pandas as pd

from anre.utils.pandas_.structure.column.column import Column
from anre.utils.pandas_.structure.index.index import Index
from anre.utils.prettyprint.prettyprint import PrettyPrint


class DataFrame:
    def __init__(
        self,
        name: str,
        indexes: list[Index],
        columns: list[Column],
        optionalColumns: list[Column] | None = None,
        allowUndefinedColumns: bool = False,
    ):
        self._name = name
        self._indexes = indexes
        self._columns = columns
        self._optionalColumns = optionalColumns if optionalColumns else []
        self._allowUndefinedColumns = allowUndefinedColumns

        assert len(self._columns) > 0 or allowUndefinedColumns, (
            f"no columns specified in '{name}' dataframe definition"
        )

        assert not (
            duplicateIndexes := [
                name
                for name, count in Counter([x.get_name() for x in self._indexes]).items()
                if count > 1
            ]
        ), f"{duplicateIndexes=} in '{name}' dataframe definition"

        assert not (
            duplicateColumns := [
                name
                for name, count in Counter([x.get_name() for x in self._columns]).items()
                if count > 1
            ]
        ), f"{duplicateColumns=} in '{name}' dataframe definition"

        assert not (
            duplicateOptionalColumns := [
                name
                for name, count in Counter([x.get_name() for x in self._optionalColumns]).items()
                if count > 1
            ]
        ), f"{duplicateOptionalColumns=} in '{name}' dataframe definition"

    def get_name(self) -> str:
        return self._name

    def get_indexes(self) -> list[Index]:
        return self._indexes

    def get_columns(self) -> list[Column]:
        return self._columns

    def get_optionalColumns(self) -> list[Column]:
        return self._optionalColumns

    def get_allowUndefinedColumns(self) -> bool:
        return self._allowUndefinedColumns

    def get_emptyPandasDataFrame(self, includeOptionalColumns: bool = True) -> pd.DataFrame:
        pandasIndex = Index.Many.get_pandasIndexOrMultiIndex(indexes=self.get_indexes())
        columns = (
            self.get_columns()
            if not includeOptionalColumns
            else self.get_columns() + self.get_optionalColumns()
        )
        pandasSeries = [column.get_emptyPandasSeries(index=pandasIndex) for column in columns]
        return pd.concat(pandasSeries, axis=1)

    def get_validatedPandasDataFrame(
        self, df: pd.DataFrame, setColumnTypes: bool = True, skipValidation: bool = False
    ) -> pd.DataFrame:
        if len(df.index) == 0:
            return self.get_emptyPandasDataFrame()

        if setColumnTypes:
            df = self.set_pandasDataFrameColumnTypes(df=df)

        if not skipValidation:
            failures = self.get_constraintFailures(df=df)
            assert not failures, PrettyPrint.get_listStr(failures)

        return df

    def set_pandasDataFrameColumnTypes(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        columnDict = {x.get_name(): x for x in self.get_columns() + self.get_optionalColumns()}
        for pandasColumnName in df.columns:
            if pandasColumnName in columnDict:
                column = columnDict[pandasColumnName]
                df[pandasColumnName] = column.get_updatedTypePandasSeries(df[pandasColumnName])
            elif self.get_allowUndefinedColumns():
                continue
            else:
                raise KeyError(
                    f'column \'{pandasColumnName}\' not found in  \'{self.get_name()}\' dataframe structure'
                )

        return df

    def get_constraintFailures(self, df: pd.DataFrame) -> list[str]:
        failures = Index.Many.get_constraintFailures(
            expectedIndexes=self.get_indexes(),
            pandasIndex=df.index,
        )

        mandatoryColNameSet = set([x.get_name() for x in self.get_columns()])
        optionalColNameSet = set([x.get_name() for x in self.get_optionalColumns()])
        actualColNameSet = set(df.columns)

        if missingColNameSet := mandatoryColNameSet - optionalColNameSet - actualColNameSet:
            failures.append(f"missing columns: {sorted(missingColNameSet)}")

        if (
            undefinedColNameSet := actualColNameSet - mandatoryColNameSet.union(optionalColNameSet)
        ) and not self.get_allowUndefinedColumns():
            failures.append(f"unexpected columns found: {sorted(undefinedColNameSet)}")

        for column in self.get_columns() + self.get_optionalColumns():
            # Here we're skipping mandatory column validation if they are not found because we want to collect all
            # failures before raising an error. The error that the mandatory column is missing is going to be recorded
            # by the code above.
            if column.get_name() not in df.columns:
                continue

            failures += column.get_constraintFailures(df[column.get_name()])

        return [f"structure error found in dataframe '{self.get_name()}': {f}" for f in failures]
