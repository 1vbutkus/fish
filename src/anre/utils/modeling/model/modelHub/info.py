from dataclasses import dataclass
from typing import Collection

from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.modeling.model.info import Info as InfoBase

classId: str = 'ModelHub'


@dataclass_validate
@dataclass(frozen=True, repr=False)
class Info(InfoBase):
    version: str
    classId: str
    className: str
    name: str
    attrs: dict
    subModelKeys: Collection[str]

    @staticmethod
    def get_expectedClassId() -> str:
        return classId
