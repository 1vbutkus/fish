import anre.utils.pandas_.structure.index.type as it
from anre.utils import testutil
from anre.utils.pandas_.structure.index.index import Index


class TestIndex(testutil.TestCase):
    def test_indexNameShouldEndWithUnderscoreIndexSuffix(self) -> None:
        _ = Index(name='intIdx_index', type=it.Int64())

        with self.assertRaises(AssertionError):
            _ = Index(name='intIdx', type=it.Int64())
