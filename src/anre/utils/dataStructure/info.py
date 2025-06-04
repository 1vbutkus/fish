# mypy: disable-error-code="call-arg,return"
"""Cia yra standartinis informacinis failas, kuris padada susiorentuoti, kai issaugom i objektai folderyje.

Standartiskai prasminguose folderio vienetuose turi buti info.json filas, kuris padada susiorentuoti i ka cia ziurim (tiek zmogui, tiek kompui)

"""

import ast
import os.path
from dataclasses import dataclass

from anre.utils.dataStructure.general import GeneralBaseFrozen
from anre.utils.Json.Json import Json

_infoFileName: str = 'info.json'


@dataclass(repr=False, frozen=True, kw_only=True)
class InfoBase(GeneralBaseFrozen):
    className: str  # the owner of the class that initiated the saving into the dir
    version: str  # those who saves data always should have versions as well

    @staticmethod
    def get_infoFileName() -> str:
        return _infoFileName

    def save(self, dirPath: str, overwrite: bool = False, useIndent: bool = True):
        _dict = self.to_dict()
        _dict_toSave = {key: value.__repr__() for key, value in _dict.items()}
        # test if this is convertable back
        try:
            _dict2 = {key: ast.literal_eval(value) for key, value in _dict_toSave.items()}
        except BaseException:
            raise AssertionError(
                f'dict is not convertable back to python object. It probably have not convertable elements: {_dict}'
            )
        assert _dict == _dict2, 'It seems that Info object has elements that can not be saved.'
        _filePath = os.path.join(dirPath, self.get_infoFileName())
        return Json.dump(obj=_dict_toSave, path=_filePath, overwrite=overwrite, useIndent=useIndent)

    @classmethod
    def load(cls, dirPath: str):
        _filePath = os.path.join(dirPath, cls.get_infoFileName())
        _dict = cls._load_infoDict_fromFile(filePath=_filePath)
        return cls.from_dict(_dict)

    @classmethod
    def load_infoDict(cls, dirPath: str) -> dict:
        """Si funkcija naudinga, kai negalime uzkrauti tiesiogiai info objekto (pvz versija nebeatitinka)"""
        _filePath = os.path.join(dirPath, cls.get_infoFileName())
        return cls._load_infoDict_fromFile(filePath=_filePath)

    @staticmethod
    def check_ifDictIsConvertable(dataDict: dict) -> bool:
        _dict_toSave = {key: value.__repr__() for key, value in dataDict.items()}
        # test if this is convertable back
        try:
            _d_alt = {key: ast.literal_eval(value) for key, value in _dict_toSave.items()}
        except BaseException:
            return False
        return dataDict == _d_alt

    @classmethod
    def get_className_safe(cls, dirPath: str) -> str | None:
        """Saugiai gaunam className arba None, jei nepavyksta padoriai gauti"""
        try:
            infoDict = cls.load_infoDict(dirPath)
            className = infoDict['className']
            return className
        except BaseException:
            pass

    @classmethod
    def _load_infoDict_fromFile(cls, filePath: str) -> dict:
        _dict = Json.load(path=filePath)
        infoDict = {key: ast.literal_eval(value) for key, value in _dict.items()}
        infoDict = cls._convert_toLatestVersion(infoDict)
        return infoDict

    @staticmethod
    def _convert_toLatestVersion(infoDict: dict) -> dict:
        return infoDict
