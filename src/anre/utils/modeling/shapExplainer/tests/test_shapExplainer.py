# mypy: disable-error-code="attr-defined"
# TODO: temp hack. Update shap and numba
import warnings

import pytest

warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")
warnings.filterwarnings(
    "ignore",
    message=".*Importing display from IPython.core.display is deprecated since IPython 7.14, please import from IPython display.*",
)
import shap  # noqa: E402

from anre.utils import testutil  # noqa: E402
from anre.utils.modeling.model.leafModel.leafModel import LeafModel  # noqa: E402
from anre.utils.modeling.shapExplainer.shapExplainer import ShapExplainer  # noqa: E402


@pytest.mark.slow
class TestShapExplainer(testutil.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        trainDf, targetObj = shap.datasets.adult()
        mlHp = {
            'num_leaves': 10,
            'max_depth': 10,
            'min_child_samples': 20,
            'n_estimators': 100,
            'min_split_gain': 0.05,
        }

        modelClassification = LeafModel.new_fromClassId(
            classId='LgbmClassificationBinary',
            hp=mlHp,
        )
        modelClassification.fit(trainDf, targetObj)

        modelRegression = LeafModel.new_fromClassId(
            classId='LgbmRegression',
            hp=mlHp,
        )
        modelRegression.fit(trainDf, targetObj * 1)
        models = [modelClassification, modelRegression]

        shap.initjs()
        cls.models = models
        cls.trainDf = trainDf

    def test_happyPath(self) -> None:
        models = self.models
        trainDf = self.trainDf

        for model in models:
            shapExplainer = ShapExplainer.new_fromModel(model=model)
            shapExplainer.set_explanation(inputDf=trainDf.sample(100))
            for mode in ['ecdf', 'raw']:
                pass

                # TODO: padaryti tastavima su grafiku braizymais
                # shapExplainer.plot_bar(mode=mode)
                # shapExplainer.plot_beeswarm(mode=mode)
                # shapExplainer.plot_heatmap(mode=mode)
                # shapExplainer.plot_force_all(mode=mode)
                # shapExplainer.plot_force_all(mode=mode)
                # shapExplainer.plot_scatter(field='Age', mode=mode)
                #
                # shapExplainer.plot_dependence(mainField='Age', interactionField=None, mode=mode)
                # shapExplainer.plot_dependence(mainField='Age', interactionField='Workclass', mode=mode)
                #
                # shapExplainer.plot_force_fromIdx([2, 3, 4], mode=mode)
                # shapExplainer.plot_force_fromIdx(2, mode=mode)
                # shapExplainer.plot_waterfall_fromIdx(2, mode=mode)
