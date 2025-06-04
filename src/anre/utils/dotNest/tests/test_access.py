import numpy as np

from anre.utils import testutil
from anre.utils.dotNest.dotNest import DotNest


class TestAccess(testutil.TestCase):
    def test_accessBasic(self) -> None:
        nest = {
            'a': {
                'b': [0, 1, 2],
                'np': np.array([0, 1, 2]),
                'listList': [[1, 2, 3], [4, 5, 6]],
                'c': [
                    {'d': 3, 'e': 4},
                    {'f': 5, 'g': 6},
                ],
                1: 'oneInt',
                '1': 'oneStr',
            },
            'h': {
                'x': 1,
                'y': 2,
            },
        }

        ### get
        assert DotNest.nestGet(nest=nest, key='h') == {'x': 1, 'y': 2}
        assert DotNest.nestGet(nest=nest, key='h.x') == 1
        assert DotNest.nestGet(nest=nest, key='a.b[1]') == 1
        assert DotNest.nestGet(nest=nest, key='a.np[1]') == 1
        assert DotNest.nestGet(nest=nest, key='a.listList[1]') == [4, 5, 6]
        assert DotNest.nestGet(nest=nest, key='a.listList[1][1]') == 5
        assert DotNest.nestGet(nest=nest, key='a.c[0].d') == 3
        assert DotNest.nestGet(nest=nest, key='a.1') == 'oneStr'
        assert DotNest.nestGet(nest=nest, key='a[1]') == 'oneInt'

        ### set
        DotNest.nestSet(nest=nest, key='a.extra', value=['a', 'b'])
        assert DotNest.nestGet(nest=nest, key='a.extra') == ['a', 'b']
        DotNest.nestSet(nest=nest, key='a.c[2]', value='someValue')
        assert DotNest.nestGet(nest=nest, key='a.c[2]') == 'someValue'
        with self.assertRaises(IndexError):
            DotNest.nestSet(nest=nest, key='a.c[10]', value='otherValue')
        with self.assertRaises(KeyError):
            DotNest.nestSet(nest=nest, key='n.e.w', value='otherValue')
        DotNest.nestSet(nest=nest, key='n.e.w', value='New', extendIfMissing=True)
        assert DotNest.nestGet(nest=nest, key='n.e.w') == 'New'

        ### del
        DotNest.nestDel(nest=nest, key='a.extra')
        assert DotNest.nestGet(nest=nest, key='a.extra', default=None) is None
        with self.assertRaises(KeyError):
            DotNest.nestDel(nest=nest, key='a.extra')
        DotNest.nestDel(nest=nest, key='a.extra', raiseIfMissing=False)

        DotNest.nestDel(nest=nest, key='a.c[0]')
        assert DotNest.nestGet(nest=nest, key='a.c[1]') == 'someValue'

        ### pop
        value = DotNest.nestPop(nest=nest, key='h.y')
        assert value == 2
        with self.assertRaises(KeyError):
            DotNest.nestGet(nest=nest, key='h.y')
        assert DotNest.nestPop(nest=nest, key='h.y', default='aa') == 'aa'
