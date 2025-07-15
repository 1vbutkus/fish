from dataclasses import dataclass
from typing import Dict

from dataclass_type_validator import dataclass_validate

from anre.utils.dataStructure.general import GeneralBaseFrozen


@dataclass_validate
@dataclass(frozen=True, repr=False, kw_only=True)
class StrategyBrainCred(GeneralBaseFrozen):
    className: str
    version: str
    strategyLabel: str
    configDict: Dict
    tagDict: Dict[str, str]
    comment: str
