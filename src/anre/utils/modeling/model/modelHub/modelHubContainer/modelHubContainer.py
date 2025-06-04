import os
import os.path
from typing import Any

from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.modelHub.modelHub import ModelHub
from anre.utils.modeling.model.modelHub.modelHubContainer.info import Info


class ModelHubContainer:
    __version__ = '0.0.0.1'
    classId: str = Info.get_expectedClassId()
    InfoClass = Info
    ModelHubClass = ModelHub

    _modelHub_dirName = 'modelHub'

    def __init__(
        self, modelHub: ModelHub, name: str | None = None, attrs: dict | None = None
    ) -> None:
        """Clase skirta talpinti modelHub'a ir programuoto logika ant virsaus"""

        attrs = dict() if attrs is None else attrs

        assert isinstance(modelHub, self.ModelHubClass)
        assert name is None or isinstance(name, str)
        assert isinstance(attrs, dict)

        if name is None:
            name = modelHub.name
        assert isinstance(name, str)

        self._modelHub: ModelHub = modelHub
        self._name = name
        self._attrs: dict = attrs

    @property
    def name(self) -> str:
        return self._name

    @property
    def attrs(self) -> dict:
        return self._attrs

    @property
    def modelHub(self):
        return self._modelHub

    def get_info(self) -> Info:
        return self.InfoClass(
            version=self.__version__,
            classId=self.classId,
            className=self.__class__.__name__,
            name=self._name,
            attrs=self._attrs,
        )

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save sub-models
        _dirPath = os.path.join(dirPath, self._modelHub_dirName)
        self._modelHub.save(dirPath=_dirPath)

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

    @classmethod
    def _load_argDict(cls, dirPath: str) -> dict[str, Any]:
        info = cls.InfoClass.load(dirPath=dirPath)

        # get sub-models paths and compare
        _dirPath = os.path.join(dirPath, cls._modelHub_dirName)
        modelHub = cls.ModelHubClass.load(dirPath=_dirPath)

        return dict(
            modelHub=modelHub,
            name=info.name,
            attrs=info.attrs,
        )

    @classmethod
    def load(cls, dirPath: str) -> 'ModelHubContainer':
        argDict = cls._load_argDict(dirPath=dirPath)
        return cls(**argDict)
