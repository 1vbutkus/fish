from anre.utils import testutil
from anre.utils.dotNest.generator.random.randomDimension.creator import Creator


class TestRandomGenerator(testutil.TestCase):
    def test_basic(self) -> None:
        _ = Creator.new(
            dotPath='some.path',
            dtype='choice',
            elems=[1, 2, 3],
        )

        _ = Creator.new(
            dotPath='some.path',
            dtype='choice',
            elems=[1, 2, 3],
            center=None,
        )

        _ = Creator.new(
            dotPath='some.path',
            dtype='int',
            center=0,
            scale=10,
        )
        _ = Creator.new(
            dotPath='some.path',
            dtype='int',
            center=0,
            scale=10,
            elems=None,
        )
