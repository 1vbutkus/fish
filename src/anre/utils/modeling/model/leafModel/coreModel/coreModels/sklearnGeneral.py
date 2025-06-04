# mypy: disable-error-code="override"
import os
from copy import deepcopy
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from anre.type import Type
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.coreModel.iCoreModel import ICoreModel
from anre.utils.modeling.model.leafModel.coreModel.info import Info
from anre.utils.modeling.sklearn_ import utils as sku


class SklearnGeneral(ICoreModel):
    __version__ = '0.0.0.1'

    classId: str = 'SklearnGeneral'
    _fileName_engine = 'engine.joblib'

    @classmethod
    def new_pipe(cls, name: str = 'Model', **kwargs: Any):
        return cls.new(engine=cls._engineFactory_pipe(**kwargs), name=name)

    @classmethod
    def new_model(cls, name: str = 'Model', **kwargs: Any):
        hpKwargs = cls.get_hpKwargs(**kwargs)
        return cls.new(engine=cls._engineFactory_model(**hpKwargs), name=name)

    @classmethod
    def new(cls, name: str = 'Model', **kwargs: Any):
        engine = kwargs.pop('engine', None)
        if engine is None:
            engine = cls._engineFactory_pipe(**kwargs)
        return cls.new_fromEngine(engine=engine, name=name)

    @classmethod
    def new_fromEngine(cls, engine, name: str = 'Model', **kwargs: Any):
        assert not kwargs
        assert cls.isValidEngine(engine=engine)
        engine = sklearn.base.clone(engine)
        return cls(
            engine=engine,
            input_shape=None,
            output_shape=None,
            isFitted=False,
            name=name,
        )

    def __init__(
        self,
        engine,
        input_shape: tuple | None,
        output_shape: tuple | None,
        isFitted: bool,
        name: str,
    ):
        assert isinstance(isFitted, bool)
        assert isinstance(name, str)
        assert self.isValidEngine(engine=engine)

        if input_shape is not None:
            input_shape = tuple(input_shape)
            assert isinstance(input_shape, tuple)
            assert len(input_shape) == 2

        if output_shape is not None:
            output_shape = tuple(output_shape)
            assert isinstance(output_shape, tuple)
            assert len(output_shape) == 1

        self._engine = engine
        self._isFitted: bool = isFitted
        self._input_shape = input_shape
        self._output_shape = output_shape
        self.name: str = name

    @property
    def isRegression(self) -> bool:
        assert sku.isSklearnModel(self._engine)
        return sku.isRegressor(self._engine)

    @property
    def isClassification(self) -> bool:
        assert sku.isSklearnModel(self._engine)
        return sku.isClassifier(self._engine)

    @property
    def isFitted(self) -> bool:
        return self._isFitted

    @property
    def input_shape(self) -> tuple:
        assert self.isFitted, 'Model is not fitted. No dimensions yet.'
        assert isinstance(self._input_shape, tuple)
        return self._input_shape

    @property
    def output_shape(self) -> tuple:
        assert self.isFitted, 'Model is not fitted. No dimensions yet.'
        assert isinstance(self._output_shape, tuple)
        return self._output_shape

    def predict(self, X, **kwargs: Any) -> np.ndarray:
        assert self.isFitted, 'Model is not fitted.'
        pred = self._engine.predict(X, **kwargs)
        assert isinstance(pred, np.ndarray)
        assert self._output_shape is not None
        assert len(pred.shape) == len(self._output_shape)
        return pred

    @classmethod
    def get_hpKwargs(cls, **kwargs: Any) -> dict[str, Type.BasicType]:
        return dict()

    @classmethod
    def get_hyperParameterList(cls, **kwargs: Any):
        return []

    def fit(self, X, y, **kwargs: Any):
        assert not self.isFitted, 'Model is already fitted. Use recreate or fit_continue'
        assert len(X.shape) == 2
        self._input_shape = (None, X.shape[-1])
        self._output_shape = (None,)
        self._engine.fit(X, y, **kwargs)
        self._isFitted = True

    def fit_continue(self, X, y, **kwargs: Any):
        raise NotImplementedError

    @classmethod
    def isValidEngine(cls, engine) -> bool:
        return sku.isSklearnModel(engine)

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        assert self.isFitted, 'Model is not fitted.'

        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save strategy itself
        engineFilePath = os.path.join(dirPath, self._fileName_engine)
        joblib.dump(self._engine, engineFilePath)

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

    @classmethod
    def load(cls, dirPath: str):
        info = Info.load(dirPath=dirPath)
        assert info.classId == cls.classId

        engineFilePath = os.path.join(dirPath, cls._fileName_engine)
        engine = joblib.load(engineFilePath)
        assert cls.isValidEngine(engine=engine)

        instance = cls(
            engine=engine,
            input_shape=info.input_shape,
            output_shape=info.output_shape,
            isFitted=info.isFitted,
            name=info.name,
        )
        return instance

    def copy(self):
        return deepcopy(self)

    def recreate(self, **kwargs: Any):
        if kwargs:
            raise NotImplementedError
        return self.__class__.new_fromEngine(engine=self._engine)

    def get_info(self) -> Info:
        return Info(
            version=self.__version__,
            classId=self.classId,
            className=self.__class__.__name__,
            name=self.name,
            isRegression=self.isRegression,
            isClassification=self.isClassification,
            isFitted=self.isFitted,
            input_shape=self.input_shape,
            output_shape=self.output_shape,
            attrs=dict(),
        )

    def get_engine(self):
        return self._engine

    def get_featureImportanceSr(self) -> pd.Series:
        raise NotImplementedError

    @classmethod
    def _engineFactory_pipe(cls, **kwargs: Any):
        engine = Pipeline([('scaler', RobustScaler()), ('regression', LinearRegression())])
        assert cls.isValidEngine(engine=engine)
        return engine

    @classmethod
    def _engineFactory_model(cls, **kwargs: Any):
        engine = RandomForestRegressor(**kwargs)
        assert cls.isValidEngine(engine=engine)
        return engine
