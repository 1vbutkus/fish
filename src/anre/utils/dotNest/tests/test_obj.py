import numpy as np

from anre.utils import testutil
from anre.utils.dotNest.dotNest import DotNest


class TestObj(testutil.TestCase):
    def test_basic(self) -> None:
        dataNest = {
            'a': {
                'b': [0, 1, 2],
                'tuple': (0, 1, 2),
                'np': np.array([0, 1, 2]),
                'listList': [[1, 2, 3], [4, 5, 6]],
                'c': [
                    {'d': 3, 'e': 4},
                    {'f': 5, 'g': 6},
                ],
                '1': 'oneStr',
            },
            'h': {
                'x': 1,
                'y': 2,
            },
        }

        dotNest = DotNest(dataNest=dataNest)
        assert dotNest.dotDict['a.c[0].d'] == 3
        assert dotNest.get('a.c[0].d') == 3
        assert dotNest['a.c[0].d'] == 3
        assert dotNest['a.c[0]'] == {'d': 3, 'e': 4}

        with self.assertRaises(KeyError):
            dotNest.get('a.c[0].d.someOtherPath')

        with self.assertRaises(KeyError):
            _ = dotNest['a.c[0].d.someOtherPath']

        assert dotNest.get('a.c[0].d.someOtherPath', None) is None

        # not default sep
        dotNest = DotNest(dataNest=dataNest, sep='_')
        assert dotNest.get('a_c[0]_d') == 3
