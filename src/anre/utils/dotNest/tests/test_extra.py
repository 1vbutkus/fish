import numpy as np
import pandas as pd

from anre.utils import testutil
from anre.utils.dotNest.dotNest import DotNest


class TestExtra(testutil.TestCase):
    def test_misc(self) -> None:
        nest = {
            'a': {
                'b': [0, 1, 2],
                'np': np.array([0, 1, 2]),
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
        assert DotNest.get_mapRawKeys(nest) == {
            1,
            '1',
            'a',
            'b',
            'c',
            'd',
            'e',
            'f',
            'g',
            'h',
            'np',
            'x',
            'y',
        }
        assert DotNest.get_countValues(nest) == 12

    def test_collect_values_fromNests(self) -> None:
        nests = [
            {'a': 1, 'b': {'c': 10, 'd': [1, 20]}},
            {'a': 1, 'b': {'c': 11, 'd': [2, 21]}},
            {'a': 1, 'b': {'c': 12, 'd': [3]}},
        ]
        assert DotNest.collect_values_fromNests(dotKey='b.c', nestDicts=nests) == [10, 11, 12]
        assert DotNest.collect_values_fromNests(dotKey='b.d[0]', nestDicts=nests) == [1, 2, 3]
        with self.assertRaises(IndexError):
            assert DotNest.collect_values_fromNests(dotKey='b.d[1]', nestDicts=nests)
        assert DotNest.collect_values_fromNests(dotKey='b.d[1]', nestDicts=nests, default=-99) == [
            20,
            21,
            -99,
        ]

    def test_compare(self) -> None:
        aNest = {'a': 1, 'b': {'c': 10, 'd': [1, 20]}, 'nan': np.nan, 'None': None}
        bNest = {'a': 1, 'b': {'c': 10, 'd': [1, -99]}, 'nan': np.nan, 'None': None, 'extra': 0}
        compareDf = DotNest.compare(aNest, aNest)
        assert isinstance(compareDf, pd.DataFrame)
        assert compareDf.empty

        compareDf = DotNest.compare(aNest, bNest)
        assert set(compareDf.index) == {'b.d[1]', 'extra'}
