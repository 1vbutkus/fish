import pandas as pd

from anre.utils import testutil
from anre.utils.pandas_.structure.constraint import constraint


class TestConstraint(testutil.TestCase):
    def test_equalConstraints(self) -> None:
        self.assertEqual(constraint.MonoInc(), constraint.MonoInc())
        self.assertEqual(constraint.NotNA(), constraint.NotNA())
        self.assertEqual(constraint.ContainsOnly([1, 2, 3]), constraint.ContainsOnly([1, 2, 3]))
        self.assertNotEqual(constraint.MonoInc(), constraint.NotNA())
        self.assertNotEqual(constraint.ContainsOnly([1, 2, 3]), constraint.ContainsOnly([2, 3, 1]))

    def test_constant_constraint(self) -> None:
        sr = pd.Series([1, 1, 1, 1])
        self.assertTrue(constraint.Constant().check(sr))
