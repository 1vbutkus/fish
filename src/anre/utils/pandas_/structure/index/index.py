# mypy: disable-error-code="has-type,misc"
from __future__ import annotations

from typing import Sequence

import pandas as pd

from anre.utils.pandas_.structure.constraint.constraint import IConstraint
from anre.utils.pandas_.structure.index.type import IType


class Index:
    def __init__(
        self,
        name: str | None,
        type: IType,
        constraints: list[IConstraint] | None = None,
    ):
        assert name is None or name.endswith('_index')
        self._name = name
        self._type = type
        self._constraints = constraints if constraints else []

    def get_name(self) -> str | None:
        return self._name

    def get_type(self) -> IType:
        return self._type

    def get_constraints(self) -> list[IConstraint]:
        return self._constraints

    def get_emptyPandasIndex(self) -> pd.Index:
        # TODO: bug with _name being None
        return self._type.get_empty(indexName=self._name)  # type: ignore[arg-type]

    def get_constraintFailures(self, index: pd.Index) -> list[str]:
        # we always check type constraints first
        # other constrains might not make sense on a wrong type
        typeFailures = self._get_typeConstraintFailures(index=index)
        if typeFailures:
            return typeFailures

        return [c.get_error_message(index) for c in self._constraints if not c.check(index)]

    def _get_typeConstraintFailures(self, index: pd.Index) -> list[str]:
        failures = []

        if not self._type.is_type(index=index):
            failures.append(
                f"index '{self._name}' type should be '{str(self._type.get_name())}' but was '{str(index.dtype)}'"
            )

        return failures

    class Many:
        @classmethod
        def get_pandasIndexOrMultiIndex(cls, indexes: list[Index]) -> pd.Index:
            if len(indexes) == 1:
                pandasIndex = indexes[0].get_emptyPandasIndex()
            else:
                pandasIndex = pd.MultiIndex.from_arrays([
                    index.get_emptyPandasIndex() for index in indexes
                ])
            return pandasIndex

        @classmethod
        def get_constraintFailures(
            cls, expectedIndexes: Sequence[Index], pandasIndex: pd.Index
        ) -> list[str]:
            multiIndex = pandasIndex.nlevels > 1
            actualIndexNames = list(pandasIndex.names) if multiIndex else [pandasIndex.name]

            expectedIndexNames = [x.get_name() for x in expectedIndexes]
            expectedIndexNameAtLevels = list(enumerate(expectedIndexNames))
            actualIndexNameAtLevels = list(enumerate(actualIndexNames))

            # We ned to do this validation separately because if expected and actual index names are not matching
            # continuing other validations do not make sense as they are sensitive to both names and ordering.
            if expectedIndexNameAtLevels != actualIndexNameAtLevels:
                failure = f"Expected (level, index) list should be {expectedIndexNameAtLevels} but was {actualIndexNameAtLevels}"
                return [failure]

            failures = []
            for level, expectedIndex in enumerate(expectedIndexes):
                idx = pandasIndex.levels[level] if multiIndex else pandasIndex  # type: ignore[attr-defined]
                failures += expectedIndex.get_constraintFailures(idx)

            return failures
