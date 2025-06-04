import anre.utils.pandas_.structure.column.type as ct
import anre.utils.pandas_.structure.index.type as it
from anre.utils import testutil
from anre.utils.pandas_.structure.column.column import Column
from anre.utils.pandas_.structure.index.index import Index
from anre.utils.pandas_.structure.structure import Structure


class TestStructure(testutil.TestCase):
    def test_validate_indexesAndColumns_definedAtModuleLocals_shouldNotRaise_ifVariableNames_match_idxAndColNames(
        self,
    ):
        some_index = Index('some_index', it.Int64(), [])
        someString = Column('someString', ct.String(), [])
        someNumber = Column('someNumber', ct.Int64(), [])
        Structure.validate(locals())

    def test_validate_indexesAndColumns_definedAtModuleLocals_shouldRaise_ifVariableName_doesNotMatch_idxName(
        self,
    ):
        some_index1 = Index('some_index', it.Int64(), [])
        with self.assertRaises(Exception):
            Structure.validate(locals())

    def test_validate_indexesAndColumns_definedAtModuleLocals_shouldRaise_ifVariableName_doesNotMatch_colName(
        self,
    ):
        someNumber1 = Column('someNumber', ct.Int64(), [])
        with self.assertRaises(Exception):
            Structure.validate(locals())
