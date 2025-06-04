from dataclasses import dataclass

from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.dataStructure.info import InfoBase


@dataclass_validate
@dataclass(frozen=True, repr=False)
class Info(InfoBase):
    classId: str
    className: str
    version: str
    isFitted: bool
    attrs: dict
