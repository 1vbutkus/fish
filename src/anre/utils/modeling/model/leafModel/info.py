from dataclasses import dataclass
from typing import Sequence

from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.modeling.model.info import Info as InfoBase

classId: str = 'LeafModel'


@dataclass_validate
@dataclass(frozen=True, repr=False)
class Info(InfoBase):
    version: str
    classId: str
    className: str
    name: str
    attrs: dict

    xFields: Sequence[str | int]

    @staticmethod
    def get_expectedClassId() -> str:
        return classId
