from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from anre.trading.strategy.action.actions.base import StrategyAction
from anre.trading.strategy.brain.brains.base.configBase import StrategyConfigBase
from anre.trading.strategy.brain.cred import StrategyBrainCred


class StrategyBrain(ABC):
    __version__ = '0.0.0.0'
    configClass: Optional[Type[StrategyConfigBase]] = None
    label = 'StrategyBrainBase'

    @classmethod
    def new(
        cls, config=None, tag_dict: Optional[Dict[str, str]] = None, comment: str = '', **kwargs
    ) -> 'StrategyBrain':
        if config is None:
            assert cls.configClass is not None, (
                'configClass is not defined. Please define config of the child class.'
            )
            config = cls.configClass.new_fromNestDict(nestDict=kwargs)
        else:
            assert not kwargs

        return cls(
            config=config,
            tag_dict=tag_dict,
            comment=comment,
        )

    @classmethod
    def new_from_config_dict(
        cls,
        config_dict: Dict[str, Any],
        tag_dict: Optional[Dict[str, str]] = None,
        comment: str = '',
    ) -> 'StrategyBrain':
        config = cls.configClass.new_fromNestDict(nestDict=config_dict)
        instance = cls(config=config, tag_dict=tag_dict, comment=comment)
        return instance

    def __init__(self, config, tag_dict: Optional[Dict[str, str]] = None, comment: str = ''):
        tag_dict = {} if tag_dict is None else tag_dict
        assert self.configClass is not None, (
            'configClass is not defined. Please define config of the child class.'
        )
        assert isinstance(config, StrategyConfigBase)
        assert isinstance(config, self.configClass)
        assert isinstance(tag_dict, dict)
        assert isinstance(comment, str)

        self.is_setting_object_finished: bool = False
        self._config = config
        self._tag_dict: Dict[str, str] = tag_dict
        self._comment: str = comment

    def set_objects(self, **kwargs):
        assert not self.is_setting_object_finished
        self.is_setting_object_finished = True

    def get_config(self):
        return self._config

    def set_config(self, config):
        assert isinstance(config, self.configClass)
        self._config = config

    def update_config(self, update_dict: Dict[str, Any] = None, **kwargs):
        newConfig = self._config.new_update(updateDict=update_dict, **kwargs)
        self.set_config(config=newConfig)

    def get_cred(self) -> StrategyBrainCred:
        return StrategyBrainCred(
            className=self.__class__.__name__,
            version=self.__version__,
            label=self.label,
            configDict=self._config.to_dict(),
            tagDict=self._tag_dict,
            comment=self._comment,
        )

    @abstractmethod
    def get_report_dict(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_state_and_get_action_list(self, action_freez: bool) -> list[StrategyAction]:
        """

        :param action_freez: bool, if True, then no action will be executed, thus strategy should not generate new. But it canupdate internalstate and think.
        :return:
        """
        pass
