# mypy: disable-error-code="assignment,override"
from __future__ import annotations

import os
from copy import deepcopy
from typing import Any, Iterable

import numpy as np
import pandas as pd

from anre.type import Type
from anre.utils import functions
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.coreModel.coreModel import (
    CoreModel,
    LgbmClassificationBinary,
    LgbmRegression,
    SklearnGeneral,
)
from anre.utils.modeling.model.leafModel.coreModel.iCoreModel import ICoreModel
from anre.utils.modeling.model.leafModel.iLeafModel import ILeafModel
from anre.utils.modeling.model.leafModel.info import Info
from anre.utils.modeling.transformer.iTransformer import ITransformer
from anre.utils.modeling.transformer.transformer import Transformer


class LeafModel(ILeafModel):
    """Standartizuoto interfaso modelis kuris gali padaryti viena konkrecia prognoze (galimai daugiadimensine)

    Sio lygmens tikslas, kad tai butu vienas, savarankiskas modelis su standartizuotu interfasu, t.y.
    Kad nereikatu dar tampytis atskiarai imputo pavaidimu, scaleriu ir panasiai. Sitas objektas turi tureti viska ko reikia, kad padaryti pilna prognoze.

    Note: Inputo proprocesisnimu rupinasi coreModeliai (arba ju enginas)

    Nuo CoreModelio sis lygmuo skiriasi dvie esminiais aspektais:
      - Moka atsirinkti savo inputus is bendro masyvo - t.y. is dataFrame, nereikia isoriskai pjaustyti informacijos.
      - Mka scalinti/reversinti output kintamuosius.

    """

    classId: str = Info.get_expectedClassId()
    __version__ = "0.0.0.1"
    _coreModel_dirName = "coreModel"
    _inputTransformer_dirName = "inputTransformer"
    _outputTransformer_dirName = "outputTransformer"

    @classmethod
    def new(
        cls,
        name: str = "Model",
        xFields: Iterable | None = None,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
        **kwargs,
    ) -> LeafModel:
        coreModel = kwargs.pop("coreModel", None)
        if coreModel is None:
            coreModel = LgbmRegression.new(name=name, **kwargs)
        return cls(
            coreModel=coreModel,
            xFields=xFields,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
        )

    def __init__(
        self,
        coreModel: ICoreModel,
        xFields: Iterable | None = None,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
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
        xFields = list(xFields) if xFields is not None else []

        assert isinstance(coreModel, ICoreModel)
        assert isinstance(inputTransformer, ITransformer)
        assert isinstance(outputTransformer, ITransformer)
        assert isinstance(xFields, list)
        if coreModel.isFitted and bool(xFields):
            assert coreModel.input_shape[-1] == len(xFields)

        self.xFields: list[str] = xFields
        self.coreModel = coreModel
        self.inputTransformer = inputTransformer
        self.outputTransformer = outputTransformer

    @property
    def name(self) -> str:
        return self.coreModel.name

    def set_name(self, name: str):
        assert isinstance(name, str)
        self.coreModel.name = name

    def get_engine(self):
        return self.coreModel.get_engine()

    @classmethod
    def isValidEngine(cls, engine) -> bool:
        raise NotImplementedError

    @classmethod
    def new_fromEngine(
        cls, engine, name: str = "Model", xFields: list[str] | None = None, **kwargs
    ) -> LeafModel:
        coreModel = CoreModel.new_fromEngine(engine=engine, name=name, **kwargs)
        instance = cls(coreModel=coreModel, xFields=xFields)
        return instance

    @classmethod
    def new_fromClassId(
        cls,
        classId: str,
        name: str = "Model",
        xFields: Iterable | None = None,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
        hp: dict | None = None,
    ) -> LeafModel:
        hp = hp if hp is not None else dict()
        assert isinstance(hp, dict)
        coreModel = CoreModel.new_fromModelClassId(classId=classId, name=name, **hp)
        instance = cls(
            coreModel=coreModel,
            xFields=xFields,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
        )
        return instance

    @classmethod
    def new_lgbmClassificationBinary(cls, xFields: Iterable | None = None, **kwargs: Any):
        return cls.new_fromClassId(
            classId=LgbmClassificationBinary.classId, xFields=xFields, hp=kwargs
        )

    @classmethod
    def new_lgbmRegression(
        cls,
        xFields: Iterable | None = None,
        inputTransformer: ITransformer | None = None,
        outputTransformer: ITransformer | None = None,
        **kwargs: Any,
    ):
        return cls.new_fromClassId(
            classId=LgbmRegression.classId,
            xFields=xFields,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
            hp=kwargs,
        )

    @classmethod
    def new_sklearnGeneral(cls, xFields: Iterable | None = None, **kwargs: Any):
        return cls.new_fromClassId(classId=SklearnGeneral.classId, xFields=xFields, hp=kwargs)

    @classmethod
    def new_kerasRegression(cls, xFields: Iterable | None = None, **kwargs: Any):
        return cls.new_fromClassId(classId="KerasRegression", xFields=xFields, hp=kwargs)

    @classmethod
    def new_kerasClassificationBinary(cls, xFields: Iterable | None = None, **kwargs: Any):
        return cls.new_fromClassId(classId="KerasClassificationBinary", xFields=xFields, hp=kwargs)

    def __call__(self, X: Type.X, **kwargs: Any):
        return self.predict(X=X, **kwargs)

    def copy(self) -> LeafModel:
        return self.__class__(
            coreModel=self.coreModel.copy(),
            xFields=deepcopy(self.xFields),
            inputTransformer=deepcopy(self.inputTransformer),
            outputTransformer=deepcopy(self.outputTransformer),
        )

    def recreate(self, **kwargs: Any) -> LeafModel:
        return self.__class__(
            coreModel=self.coreModel.recreate(**kwargs),
            xFields=deepcopy(self.xFields),
            inputTransformer=deepcopy(self.inputTransformer),
            outputTransformer=deepcopy(self.outputTransformer),
        )

    @property
    def output_shape(self):
        return self.coreModel.output_shape

    @property
    def input_shape(self):
        if self.xFields:
            return None, len(self.xFields)
        return self.coreModel.input_shape

    @property
    def isRegression(self):
        return self.coreModel.isRegression

    @property
    def isClassification(self):
        return self.coreModel.isClassification

    @property
    def isFitted(self):
        return self.coreModel.isFitted

    def _getValidate_X(self, X):
        if isinstance(X, pd.DataFrame):
            assert not isinstance(X.columns, pd.MultiIndex)
            if self.xFields is None or len(self.xFields) == 0:
                self.xFields = list(X.columns)
            else:
                X = X[self.xFields]
        elif isinstance(X, np.ndarray):
            pass
        else:
            raise NotImplementedError

        X = self.inputTransformer.transform(X)
        return X

    @classmethod
    def get_hpKwargs(cls, **kwargs: Any) -> dict[str, Type.BasicType]:
        return cls.coreModel.get_hpKwargs(**kwargs)

    @classmethod
    def get_hyperParameterList(cls, **kwargs: Any):
        return cls.coreModel.get_hyperParameterList(**kwargs)

    def fit(self, X, y, **kwargs: Any):
        assert not self.isFitted, "Model is already fitted. Use recreate or fit_continue."

        if not self.inputTransformer.isFitted:
            self.inputTransformer.fit(x=X)
        if not self.outputTransformer.isFitted:
            self.outputTransformer.fit(x=y)

        X = self._getValidate_X(X=X)
        y = self.outputTransformer.transform(y)
        self.coreModel.fit(X=X, y=y, **kwargs)

    def fit_continue(self, X, y, **kwargs: Any):
        assert self.isFitted
        X = self._getValidate_X(X=X)
        y = self.outputTransformer.transform(y)
        self.coreModel.fit_continue(X=X, y=y, **kwargs)

    def get_info(self) -> Info:
        return Info(
            version=self.__version__,
            classId=self.classId,
            className=self.__class__.__name__,
            name=self.name,
            attrs=dict(),
            xFields=self.xFields,
        )

    def get_xDf(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.xFields]

    def predict(
        self, X: Type.X, chunkSize: int | None = None, skipPredScale: bool = False, **kwargs
    ) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            if chunkSize is None:
                # xDf = self.get_xDf(df=X)
                X = self._getValidate_X(X=X)
                pred = self.coreModel.predict(X=X, **kwargs)
            else:
                assert chunkSize > 0
                predList = []
                for subDf in functions.chunksTable(table=X, chunkSize=chunkSize):
                    # xDf = self.get_xDf(df=subDf)
                    X = self._getValidate_X(X=subDf)
                    pred = self.coreModel.predict(X=X, **kwargs)
                    predList.append(pred)
                del subDf
                pred = np.concatenate(predList)

        elif isinstance(X, np.ndarray):
            if chunkSize is None:
                X = self._getValidate_X(X=X)
                pred = self.coreModel.predict(X=X, **kwargs)
            else:
                assert chunkSize > 0
                predList = []
                for subX in functions.chunksTable(table=X, chunkSize=chunkSize):
                    X = self._getValidate_X(X=subX)
                    pred = self.coreModel.predict(X=X, **kwargs)
                    predList.append(pred)
                del subX
                pred = np.concatenate(predList)

        else:
            raise NotImplementedError

        if skipPredScale:
            return pred
        else:
            pred = self.outputTransformer.inverse_transform(x=pred)

        assert isinstance(pred, np.ndarray)
        assert pred.shape[1:] == self.output_shape[1:]

        return pred

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        assert self.isFitted, "Model is not fitted"

        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save core strategy
        _dirPath = os.path.join(dirPath, self._coreModel_dirName)
        self.coreModel.save(dirPath=_dirPath, overwrite=False)

        # save transformers
        _dirPath = os.path.join(dirPath, self._inputTransformer_dirName)
        self.inputTransformer.save(dirPath=_dirPath, overwrite=False)
        _dirPath = os.path.join(dirPath, self._outputTransformer_dirName)
        self.outputTransformer.save(dirPath=_dirPath, overwrite=False)

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

    @classmethod
    def load(cls, dirPath: str) -> LeafModel:
        info = Info.load(dirPath=dirPath)
        xFields = info.xFields

        # load coreModel
        _dirPath = os.path.join(dirPath, cls._coreModel_dirName)
        coreModel = CoreModel.load(dirPath=_dirPath)

        # load transformers
        _dirPath = os.path.join(dirPath, cls._inputTransformer_dirName)
        inputTransformer = Transformer.load(dirPath=_dirPath)
        _dirPath = os.path.join(dirPath, cls._outputTransformer_dirName)
        outputTransformer = Transformer.load(dirPath=_dirPath)

        instance = cls(
            xFields=xFields,
            coreModel=coreModel,
            inputTransformer=inputTransformer,
            outputTransformer=outputTransformer,
        )
        return instance

    def get_featureImportanceSr(self) -> pd.Series:
        featureImportanceSr = self.coreModel.get_featureImportanceSr()
        featureImportanceSr.index = self.xFields
        return featureImportanceSr
