import os
from dataclasses import dataclass

from anre.utils.dataStructure.info import InfoBase

infoFileName: str = 'modelInfo.json'


@dataclass(frozen=True, repr=False)
class Info(InfoBase):
    version: str
    classId: str
    className: str
    name: str
    attrs: dict

    @staticmethod
    def get_infoFileName() -> str:
        return infoFileName

    @classmethod
    def load_infoDict(cls, dirPath: str) -> dict:
        filePath = os.path.join(dirPath, cls.get_infoFileName())
        return cls._load_infoDict_fromFile(filePath=filePath)

    @staticmethod
    def get_expectedClassId() -> str:
        raise NotImplementedError
