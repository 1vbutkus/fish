from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn import metrics
from sklearn.inspection import permutation_importance

from anre.utils.modeling.model.iPredictModel import IPredictModel


class ModelDiagnostic:
    @classmethod
    def new_fromSklearn(cls, model):
        assert "'sklearn." in str(type(model))
        assert sklearn.base.is_regressor(model) or sklearn.base.is_classifier(model), (
            "Model should be regressor or classifier"
        )
        _ = sklearn.base.is_regressor(model)

    def __init__(
        self,
        model: IPredictModel,
        isRegression: bool,
        defaultDataDf: pd.DataFrame,
        yField: str,
        xFields=None,
        prepInputFun=None,
    ):
        self.model = model
        self._defaultDataDf = defaultDataDf
        self._yField = yField
        self._isRegression = isRegression

        if xFields is None:
            xFields = list(defaultDataDf.head().drop(columns=[yField]).columns)
        self._xFields = xFields

        if prepInputFun is None:
            if xFields is None:
                prepInputFun = self._identity
            else:
                prepInputFun = self._selectXFields
        self._prepInputFun = prepInputFun

    @staticmethod
    def _identity(df):
        return df

    def _selectXFields(self, df):
        return df[self._xFields]

    def _getDataDf(self, dataDf):
        if dataDf is None:
            return self._defaultDataDf
        else:
            return dataDf

    def _get_y(self, dataDf):
        return dataDf[self._yField]

    def _get_X(self, dataDf):
        return self._prepInputFun(dataDf)

    def predict(self, dataDf=None, **kwargs: Any):
        dataDf = self._getDataDf(dataDf=dataDf)
        X = self._get_X(dataDf)
        return self.model.predict(X)

    def predictMain(self, dataDf=None, **kwargs: Any):
        return self.predict(dataDf=dataDf, **kwargs)

    def get_confusionMatrix(self, dataDf=None, tr=0.5, normalize: bool = True, **kwargs: Any):
        """return matrix actual vs predicted"""

        dataDf = self._getDataDf(dataDf=dataDf)

        preds_prob = self.predict(dataDf=dataDf, **kwargs)
        preds = (preds_prob > tr) * 1
        y_true = self._get_y(dataDf=dataDf)

        tb = pd.crosstab(
            y_true,
            preds,
            rownames=['actual'],
            colnames=['preds'],
            margins=True,
            normalize=normalize,
        )
        tb.at['All', 'All'] = np.diag(tb).sum() - tb.at['All', 'All']

        return tb

    def get_permutationImportance(
        self, dataDf=None, scoring=None, n_repeats=5, n_jobs=None, random_state=None
    ):
        dataDf = self._getDataDf(dataDf=dataDf)
        y = self._get_y(dataDf=dataDf)
        X = self._get_X(dataDf=dataDf)
        permImpDict = permutation_importance(
            self.model,
            X,
            y,
            scoring=scoring,
            n_repeats=n_repeats,
            n_jobs=n_jobs,
            random_state=random_state,
        )
        permImpSr = pd.Series(permImpDict['importances_mean'], index=X.columns).sort_values(
            ascending=False
        )
        return permImpSr

    def get_partialDependency(self, field, values=None, dataDf=None):
        dataDf = self._getDataDf(dataDf=dataDf).copy()

        if values is None:
            ser = dataDf[field]
            if ser.dtype.name == 'category':
                values = ser.cat.categories
            elif ser.dtype.name in ['O', 'object']:
                values = ser.unique()
            else:
                values = ser.quantile(np.arange(0.00, 1.0001, 0.02)).unique()

        resArr = np.empty((len(values), 2))
        for idx, value in enumerate(values):
            dataDf[field] = value
            pred = self.predictMain(dataDf=dataDf)
            resArr[idx, 0] = pred.mean()
            resArr[idx, 1] = pred.std()

        resDf = pd.DataFrame(resArr, index=values, columns=['mean', 'std'])
        return resDf

    def _guess_varType(self, field):
        dataDf = self._getDataDf(dataDf=None)
        ser = dataDf[field]
        if ser.dtype.name == 'category':
            return 'category'
        elif ser.dtype.name in ['O', 'object']:
            return 'category'
        else:
            nu = ser.nunique()
            if (nu < 20) and (len(ser) / nu > 10):
                return 'category'
        return 'numeric'

    def plot_roc(self, dataDf=None, pos_label=1, **kwargs: Any):
        dataDf = self._getDataDf(dataDf=dataDf)
        y_score = self.predict_proba(dataDf=dataDf, **kwargs)  # type: ignore[attr-defined]
        y_true = self._get_y(dataDf=dataDf)
        fpr, tpr, tr = metrics.roc_curve(y_true=y_true, y_score=y_score, pos_label=pos_label)
        score = metrics.auc(fpr, tpr)

        fig, ax = plt.subplots()
        ax.plot(fpr, tpr, color='darkorange', label='ROC')
        ax.plot([0, 1], [0, 1], color='navy', linestyle='--')
        ax.set_xlim((0.0, 1.0))
        ax.set_ylim((0.0, 1.05))
        ax.set_title('ROC curve (area = %0.2f)' % score)
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        return ax

    def plot_positeveRates(self, dataDf=None, pos_label=1, **kwargs: Any):
        dataDf = self._getDataDf(dataDf=dataDf)
        y_score = self.predict_proba(dataDf=dataDf, **kwargs)  # type: ignore[attr-defined]
        y_true = self._get_y(dataDf=dataDf)
        fpr, tpr, tr = metrics.roc_curve(y_true=y_true, y_score=y_score, pos_label=pos_label)
        score = metrics.auc(fpr, tpr)

        fig, ax = plt.subplots()
        ax.plot(tr, tpr, label='tpr')
        ax.plot(tr, 1 - fpr, label='1-fpr')
        ax.set_xlim((0.0, 1.0))
        ax.set_ylim((0.0, 1.05))
        ax.set_title('ROC curve (area = %0.2f)' % score)
        ax.set_xlabel('Treashold')
        ax.set_ylabel('Positive Rate')
        ax.legend(loc="lower right")
        return ax

    def _plot_standart_line(self, x, y, ax):
        return ax.plot(x, y, color='red', linewidth=2)

    def _plot_standart_init(self, ax=None, xlim=None, ylim=None, title=None):
        if ax is None:
            fig, ax = plt.subplots()
        return ax

    def _plot_standart_setAttributes(self, ax=None, xlim=None, ylim=None, title=None):
        if ax is None:
            fig, ax = plt.subplots()
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)
        if title is not None:
            ax.set_title(title)
        return ax
