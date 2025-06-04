# mypy: disable-error-code="override"
from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd
from tensorflow import keras  # type: ignore[import-not-found]

from anre.type import Type
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.leafModel.coreModel.iCoreModel import ICoreModel
from anre.utils.modeling.model.leafModel.coreModel.info import Info

# FIXME: Add missing files with the below types
# from anre.utils.modeling.tensorflow_.modelFactory.modelFactory import kerasModelType
# from anre.utils.modeling.tensorflow_.wrapper.wrapper import Wrapper as TfWrapper


class TfWrapper:
    pass


class kerasModelType:
    pass


class KerasRegression(ICoreModel):
    __version__ = '0.0.0.1'

    classId: str = 'KerasRegression'
    isRegression: bool = True
    isClassification: bool = False

    _engineClass = TfWrapper
    _fileName_engine = 'tfWrapper'
    _fileName_extraParams = 'extraParams.json'

    @classmethod
    def new(cls, name: str = 'Model', **kwargs: Any) -> 'KerasRegression':
        engine = kwargs.pop('engine', None)
        if engine is None:
            hpKwargs = cls.get_hpKwargs(**kwargs)
            engine = cls._engineFactory(**hpKwargs)
        return cls.new_fromEngine(engine=engine, name=name)

    @classmethod
    def new_fromEngine(cls, engine, name: str = 'Model', **kwargs: Any) -> 'KerasRegression':
        assert not kwargs
        return cls(engine=engine, name=name)

    def __init__(self, engine: TfWrapper, name: str) -> None:
        assert self.classId == self.__class__.__name__
        assert isinstance(name, str)
        assert self.isValidEngine(engine=engine)
        self._engine: TfWrapper = engine
        self.name: str = name

    @property
    def isFitted(self) -> bool:
        return self._engine.isFitted  # type: ignore[attr-defined]

    @property
    def input_shape(self) -> tuple:
        return self._engine.input_shape  # type: ignore[attr-defined]

    @property
    def output_shape(self) -> tuple:
        return self._engine.output_shape  # type: ignore[attr-defined]

    def predict(self, X, **kwargs: Any) -> np.ndarray:
        assert self.isFitted, 'Model is not fitted.'
        pred = self._engine.predict(X)  # type: ignore[attr-defined]
        assert isinstance(pred, np.ndarray)
        assert len(pred.shape) == len(self.output_shape)
        return pred

    @classmethod
    def get_hpKwargs(cls, **kwargs: Any) -> dict[str, Type.BasicType]:
        return dict()

    @classmethod
    def get_hyperParameterList(cls, **kwargs: Any):
        return []

    def fit(self, X, y, **kwargs: Any):
        assert not self.isFitted, 'Model is already fitted. Use recreate of fit_continue.'
        self._engine.fit(X, y, **kwargs)  # type: ignore[attr-defined]

    def fit_continue(self, X, y, **kwargs: Any):
        assert self.isFitted, 'Model is not fitted. Use fit first.'
        self._engine.fit(X, y, **kwargs)  # type: ignore[attr-defined]

    @classmethod
    def isValidEngine(cls, engine) -> bool:
        return isinstance(engine, cls._engineClass)

    def get_info(self) -> Info:
        return Info(
            version=self.__version__,
            classId=self.classId,
            className=self.__class__.__name__,
            name=self.name,
            isRegression=self.isRegression,
            isClassification=self.isClassification,
            input_shape=self.input_shape,
            output_shape=self.output_shape,
            isFitted=self.isFitted,
            attrs=dict(),
        )

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        assert self.isFitted, 'Model is not fitted.'

        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save strategy itself
        engineFilePath = os.path.join(dirPath, self._fileName_engine)
        self._engine.save(engineFilePath)  # type: ignore[attr-defined]

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

    @classmethod
    def load(cls, dirPath: str) -> KerasRegression:
        info = Info.load(dirPath=dirPath)
        assert info.classId == cls.classId

        engineFilePath = os.path.join(dirPath, cls._fileName_engine)
        engine = TfWrapper.load(engineFilePath)  # type: ignore[attr-defined]
        assert cls.isValidEngine(engine=engine)

        instance = cls(
            engine=engine,
            name=info.name,
        )
        return instance

    def copy(self):
        return self.__class__(engine=self._engine.copy(), name=self.name)

    def recreate(self, **kwargs: Any):
        return self.__class__.new(
            engine=self._engine.recreate(**kwargs),  # type: ignore[attr-defined]
        )

    def get_engine(self):
        return self._engine

    def get_tfModel(self) -> kerasModelType:
        return self._engine.get_tfModel()  # type: ignore[attr-defined]

    def get_featureImportanceSr(self) -> pd.Series:
        raise NotImplementedError

    def set_lr(self, learning_rate):
        keras.backend.set_value(self._engine.optimizer.learning_rate, learning_rate)

    def get_weights(self):
        return self._engine.get_weights()

    def set_weights(self, weights):
        return self._engine.set_weights(weights)

    @staticmethod
    def _engineFactory(**kwargs: Any) -> TfWrapper:
        return TfWrapper.new_regression_robust(**kwargs)  # type: ignore[attr-defined]
