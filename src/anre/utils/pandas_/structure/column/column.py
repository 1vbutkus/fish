# mypy: disable-error-code="has-type,misc,override"
from __future__ import annotations

import pandas as pd

from anre.utils.pandas_.structure.column.type import IType
from anre.utils.pandas_.structure.constraint.constraint import IConstraint


class Column:
    def __init__(
        self,
        name: str | tuple,
        type: IType,
        constraints: list[IConstraint] | None = None,
    ):
        self._name = name
        self._type = type
        self._constraints = constraints if constraints else []

    def get_name(self) -> str:
        return self._name  # type: ignore[return-value]

    def get_type(self) -> IType:
        return self._type

    def get_constraints(self) -> list[IConstraint]:
        return self._constraints

    def set_relaxConstraint(self, constraint: IConstraint) -> Column:
        assert any(x == constraint for x in self.get_constraints())
        constraints = [x for x in self.get_constraints() if not x == constraint]
        return Column(name=self.get_name(), type=self.get_type(), constraints=constraints)

    def get_emptyPandasSeries(self, index: pd.Index) -> pd.Series:
        sr = pd.Series(index=index, name=self._name, dtype=object)
        return self._type.to_type(sr=sr)

    def get_updatedTypePandasSeries(self, sr: pd.Series) -> pd.Series:
        return self._type.to_type(sr=sr)

    def get_constraintFailures(self, sr: pd.Series) -> list[str]:
        # we always check type constraints first
        # other constrains might not make sense on a wrong type
        typeFailures = self._get_typeConstraintFailures(sr=sr)
        if typeFailures:
            return typeFailures

        return [c.get_error_message(sr) for c in self._constraints if not c.check(sr)]

    def _get_typeConstraintFailures(self, sr: pd.Series) -> list[str]:
        failures = []
        if not self._type.is_type(sr=sr):
            failures.append(
                f"column '{self._name}' type should be '{self._type.get_name()}' but was '{str(sr.dtype)}'"
            )

        return failures

    def __eq__(self, other: Column) -> bool:
        return self.get_name() == other.get_name() and self.get_type() == other.get_type()
