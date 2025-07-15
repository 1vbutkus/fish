from dataclasses import dataclass
from typing import Optional

from dataclass_type_validator import dataclass_validate

from anre.trading.strategy.brain.brains.base.configBase import StrategyConfigBase


@dataclass_validate
@dataclass(repr=False, frozen=True, kw_only=True)
class Config(StrategyConfigBase):
    target_base_step_level: int = 1  # kiek giliai nerti i knyga. 0 tai stotis i jau esant top leveli, >0, tai nerti i knyga. -n tai buti front runneriu per n zingsniu.
    target_skew_step_level: int = 0  # asimetrija. jei >0, tai prie LONG pridesim papildomu zingsniu. Jei -n, tai SHORT sumazinsime per n zingsniu
    keep_offset_shallow_level: int = 0  # tolerancija, kuriam intervale toleruoti jau egzistuojancio orderio nuokrypi nuo dabartinio targeto
    keep_offset_deep_level: int = 0
    share_size = 10
    step1000: Optional[int] = None   # jei None, tai bus tick size
    place_patience: int = 1

    def __post_init__(self):
        assert self.keep_offset_shallow_level >= 0, f'keep_offset_shallow_level must be >= 0, got: {self.keep_offset_shallow_level}'
        assert self.keep_offset_deep_level >= 0, f'keep_offset_deep_level must be >= 0, got: {self.keep_offset_deep_level}'
        assert self.step1000 is None or 0 < self.step1000 <= 10, f'step1000 must be None or 0 < step1000 <= 10, got: {self.step1000}'
        assert self.share_size >= 1, f'risk_size must be >= 1, got: {self.share_size}'
        assert self.place_patience >= 0, f'place_patience must be >= 0, got: {self.place_patience}'

