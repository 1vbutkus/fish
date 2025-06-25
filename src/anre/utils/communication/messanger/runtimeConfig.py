from dataclasses import dataclass

from dataclass_type_validator import dataclass_validate


@dataclass_validate
@dataclass(frozen=False)
class RuntimeConfig:
    quiet: bool = False
    collectMessages: bool = False
    alarmLevel: int = 30
    popLevel: int = 40
