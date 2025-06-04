from dataclasses import dataclass

from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.modeling.model.modelHub.info import Info as InfoBase

classId: str = 'PartitionModel'


@dataclass_validate
@dataclass(frozen=True, repr=False)
class Info(InfoBase):
    @staticmethod
    def get_expectedClassId() -> str:
        return classId
