import unittest

from anre.trading.strategy.brain.brains.dummy.config import Config
from anre.trading.strategy.brain.brains.dummy.dummy import Dummy as DummyStrategyBrain
from anre.trading.strategy.brain.cred import StrategyBrainCred
from anre.trading.strategy.parameter.parameter import Parameter


class TestParameterRandom(unittest.TestCase):
    def test_consistency(self):
        strategy_brain = DummyStrategyBrain.new()
        parameter_from_strategy = Parameter.new_from_strategy_brain(strategy_brain=strategy_brain)
        parameter_from_predefined = Parameter('Dummy', strategyLabel='Dummy')

        assert parameter_from_predefined == parameter_from_strategy

        assert set(parameter_from_predefined.paramDotDict) == set(
            parameter_from_strategy.paramDotDict
        )
        config = Config.new_fromNestDict(nestDict=parameter_from_predefined['configDict'])
        assert isinstance(config, Config)

        cred = strategy_brain.get_cred()
        assert isinstance(cred, StrategyBrainCred)
        cred_dict = cred.to_dict()
        alt_cred = StrategyBrainCred.from_dict(cred_dict)
        assert alt_cred == cred
