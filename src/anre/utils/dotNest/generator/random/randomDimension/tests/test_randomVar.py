from anre.utils import testutil
from anre.utils.dotNest.generator.random.randomDimension.randomVar import RandomVar


class TestRandomVar(testutil.TestCase):
    def test_basic(self) -> None:
        RandomVar.new_int(center=2, scale=1)
        RandomVar.new_float(center=2, scale=1)
        RandomVar.new_choice([1, 2, 3])
