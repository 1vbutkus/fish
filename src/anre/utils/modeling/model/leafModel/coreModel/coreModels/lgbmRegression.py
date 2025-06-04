# mypy: disable-error-code="override"
import os
from copy import deepcopy
from typing import Any

import joblib
import numpy as np
import pandas as pd
from lightgbm import Booster, LGBMRegressor

from anre.type import Type
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.model.hyperParameters.hpCatalog import HpCatalog
from anre.utils.modeling.model.leafModel.coreModel.iCoreModel import ICoreModel
from anre.utils.modeling.model.leafModel.coreModel.info import Info


class LgbmRegression(ICoreModel):
    __version__ = '0.0.0.1'

    classId: str = 'LgbmRegression'
    isRegression: bool = True
    isClassification: bool = False

    _engineClass = LGBMRegressor
    _fileName_engine = 'engine.joblib'
    _hpCatalog: HpCatalog = HpCatalog.new_lgbm()

    @classmethod
    def new(cls, name: str = 'Model', **kwargs: Any) -> 'LgbmRegression':
        hpKwargs = cls.get_hpKwargs(**kwargs)
        return cls.new_fromEngine(engine=cls._engineFactory(**hpKwargs), name=name)

    @classmethod
    def new_fromEngine(cls, engine, name: str = 'Model', **kwargs: Any) -> 'LgbmRegression':
        assert cls.isValidEngine(engine=engine)

        # we recreate engine to make sure it is not fitted
        kwargsCompose = engine.get_params()
        kwargsCompose.update(**kwargs)
        engine = cls._engineFactory(**kwargsCompose)

        return cls(engine=engine, input_shape=None, output_shape=None, name=name)

    def __init__(
        self, engine, input_shape: tuple | None, output_shape: tuple | None, name: str
    ) -> None:
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
        self._input_shape = input_shape
        self._output_shape = output_shape
        self.name: str = name

    @property
    def isFitted(self) -> bool:
        if isinstance(self._engine, Booster):
            return True
        return self._engine.__sklearn_is_fitted__()

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

    def predict(self, X, n_jobs=1, **kwargs: Any) -> np.ndarray:
        assert self.isFitted, 'Model is not fitted.'
        pred = self._engine.predict(X, n_jobs=n_jobs, **kwargs)
        assert isinstance(pred, np.ndarray)
        assert self._output_shape is not None
        assert len(pred.shape) == len(self._output_shape)
        return pred

    @classmethod
    def get_hpKwargs(cls, **kwargs: Any) -> dict[str, Type.BasicType]:
        return cls._hpCatalog.get_hpKwargs(**kwargs)

    @classmethod
    def get_hyperParameterList(cls, **kwargs: Any):
        return cls._hpCatalog.get_hyperParameterList(**kwargs)

    def fit(self, X, y, **kwargs: Any):
        assert not self.isFitted, 'Model is already fitted. Use recreate or fit_continue'
        assert len(X.shape) == 2
        self._input_shape = (None, X.shape[-1])
        self._output_shape = (None,)
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.DataFrame):
            y = y.values
        assert X.shape[0] == y.shape[0]
        assert y.shape[0] > 0
        self._engine.fit(X, y, **kwargs)

    def fit_continue(self, X, y, **kwargs: Any):
        raise NotImplementedError

    @classmethod
    def isValidEngine(cls, engine) -> bool:
        return isinstance(engine, (cls._engineClass, Booster))

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
            name=info.name,
        )
        return instance

    def copy(self) -> 'LgbmRegression':
        return deepcopy(self)

    def recreate(self, **kwargs: Any) -> 'LgbmRegression':
        return self.__class__.new_fromEngine(self._engine, **kwargs)

    def get_info(self) -> Info:
        return Info(
            version=self.__version__,
            classId=self.classId,
            className=self.__class__.__name__,
            name=self.name,
            isRegression=self.isRegression,
            isClassification=self.isClassification,
            isFitted=self.isFitted,
            input_shape=self._input_shape,  # type: ignore[arg-type]
            output_shape=self._output_shape,  # type: ignore[arg-type]
            attrs=dict(),
        )

    def get_engine(self):
        return self._engine

    def get_featureImportanceSr(self) -> pd.Series:
        return pd.Series(self._engine.feature_importances_, index=self._engine.feature_name_)

    @classmethod
    def _engineFactory(cls, **kwargs: Any):
        engine = cls._engineClass(**kwargs)
        assert cls.isValidEngine(engine=engine)
        return engine
