# mypy: disable-error-code="call-arg,operator"
from dataclasses import dataclass
from typing import Literal

from anre.type import Type
from anre.utils.dataStructure.general import GeneralBaseMutable


@dataclass(repr=False, frozen=False)
class HyperParameter(GeneralBaseMutable):
    label: str
    type: Literal["float", "int", "str", "bool"]
    value: Type.BasicType
    step: Type.RealNumber | None = None
    softLims: tuple[Type.RealNumber, Type.RealNumber] | None = None
    hardLims: tuple[Type.RealNumber, Type.RealNumber] | None = None
    admissibleValues: tuple[Type.BasicType, ...] | None = None
    comment: str | None = None

    def __post_init__(self):
        self.validate()

    def validate(self):
        assert isinstance(self.label, str) and bool(self.label)
        assert isinstance(self.type, str) and self.type in ["float", "int", "str", "bool"]
        assert isinstance(self.value, Type.BasicType.__args__)

        if self.type == 'float':
            assert isinstance(self.value, (float, int))
            if self.step is not None:
                assert self.step > 0

        elif self.type == 'int':
            assert isinstance(self.value, int)
            if self.step is None:
                self.step = 1
            assert isinstance(self.step, int)
            assert self.step > 0

        elif self.type == 'str':
            assert isinstance(self.value, str)

        elif self.type == 'bool':
            assert isinstance(self.value, bool)

        else:
            raise NotImplementedError

        if self.hardLims is not None:
            self._validate_lims(lims=self.hardLims)

        if self.softLims is not None:
            self._validate_lims(lims=self.softLims)

        if self.admissibleValues is not None:
            assert isinstance(self.admissibleValues, tuple)
            assert self.value in self.admissibleValues, (
                f'Value({self.value}) must be in {self.admissibleValues}'
            )

    def _validate_lims(self, lims: tuple[Type.RealNumber, Type.RealNumber]):
        assert isinstance(lims, tuple), f'Argument {lims=} must be tuple, but got {type(lims)}'
        assert len(lims) == 2, f'Argument {lims=} must have length =2 , but got {len(lims)}'
        assert isinstance(lims[0], Type.RealNumber)
        assert isinstance(lims[1], Type.RealNumber)
        assert lims[0] <= lims[1]
        assert all([el is None or isinstance(el, Type.RealNumber.__args__)] for el in lims)
        assert lims[0] <= self.value <= lims[1], f'Value({self.value}) is not in range: {lims}'
