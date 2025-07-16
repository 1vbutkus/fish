from abc import ABC, abstractmethod
from typing import Optional


class BaseMonitor(ABC):

    @abstractmethod
    def iteration(self, gtt=2):
        pass

    @abstractmethod
    def assert_up_to_date(self, gtt: Optional[int | float] = None):
        pass
