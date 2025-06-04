# mypy: disable-error-code="assignment,override"
import os.path
from typing import Any, Mapping

from cachetools import cached

from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.iModel import IModel
from anre.utils.modeling.model.iPersistModel import IPersistModel
from anre.utils.modeling.model.leafModel.leafModel import LeafModel
from anre.utils.modeling.model.modelHub.info import Info
from anre.utils.modeling.model.modelLoader import ModelLoader
from anre.utils.modeling.transformer.iTransformer import ITransformer
from anre.utils.modeling.transformer.transformer import Transformer


class ModelHub(IPersistModel):
    """Modeliu hubas.

    Sis objektas nera pilnavertis modelis, nes jo predict funkcija neapibrezta (nes jineveinareikme),bet vaikai gali apsibrezti ja tvarkingai.
    Nera ir kitu atributu, kaip shape

    """

    __version__ = '0.0.0.1'
    classId: str = Info.get_expectedClassId()
    _models_dirName = 'models'
    _inputTransformer_dirName = "inputTransformer"
    _outputTransformer_dirName = "outputTransformer"
    InfoClass = Info

    @classmethod
    def new_fromList(
        cls,
        *,
        models: list[IPersistModel],
        name: str | None = None,
        attrs: dict | None = None,
        useNamesAsKeys: bool = False,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
        skipValidation=False,
    ):
        attrs = dict() if attrs is None else attrs

        if useNamesAsKeys:
            modelDict = {model.name: model for model in models}
            assert len(modelDict) == len(models), (
                'Some names in models are the same. Please use unique names or use useNamesAsKeys=False'
            )
            subModelKeys = [model.name for model in models]
        else:
            modelDict = {str(i): model for i, model in enumerate(models)}
            subModelKeys = [str(i) for i in range(len(models))]

        return cls.new(
            modelDict=modelDict,
            name=name,
            attrs=attrs,
            subModelKeys=subModelKeys,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
            skipValidation=skipValidation,
        )

    @classmethod
    def new(
        cls,
        modelDict: dict[str, IPersistModel],
        name: str | None = None,
        attrs: dict | None = None,
        subModelKeys: list[str] | None = None,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
        skipValidation=False,
    ) -> 'ModelHub':
        name = cls.__name__ if name is None else name
        attrs = dict() if attrs is None else attrs
        subModelKeys = list(modelDict) if subModelKeys is None else subModelKeys
        return cls(
            modelDict=modelDict,
            name=name,
            attrs=attrs,
            subModelKeys=subModelKeys,
            inputTransformer=inputTransformer,
            isLazy=False,
            outputTransformer=outputTransformer,
            skipValidation=skipValidation,
        )

    def __init__(
        self,
        modelDict: Mapping[str, IPersistModel | str],
        name: str,
        attrs: dict,
        subModelKeys: list[str],
        isLazy: bool,
        inputTransformer: ITransformer | None,
        outputTransformer: ITransformer | None,
        skipValidation: bool = False,
    ):
        inputTransformer = (
            inputTransformer
            if inputTransformer is not None
            else Transformer.new_identity().fit(None)  # type: ignore[arg-type]
        )
        outputTransformer = (
            outputTransformer
            if outputTransformer is not None
            else Transformer.new_identity().fit(None)  # type: ignore[arg-type]
        )

        assert isinstance(modelDict, dict)
        assert isinstance(name, str)
        assert isinstance(attrs, dict)
        assert isinstance(subModelKeys, (list, tuple))
        assert isinstance(skipValidation, bool)
        assert isinstance(isLazy, bool)
        assert isinstance(inputTransformer, ITransformer)
        assert isinstance(outputTransformer, ITransformer)

        subModelKeys = tuple(subModelKeys)
        modelDict = {key: modelDict[key] for key in subModelKeys}

        self._modelDict: dict[str, IPersistModel] = modelDict
        self._attrs: dict = attrs
        self._name: str = name
        self._isLazy: bool = isLazy
        self._subModelKeys: tuple[str, ...] = subModelKeys
        self._inputTransformer = inputTransformer
        self._outputTransformer = outputTransformer

        if not skipValidation:
            self.validate()

    def get_childModels(self) -> list[IPersistModel]:
        return [self.get_subModel(key) for key in self._subModelKeys]

    def get_subModelCount(self) -> int:
        return len(self._subModelKeys)

    @classmethod
    def _collect_leafModels(cls, model) -> list[LeafModel]:
        if isinstance(model, LeafModel):
            return [model]

        elif issubclass(model.__class__, ModelHub):
            childModels = model.get_childModels()
            resList = []
            for childModel in childModels:
                childResList = cls._collect_leafModels(childModel)
                resList.extend(childResList)
            return resList

        else:
            msg = f'Model of class {type(model)} is not Implemented: {model=}'
            raise NotImplementedError(msg)

    def load_allSubModels(self):
        _ = self._collect_leafModels(self)

    @cached({})
    def get_xFields(self) -> list[str]:
        return self._get_xFields_fromModel(model=self)

    @classmethod
    def _get_xFields_fromModel(cls, model) -> list[str]:
        if isinstance(model, LeafModel):
            return model.xFields

        elif issubclass(model.__class__, ModelHub):
            childModels = model.get_childModels()
            resList = []
            for childModel in childModels:
                if hasattr(childModel, 'get_xFields'):
                    childResList = childModel.get_xFields()
                else:
                    childResList = cls._get_xFields_fromModel(childModel)
                resList.extend(childResList)
            return list(set(resList))

        else:
            msg = f'Model of class {type(model)} is not Implemented: {model=}'
            raise NotImplementedError(msg)

    def validate(self):
        ### modelDict
        assert isinstance(self._modelDict, dict)
        assert self._modelDict
        for key, model in self._modelDict.items():
            if isinstance(model, str):
                assert self._isLazy
                assert os.path.exists(model)
            else:
                assert isinstance(model, IPersistModel), (
                    f'model(`{model}`) expected to be instance of IPersistModel, but got {type(model)}'
                )
            assert isinstance(key, str)
            assert key

        ### name
        assert isinstance(self._name, str)
        assert self._name

        ### attrs
        assert isinstance(self._attrs, dict)
        assert Info.check_ifDictIsConvertable(self._attrs), (
            f'attrs is not convertable: {self._attrs}'
        )

        ### subModelKeys
        assert isinstance(self._subModelKeys, tuple)
        assert set(self._subModelKeys) == set(self._modelDict)
        assert len(self._subModelKeys) == len(self._subModelKeys)
        assert all([isinstance(el, str) for el in self._subModelKeys])

    @property
    def name(self) -> str:
        return self._name

    @property
    def attrs(self) -> dict:
        return self._attrs

    @property
    def subModelKeys(self) -> tuple[str, ...]:
        return self._subModelKeys

    def set_name(self, name: str):
        assert isinstance(name, str)
        assert name
        self._name = name

    def set_attrs(self, attrs: dict):
        assert isinstance(attrs, dict)
        assert Info.check_ifDictIsConvertable(attrs)
        self._attrs = attrs

    def set_inAttrs(self, **kwargs: Any):
        assert Info.check_ifDictIsConvertable(kwargs)
        self._attrs.update(**kwargs)

    def get_subModel(self, key: str) -> IPersistModel:
        assert isinstance(key, str)
        modelOrPath = self._modelDict[key]
        if isinstance(modelOrPath, str):
            modelOrPath = ModelLoader.load(dirPath=modelOrPath, lazyLevel=1)
            assert isinstance(modelOrPath, IPersistModel)
            self._modelDict[key] = modelOrPath

        assert isinstance(modelOrPath, IPersistModel)
        return modelOrPath

    def get_info(self) -> Info:
        return self.InfoClass(
            version=self.__version__,
            classId=self.classId,
            className=self.__class__.__name__,
            name=self.name,
            attrs=self.attrs,
            subModelKeys=self.subModelKeys,
        )

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save sub-models
        _modelsDirPath = os.path.join(dirPath, self._models_dirName)
        FileSystem.create_folder(_modelsDirPath, raise_if_exists=True)
        for label, subModel in self._modelDict.items():
            _dirPath = os.path.join(_modelsDirPath, str(label))
            subModel.save(dirPath=_dirPath)

        # save transformers
        _dirPath = os.path.join(dirPath, self._inputTransformer_dirName)
        self._inputTransformer.save(dirPath=_dirPath, overwrite=False)
        _dirPath = os.path.join(dirPath, self._outputTransformer_dirName)
        self._outputTransformer.save(dirPath=_dirPath, overwrite=False)

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

    @classmethod
    def load(cls, dirPath: str, lazyLevel: int = 0) -> IPersistModel:
        """

        lazyLevel - jei lazyLevel > 0, tai sub-modeliai neloadinami kol jo niekas nepaprase. Kiekvienas vaikas bus kraunas su lazyLevel += 1.
        """

        info = cls.InfoClass.load(dirPath=dirPath)
        isLazy = lazyLevel > 0

        # get sub-models paths and compare
        _modelsDirPath = os.path.join(dirPath, cls._models_dirName, '*')
        subModelDirPathList = FileSystem.get_path_list_via_glob(_modelsDirPath)
        namesFoundSet = {
            os.path.basename(subModelDirPath) for subModelDirPath in subModelDirPathList
        }
        namesExpectSet = set(info.subModelKeys)
        assert namesFoundSet == namesExpectSet, (
            f'Actual names not matching expected names: {namesFoundSet=} vs {namesExpectSet=}'
        )

        # load sub-models
        modelDict = {}
        for _dirPath in subModelDirPathList:
            label = os.path.basename(_dirPath)
            if isLazy:
                model = _dirPath
            else:
                model = ModelLoader.load(dirPath=_dirPath, lazyLevel=lazyLevel + 1)
            modelDict[label] = model

        # load transformers
        _dirPath = os.path.join(dirPath, cls._inputTransformer_dirName)
        inputTransformer = Transformer.load(dirPath=_dirPath)
        _dirPath = os.path.join(dirPath, cls._outputTransformer_dirName)
        outputTransformer = Transformer.load(dirPath=_dirPath)

        instance = cls(
            modelDict=modelDict,
            name=info.name,
            attrs=info.attrs,
            subModelKeys=info.subModelKeys,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
            isLazy=isLazy,
        )
        return instance

    @staticmethod
    def _checkConvert_subModelsToIModel(modelDict) -> dict[str, IModel | str]:
        assert isinstance(modelDict, dict)
        for key, model in modelDict.items():
            assert isinstance(model, (IModel, str))
        return modelDict
