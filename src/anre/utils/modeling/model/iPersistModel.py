from __future__ import annotations

import abc

from anre.utils.modeling.model.info import Info


class IPersistModel(abc.ABC):
    classId: str
    name: str

    @abc.abstractmethod
    def get_info(self) -> Info: ...

    @abc.abstractmethod
    def save(self, dirPath: str, overwrite: bool = False) -> None: ...

    @classmethod
    @abc.abstractmethod
    def load(cls, dirPath: str) -> IPersistModel: ...
