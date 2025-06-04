from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from anre.utils import testutil
from anre.utils.modeling.sklearn_ import utils as sku


class TestSku(testutil.TestCase):
    def test_happyPath(self) -> None:
        model = SVC()
        partPipe = Pipeline([('scaler', StandardScaler())])
        modelPipe = Pipeline([('scaler', StandardScaler()), ('svc', SVC())])

        assert sku.isRegressor(model) is False
        assert sku.isClassifier(model) is True
        assert sku.isRegressor(modelPipe) is False
        assert sku.isClassifier(modelPipe) is True

        assert sku.isSklearnModel(model) is True
        assert sku.isSklearnModel(modelPipe) is True
        assert sku.isSklearnModel(partPipe) is False
