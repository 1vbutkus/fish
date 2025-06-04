from dataclasses import dataclass

from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.modeling.model.info import Info as InfoBase


@dataclass_validate
@dataclass(frozen=True, repr=False)
class Info(InfoBase):
    version: str
    classId: str
    className: str
    name: str
    attrs: dict

    isRegression: bool
    isClassification: bool
    isFitted: bool
    input_shape: tuple[int | None, ...]
    output_shape: tuple[int | None, ...]

    @staticmethod
    def get_expectedClassId() -> str:
        raise NotImplementedError
