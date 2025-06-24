from dataclasses import dataclass

from anre.utils.dataStructure.general import GeneralBaseFrozen


@dataclass(repr=False, frozen=True, kw_only=True)
class StrategyConfigBase(GeneralBaseFrozen):
    pass
