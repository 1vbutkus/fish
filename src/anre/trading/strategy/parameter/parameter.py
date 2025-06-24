import os.path
from typing import Optional

from anre.config.config import config as anre_config
from anre.trading.strategy.brain.brains.base.brainBase import StrategyBrain
from anre.utils.dotNest.dotNest import DotNest
from anre.utils.parameter.parameter import Parameter as ParameterBase


class Parameter(ParameterBase):

    @classmethod
    def new_from_strategy_brain(cls, strategy_brain: StrategyBrain) -> 'Parameter':
        assert isinstance(strategy_brain, StrategyBrain)
        cred = strategy_brain.get_cred()
        paramDict = {
            'strategyLabel': cred.label,
            'configDict': cred.configDict,
            'tagDict': cred.tagDict,
            'comment': cred.comment,
        }
        return cls(paramDict)

    def __init__(self, *params, strategyLabel: Optional[str] = None, skipValidation=False):
        _default = anre_config.path.get_path_to_resource_dir('strategyPredefined', 'default.yaml')
        pathToPredefinedList = [_default]
        if strategyLabel:
            assert isinstance(strategyLabel, str)
            _extraPath = anre_config.path.get_path_to_resource_dir('strategyPredefined', f'{strategyLabel}.yaml')
            if os.path.exists(_extraPath):
                pathToPredefinedList.append(_extraPath)

        super().__init__(*params, pathToPredefined=pathToPredefinedList, skipValidation=True)

        if not skipValidation:
            assert self._validate(paramDotDict=self.paramDotDict, paramDerivedDotDict=self.paramDerivedDotDict)
            if strategyLabel:
                assert self.paramDotDict['strategyLabel'] == strategyLabel, f'Strategy labels is not matching: {self.paramDotDict["strategyLabel"]} vs {strategyLabel}'

    @classmethod
    def _validate(cls, paramDotDict, paramDerivedDotDict) -> bool:
        paramsDict = DotNest.convert_dotDict2nest(paramDotDict)
        assert set(paramsDict) == {'strategyLabel', 'configDict', 'tagDict',
                                   'comment'}, f"params labels must be ['strategyLabel', 'configDict', 'tagDict', 'comment'], but got: {set(paramDotDict)}"
        isinstance(paramsDict['strategyLabel'], str)
        isinstance(paramsDict['configDict'], dict)
        isinstance(paramsDict['tagDict'], dict)
        isinstance(paramsDict['comment'], str)
        assert paramsDict['strategyLabel']
        for key, value in paramsDict['tagDict'].items():
            assert isinstance(key, str)
            assert isinstance(value, str)
        return True


def __dummy__():
    parameter = Parameter('Dummy', strategyLabel='Dummy')
