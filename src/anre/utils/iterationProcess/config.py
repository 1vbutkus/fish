from dataclasses import dataclass, field
from typing import List

from anre.utils.dataclass_type_validator import dataclass_validate
from anre.utils.dataStructure.general import GeneralBaseFrozen


@dataclass_validate
@dataclass(frozen=True, repr=False)
class Config(GeneralBaseFrozen):
    wait: int | float = 10
    sleepInFailList: List[float | int] = field(default_factory=lambda: [0.5, 1, 5])
    tryForever: bool = False

    def __post_init__(self):
        assert self.wait >= 0, f'Wait must be not negative, got: {self.wait}'
        assert all([el >= 0 for el in self.sleepInFailList]), (
            f'sleepInFail must be not negative, got: {self.sleepInFailList}'
        )
        if self.tryForever:
            assert self.sleepInFailList, 'if tryForever, then sleepInFailList must not be empty'
