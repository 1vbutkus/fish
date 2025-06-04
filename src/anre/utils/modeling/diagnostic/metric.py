# mypy: disable-error-code="assignment"
from typing import cast

import numpy as np
import pandas as pd
from sklearn import metrics

from anre.utils.modeling.dataSet.dataSetMl import DataSetMl
from anre.utils.modeling.model.iModel import IModel


class Metric:
    @classmethod
    def get_targetPerformanceDf(cls, model: IModel, dsDict: dict[str, DataSetMl]) -> pd.DataFrame:
        srList = [
            cls.get_targetPerformanceSr_fromModel(model=model, X=ds.X, y=ds.target).rename(name)  # type: ignore[arg-type]
            for name, ds in dsDict.items()
        ]
        targetPerformanceDf = pd.concat(srList, axis=1)
        return targetPerformanceDf

    @classmethod
    def get_targetPerformanceSr_fromModel(
        cls, model: IModel, X: pd.DataFrame | np.ndarray, y: pd.DataFrame | pd.Series | np.ndarray
    ) -> pd.Series:
        yTrue = y
        yPred = model.predict(X)
        assert yTrue.shape == yPred.shape

        if model.isRegression:
            targetPerformanceDict = cls.get_targetPerformanceDict_regression(
                yTrue=yTrue, yPred=yPred
            )
        elif model.isClassification:
            targetPerformanceDict = cls.get_targetPerformanceDict_classification(
                yTrue=yTrue,  # type: ignore[arg-type]
                yPred=yPred,  # type: ignore[arg-type]
            )
        else:
            raise NotImplementedError

        return pd.Series(targetPerformanceDict, dtype=float)

    @classmethod
    def get_targetPerformanceDict_regression(
        cls,
        yTrue: pd.DataFrame | pd.Series | np.ndarray,
        yPred: pd.DataFrame | pd.Series | np.ndarray,
    ) -> dict:
        yTrue, yPred = cls._checkAndTransform_yInputs(yTrue=yTrue, yPred=yPred)

        yTrueSr = pd.Series(yTrue, index=range(len(yTrue)))
        yPredSr = pd.Series(yPred, index=range(len(yPred)))

        scores = {
            'mae': metrics.mean_absolute_error(yTrueSr, yPredSr),
            'rmse': np.sqrt(metrics.mean_squared_error(yTrueSr, yPredSr)),
            'r2': metrics.r2_score(yTrueSr, yPredSr),
            'auc': metrics.roc_auc_score(1 * (yTrueSr >= np.mean(yTrueSr)), yPredSr),
            'corr': yTrueSr.corr(yPredSr, method='pearson'),
            'spearmanr': yTrueSr.corr(yPredSr, method='spearman'),
        }
        return scores

    @classmethod
    def get_targetPerformanceDict_classification(
        cls, yTrue: pd.Series | np.ndarray, yPred: pd.Series | np.ndarray, tr=0.5
    ) -> dict:
        yTrue, yPred = cls._checkAndTransform_yInputs(yTrue=yTrue, yPred=yPred)
        scores = {
            'auc': metrics.roc_auc_score(yTrue, yPred),
            'accuracy': metrics.accuracy_score(yTrue, yPred > tr),
            'f1': metrics.f1_score(yTrue, yPred > tr),
        }
        return scores

    @classmethod
    def get_targetPerformanceReport_regression(cls, yTrue, yPred):
        targetRecs = {
            'mainModel': cls.get_targetPerformanceDict_regression(yTrue=yTrue, yPred=yPred),
            'zeroModel': cls.get_targetPerformanceDict_regression(
                yTrue=yTrue, yPred=yPred * 0 + np.mean(yTrue)
            ),
        }
        return targetRecs

    @staticmethod
    def _checkAndTransform_yInputs(
        yTrue: pd.DataFrame | pd.Series | np.ndarray, yPred: pd.DataFrame | pd.Series | np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        if isinstance(yTrue, (pd.Series, pd.DataFrame)):
            yTrue = yTrue.values
        if isinstance(yPred, (pd.Series, pd.DataFrame)):
            yPred = yPred.values

        assert isinstance(yTrue, np.ndarray)
        assert isinstance(yPred, np.ndarray)

        assert yTrue.shape == yPred.shape
        if len(yTrue.shape) > 1:
            yTrue = yTrue.reshape(-1)
            yPred = yPred.reshape(-1)

        ind = np.isnan(yTrue) | np.isnan(yPred)
        if ind.any():
            yTrue = yTrue[~ind]
            yPred = yPred[~ind]

        assert len(yTrue.shape) == 1
        assert len(yPred.shape) == 1
        assert len(yTrue) == len(yPred)

        return cast(tuple[np.ndarray, np.ndarray], (yTrue, yPred))
