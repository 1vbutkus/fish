# mypy: disable-error-code="union-attr"
# TODO: temp hack. Update shap and numba
import warnings
from typing import Any, Callable

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")
import shap  # noqa: E402

from anre.utils.modeling.model.leafModel.leafModel import LeafModel  # noqa: E402


class ShapExplainer:
    @classmethod
    def new_fromModel(cls, model: LeafModel):
        inputPrepareFun = model.get_xDf
        engine = model.coreModel.get_engine()
        predScaleFn = model.outputTransformer.transform
        classId = model.coreModel.get_info().classId
        if classId == 'LgbmClassificationBinary':
            explainer = shap.TreeExplainer(engine)
        elif classId == 'LgbmRegression':
            explainer = shap.TreeExplainer(engine)
            # explainer = shap.Explainer(mlModel)
        else:
            raise NotImplementedError(f'classId(`{classId}`) is not supported yet.')

        return cls(
            explainer=explainer,
            inputPrepareFun=inputPrepareFun,
            predScaleFn=predScaleFn,
        )

    def __init__(
        self, explainer: shap.Explainer, inputPrepareFun: Callable, predScaleFn: Callable
    ) -> None:
        if predScaleFn is None:

            def predScaleFn(x):
                return x

        if inputPrepareFun is None:

            def inputPrepareFun(x):
                return x

        assert isinstance(explainer, shap.Explainer)
        assert callable(inputPrepareFun)
        assert callable(predScaleFn)

        self._explanation_raw: shap.Explanation | None = None
        self._explanation_ecdf: shap.Explanation | None = None
        self._preparedInputDf: pd.DataFrame | None = None

        self._explainer = explainer
        self._inputPrepareFun = inputPrepareFun
        self._predScaleFn = predScaleFn

    @staticmethod
    def sample_inputDf(inputDf: pd.DataFrame, n=10000, mode='random') -> pd.DataFrame:
        if mode == 'random':
            assert n > 1
            if inputDf.shape[0] >= n:
                return inputDf.sample(n, replace=False)
            else:
                return inputDf.sample(n, replace=True)
        else:
            raise NotImplementedError

    @staticmethod
    def _convert_explanationToDict(explanation: shap.Explanation) -> dict:
        explanationDict = dict(
            values=explanation.values,
            base_values=explanation.base_values,
            data=explanation.data,
            display_data=explanation.display_data,
            instance_names=explanation.instance_names,
            feature_names=explanation.feature_names,
            output_names=explanation.output_names,
            output_indexes=explanation.output_indexes,
            lower_bounds=explanation.lower_bounds,
            upper_bounds=explanation.upper_bounds,
        )
        return explanationDict

    @classmethod
    def _recreate_explanation(
        cls, explanation: shap.Explanation, values=None, base_values=None, **kwargs
    ) -> shap.Explanation:
        kwargsFromExplanation = cls._convert_explanationToDict(explanation=explanation)
        if values is not None:
            kwargs['values'] = values
        if base_values is not None:
            kwargs['base_values'] = base_values
        kwargsFromExplanation.update(kwargs)
        return shap.Explanation(**kwargsFromExplanation)

    @classmethod
    def _get_transformedExplanation(
        cls, transformFun, explanation: shap.Explanation
    ) -> shap.Explanation:
        base_values = transformFun(explanation.base_values)
        values = np.array([
            transformFun(shapValue_i.values + shapValue_i.base_values)
            - transformFun(shapValue_i.base_values)
            for shapValue_i in explanation
        ])
        transformedExplanation = cls._recreate_explanation(
            explanation=explanation, values=values, base_values=base_values
        )
        return transformedExplanation

    def set_explanation(self, inputDf: pd.DataFrame) -> None:
        assert inputDf.shape[0] > 0

        preparedInputDf = self._inputPrepareFun(inputDf)
        explanation = self._explainer(preparedInputDf)

        if len(explanation.shape) == 2:
            pass
        elif len(explanation.shape) == 3:
            explanation = explanation[:, :, -1]
        else:
            raise ValueError

        self._explanation_ecdf = self._get_transformedExplanation(
            transformFun=self._predScaleFn, explanation=explanation
        )
        self._explanation_raw = explanation
        self._preparedInputDf = preparedInputDf

    def get_importanceSr(self, mode='raw'):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            return self._get_importanceSr(explanation=self._explanation_ecdf)
        elif mode == 'raw':
            return self._get_importanceSr(explanation=self._explanation_raw)
        else:
            raise NotImplementedError

    def plot_bar(self, mode='raw', **kwargs: Any):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            return shap.plots.bar(self._explanation_ecdf, **kwargs)
        elif mode == 'raw':
            return shap.plots.bar(self._explanation_raw, **kwargs)
        else:
            raise NotImplementedError

    def plot_beeswarm(self, mode='raw', **kwargs: Any):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            return shap.plots.beeswarm(self._explanation_ecdf, **kwargs)
        elif mode == 'raw':
            return shap.plots.beeswarm(self._explanation_raw, **kwargs)
        else:
            raise NotImplementedError

    def plot_heatmap(self, mode='raw', instanceOrder='original', **kwargs: Any):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            explanation = self._explanation_ecdf
        elif mode == 'raw':
            explanation = self._explanation_raw
        else:
            raise NotImplementedError

        if isinstance(instanceOrder, str):
            if instanceOrder == 'original':
                instance_order = np.array(range(self._preparedInputDf.shape[0]))
            elif instanceOrder == 'sum':
                instance_order = np.argsort(explanation.values.sum(1))
            elif instanceOrder == 'default':
                instance_order = None
            else:
                raise NotImplementedError
        else:
            instance_order = instanceOrder

        if instance_order is None:
            return shap.plots.heatmap(explanation, **kwargs)
        else:
            return shap.plots.heatmap(explanation, instance_order=instance_order, **kwargs)

    def plot_force_all(self, mode='raw'):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            return shap.force_plot(
                base_value=float(self._explanation_ecdf.base_values[0]),
                shap_values=self._explanation_ecdf.values,
                features=self._preparedInputDf,
            )
        elif mode == 'raw':
            return shap.force_plot(
                base_value=float(self._explanation_raw.base_values[0]),
                shap_values=self._explanation_raw.values,
                features=self._preparedInputDf,
            )
        else:
            raise NotImplementedError

    def plot_scatter(self, field, mode='raw', **kwargs: Any):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            return shap.plots.scatter(self._explanation_ecdf[:, field], **kwargs)  # type: ignore[index]
        elif mode == 'raw':
            return shap.plots.scatter(self._explanation_raw[:, field], **kwargs)  # type: ignore[index]
        else:
            raise NotImplementedError

    def plot_dependence(
        self, mainField: str, interactionField: str | None = None, mode='raw', **kwargs
    ):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'
        if mode == 'ecdf':
            return shap.dependence_plot(
                mainField,
                self._explanation_ecdf.values,
                self._preparedInputDf,
                interaction_index=interactionField,
                **kwargs,
            )
        elif mode == 'raw':
            return shap.dependence_plot(
                mainField,
                self._explanation_raw.values,
                self._preparedInputDf,
                interaction_index=interactionField,
                **kwargs,
            )
        else:
            raise NotImplementedError

    def plot_force_fromIdx(self, idx, mode='raw'):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            return shap.plots.force(self._explanation_ecdf[idx])
        elif mode == 'raw':
            return shap.plots.force(self._explanation_raw[idx])
        else:
            raise NotImplementedError

    def plot_waterfall_fromIdx(self, idx, mode='raw'):
        assert self._preparedInputDf is not None, 'Pleas use self.set_explanation'

        if mode == 'ecdf':
            return shap.plots.waterfall(self._explanation_ecdf[idx])
        elif mode == 'raw':
            return shap.plots.waterfall(self._explanation_raw[idx])
        else:
            raise NotImplementedError

    @staticmethod
    def _get_importanceSr(explanation) -> pd.Series:
        shapValues = explanation.values
        columns = explanation.feature_names
        shapValuesDf = pd.DataFrame(shapValues, columns=columns)
        importanceSr = shapValuesDf.abs().mean().sort_values(ascending=False)
        return importanceSr
