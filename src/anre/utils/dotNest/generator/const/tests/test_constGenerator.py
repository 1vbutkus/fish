# mypy: disable-error-code="call-overload"
from anre.utils import testutil
from anre.utils.dotNest.generator.const.constGenerator import ConstGenerator


class TestConstGenerator(testutil.TestCase):
    def test_basic(self) -> None:
        baseParam = {
            'const0_1': 1,
            'const0_2': 1,
            'dict0': {
                'int': 1,
                'float': 2.0,
                'chose': 'abc',
                'extra': 'extra',
            },
        }

        randomGenerator = ConstGenerator.new(
            baseParam=baseParam,
        )
        newParam = randomGenerator.sample()
        assert len(newParam['dict0']['chose']) == 3
        assert isinstance(newParam['dict0']['int'], int)
        assert newParam['dict0']['int'] == 1
        assert newParam['dict0']['float'] == 2.0

        assert newParam == baseParam
