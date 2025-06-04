from dataclasses import dataclass
from typing import Any

from anre.utils.dataclass_type_validator import dataclass_validate


@dataclass_validate
@dataclass(frozen=False)
class SafeWrapResult:
    success: bool
    result: Any
    takesTimeSec: float
    errorStr: str
    tracebackStr: str
