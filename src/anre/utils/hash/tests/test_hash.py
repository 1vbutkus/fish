# mypy: disable-error-code="assignment,dict-item"
import pandas as pd

from anre.utils import testutil
from anre.utils.hash.hash import Hash


class TestHash(testutil.TestCase):
    def test_basicFunctions(self) -> None:
        # the same
        obj_1 = {'a': 1, 'b': 2}
        obj_2 = {'a': 1, 'b': 2}
        assert Hash.get_hash(obj_1) == Hash.get_hash(obj_2)

        # reverse
        obj_1_rev = {'b': 2, 'a': 1}
        assert Hash.get_hash(obj_1) == Hash.get_hash(obj_1_rev)

        obj_1 = pd.Series({'a': 1.123456789})
        obj_2 = pd.Series({'a': 1.123456789123})
        assert Hash.get_hash(obj_1) != Hash.get_hash(obj_2)

        obj_1 = dict(a=pd.Series({'a': 1.123456789}))
        obj_2 = dict(a=pd.Series({'a': 1.123456789123}))
        assert Hash.get_hash(obj_1) != Hash.get_hash(obj_2)
        assert Hash.get_dictHash(obj_1) != Hash.get_dictHash(obj_2)
