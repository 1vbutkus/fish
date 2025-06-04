from anre.utils import testutil
from anre.utils.modeling.model.hyperParameters.hpCatalog import HpCatalog


class TestHpCatalog(testutil.TestCase):
    def test_happyPath(self) -> None:
        hpCatalog = HpCatalog.new_lgbm()
        hpKwargs = hpCatalog.get_hpKwargs(a=1)
        self.assertIsInstance(hpKwargs, dict)
        assert hpKwargs['a'] == 1
