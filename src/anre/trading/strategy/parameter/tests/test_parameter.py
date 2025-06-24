import unittest

from anre.trading.strategy.parameter.parameter import Parameter, ParameterBase


class TestParameterBase(unittest.TestCase):

    def test_dummy_smoke(self):
        parameter = Parameter('Dummy', strategyLabel='Dummy')
        assert isinstance(parameter, Parameter)
        assert isinstance(parameter, ParameterBase)

        with self.assertRaises(AssertionError):
            _ = Parameter('NotDummy', strategyLabel='Dummy')
