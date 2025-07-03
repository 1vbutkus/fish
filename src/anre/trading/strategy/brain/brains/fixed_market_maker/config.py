from dataclasses import dataclass

from dataclass_type_validator import dataclass_validate

from anre.trading.strategy.brain.brains.base.configBase import StrategyConfigBase


@dataclass_validate
@dataclass(repr=False, frozen=True, kw_only=True)
class Config(StrategyConfigBase):
    pass
