# mypy: disable-error-code="dict-item,var-annotated"
import numpy as np

from anre.utils import testutil
from anre.utils.dotNest.dotNest import DotNest


class TestTransform(testutil.TestCase):
    def test_roundTrip(self) -> None:
        nest = {
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

        nest2 = DotNest.convert_dotDict2nest(nest)
        assert nest2 is not nest
        assert nest2 == nest

        dotDict = DotNest.convert_nest2dotDict(nest)
        assert 'a.c[0].d' in dotDict.keys()
        assert 'a.c.[0].d' not in dotDict.keys()
        with self.assertRaises(AssertionError):
            _ = DotNest.convert_nest2dotDict(dotDict)
        nestDict = DotNest.convert_dotDict2nest(dotDict)
        assert nest == nestDict

        dotDict = DotNest.convert_nest2dotDict(nest, sep='-')
        assert 'a-c[0]-d' in dotDict.keys()
        nestDict = DotNest.convert_dotDict2nest(dotDict, sep='-')
        assert nest == nestDict

        dotDict = DotNest.convert_nest2dotDict(nest, listToMap=False)
        assert 'a.c[0].d' not in dotDict.keys()
        assert 'a.c.[0].d' not in dotDict.keys()
        assert 'a.c' in dotDict.keys()
        nestDict = DotNest.convert_dotDict2nest(dotDict)
        assert nest == nestDict

    def test_exception_keyMustBeStr(self) -> None:
        with self.assertRaises(AssertionError):
            DotNest.convert_nest2dotDict({0: 0})

    def test_exception_keyShouldNotHaveSep(self) -> None:
        with self.assertRaises(AssertionError):
            DotNest.convert_nest2dotDict({'a.b': 0})

    def test_convertDotKeyWithinList(self) -> None:
        mixtNest = [
            {
                'activeBrain': 'passive',
                'passiveConfig.cancelAllOrders': True,
            }
        ]
        nest = DotNest.convert_dotDict2nest(mixtNest)
        assert nest == [{'activeBrain': 'passive', 'passiveConfig': {'cancelAllOrders': True}}]

    def test_exception_mixedCaseShouldNotShadow(self) -> None:
        nest = {
            'a': {
                'b': {
                    'c': 1,
                    'e': 10,
                }
            },
            'a.b': 2,
        }
        with self.assertRaises(AssertionError):
            DotNest.convert_dotDict2nest(nest)

    def test_list(self) -> None:
        nest = [
            {'a': 1},
            {'a': 1},
            {'a': 1},
        ]

        dotDict = DotNest.convert_nest2dotDict(nest)
        assert dotDict == {'[0].a': 1, '[1].a': 1, '[2].a': 1}
        nestDict = DotNest.convert_dotDict2nest(dotDict)
        assert nest == nestDict

    def test_mixedCase_happyPath(self) -> None:
        nest = {
            'a': {
                'b': {
                    'c': 1,
                    'e': 10,
                }
            },
            'a.b': 2,
        }
        with self.assertRaises(AssertionError):
            _ = DotNest.convert_dotDict2nest(nest)

    def test_doNotChangeEmptyType(self) -> None:
        # nest = {
        # }
        # assert nest == DotNest.convert_dotDict2nest(nest)
        #
        # nest = {
        #     'a': {},
        # }
        # assert nest == DotNest.convert_dotDict2nest(nest)

        nest = {
            'a.b.c[0]': {},
        }
        DotNest.convert_dotDict2nest(nest)

    def test_updateNest(self) -> None:
        nest = {
            'a': {
                'b': {
                    'c': 1,
                    'e': 10,
                }
            },
        }

        updateMap = {'a.b.c': 3}
        DotNest.update_nest(nest=nest, updateMap=updateMap)
        assert nest['a']['b']['c'] == 3

        updateMap = {'a.b': {'d': 7}}
        DotNest.update_nest(nest=nest, updateMap=updateMap)
        assert nest['a']['b'] == {'d': 7}

        # create path on the fly, i.e. extendIfMissing
        updateMap = {'a.b.c.d': 'extendedPath'}
        DotNest.update_nest(nest=nest, updateMap=updateMap, extendIfMissing=True)
        assert nest['a']['b']['c'] == {'d': 'extendedPath'}

        updateMap = {'x.y.z': 3}
        with self.assertRaises(KeyError):
            DotNest.update_nest(nest=nest, updateMap=updateMap)
