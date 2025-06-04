# mypy: disable-error-code="override"
from __future__ import annotations

import copy
import os
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn.base
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler

from anre.type import Type
from anre.utils.fileSystem.fileSystem import FileSystem
from anre.utils.modeling.transformer.info import Info
from anre.utils.modeling.transformer.iTransformer import ITransformer


class SklearnGeneral(ITransformer):
    classId = 'SklearnGeneral'
    __version__ = "0.0.0.1"
    _fileName_engine = 'engine.joblib'

    @classmethod
    def new_scalePca(cls, quantile_range=(5, 95), nComponents=None) -> 'SklearnGeneral':
        return cls.new(
            engine=make_pipeline(
                RobustScaler(quantile_range=quantile_range), PCA(n_components=nComponents)
            )
        )

    @classmethod
    def new_selectPca(cls, nComponents=None, pcaFields=None) -> 'SklearnGeneral':
        if pcaFields:
            engine = ColumnTransformer(
                [
                    ("norm1", PCA(n_components=nComponents), pcaFields),
                ],
                remainder="passthrough",
            )
        else:
            engine = PCA(n_components=nComponents)
        return cls.new(engine=engine)

    @classmethod
    def new_scaler(cls, quantile_range=(5, 95)) -> 'SklearnGeneral':
        return cls.new(engine=RobustScaler(quantile_range=quantile_range))

    @classmethod
    def new(cls, **kwargs: Any) -> 'SklearnGeneral':
        engine = kwargs.pop('engine', None)
        engine = (
            engine
            if engine is not None
            else make_pipeline(RobustScaler(quantile_range=(5, 95)), PCA())
        )
        return cls(
            engine=engine,
            isFitted=False,
            isVector=None,
        )

    def __init__(self, engine, isFitted: bool, isVector: bool | None) -> None:
        assert self.__class__.__name__ == self.classId
        assert self._isValidEngine(engine=engine)
        assert isinstance(isFitted, bool)
        assert isVector is None or isinstance(isVector, bool)
        if isFitted:
            assert isinstance(isVector, bool)

        self._engine = engine
        self._isFitted = isFitted
        self._isVector = isVector

    @property
    def isFitted(self) -> bool:
        return self._isFitted

    def fit(self, x: Type.Xy) -> 'SklearnGeneral':
        assert not self._isFitted

        assert isinstance(x, Type.Xy)
        assert 1 <= len(x.shape) <= 2
        assert self._isVector is None
        self._isVector = len(x.shape) == 1

        X = self._fix_input(x=x)
        self._engine.fit(X)
        self._isFitted = True

        return self

    def _fix_input(self, x):
        assert self._isVector is not None
        assert isinstance(x, (np.ndarray, pd.DataFrame, pd.Series))

        if self._isVector:
            assert len(x.shape) == 1
            if isinstance(x, (pd.DataFrame, pd.Series)):
                x = x.values

            X = x.reshape(-1, 1)
        else:
            assert len(x.shape) == 2
            X = x

        assert len(X.shape) == 2
        return X

    def _fix_output(self, X):
        if self._isVector:
            assert len(X.shape) == 2
            if X.shape[1] == 1:
                X = X.reshape(X.shape[0])

        return X

    def transform(self, x: Type.Xy) -> np.ndarray:
        assert self._isFitted
        X = self._fix_input(x=x)
        transX = self._engine.transform(X)
        transX = self._fix_output(transX)
        return transX

    def inverse_transform(self, x: Type.Xy) -> np.ndarray:
        assert self._isFitted
        X = self._fix_input(x=x)
        assert hasattr(self._engine, 'inverse_transform')
        newX = self._engine.inverse_transform(X)
        if self._isVector and len(x.shape) == 1:
            newX = newX.reshape(newX.shape[0])
        return newX

    def save(self, dirPath: str, overwrite: bool = False) -> None:
        assert self.isFitted
        FileSystem.create_folder(dirPath, recreate=overwrite, raise_if_exists=True)

        # save strategy itself
        engineFilePath = os.path.join(dirPath, self._fileName_engine)
        joblib.dump(self._engine, engineFilePath)

        # save info
        self.get_info().save(dirPath=dirPath, overwrite=False)

    @classmethod
    def load(cls, dirPath: str) -> SklearnGeneral:
        info = Info.load(dirPath=dirPath)

        engineFilePath = os.path.join(dirPath, cls._fileName_engine)
        engine = joblib.load(engineFilePath)
        assert cls._isValidEngine(engine=engine)

        assert info.classId == cls.classId
        return cls(
            engine=engine,
            isFitted=info.isFitted,
            isVector=info.attrs['isVector'],
        )

    @classmethod
    def _isValidEngine(cls, engine) -> bool:
        return hasattr(engine, 'fit') and hasattr(engine, 'transform')

    def get_info(self) -> Info:
        return Info(
            classId=self.classId,
            className=self.__class__.__name__,
            version=self.__version__,
            isFitted=self.isFitted,
            attrs=dict(
                isVector=self._isVector,
            ),
        )

    def copy(self) -> 'SklearnGeneral':
        return copy.deepcopy(self)

    def recreate(self) -> 'SklearnGeneral':
        return self.new(engine=sklearn.base.clone(self._engine))


def __init__() -> None:
    nRows = 60
    nCols = 5
    X_np = np.random.rand(nRows, nCols)
    X_pd = pd.DataFrame(X_np, columns=[f'x{i}' for i in range(X_np.shape[1])])
    pcaFields = list(X_pd.columns)[:4]

    ct = ColumnTransformer(
        [
            ("norm1", PCA(n_components=2), pcaFields),
        ],
        remainder="passthrough",
    )

    ct.fit_transform(X_pd)
