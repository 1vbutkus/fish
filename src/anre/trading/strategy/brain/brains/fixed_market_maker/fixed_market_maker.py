from typing import Any, Dict, Optional
import logging

from anre.trading.monitor.base import BaseMonitor
from anre.trading.strategy.action.actions.base import StrategyAction
from anre.trading.strategy.brain.brains.base.brainBase import StrategyBrain
from anre.trading.strategy.brain.brains.fixed_market_maker.config import Config
from anre.trading.strategy.action.patience.patience import Patience
from anre.trading.strategy.action.factory import Factory as ActionFactory


class FixedMarketMaker(StrategyBrain):
    __version__ = "0.0.0.0"
    configClass = Config
    strategyLabel = 'FixedMarketMaker'

    def __init__(self, config, tag_dict: Optional[Dict[str, str]] = None, comment: str = ''):
        super().__init__(config=config, tag_dict=tag_dict, comment=comment)
        self._monitor: Optional[BaseMonitor] = None
        self._patience: Optional[Patience] = None
        self._logger = logging.getLogger(__name__)

    def set_objects(self, monitor: BaseMonitor, **kwargs):
        assert not self.is_setting_object_finished
        assert isinstance(monitor, BaseMonitor)
        self._monitor = monitor
        self._patience = Patience()
        self.is_setting_object_finished = True

    def get_report_dict(self) -> Dict[str, Any]:
        return {}

    def update_state_and_get_action_list(self, action_freeze: bool) -> list[StrategyAction]:
        assert self.is_setting_object_finished

        if action_freeze:
            return []

        # TODO: monitoriu turi sukti aksteciau. Teikes patikrinti
        self._monitor.iteration()


        monitor = self._monitor
        patience = self._patience
        config: Config = self._config

        step1000 = config.step1000 if config.step1000 is not None else monitor.get_tick1000()



        # monitor.get_top_level_price_dict()
        bool_market_cred = monitor.market_info_parser.bool_market_cred
        public_market_order_book, house_order_book, net_market_order_book = (
            monitor.get_market_order_books()
        )
        bid1000, ask1000 = net_market_order_book.get_main_asset_best_price1000s()

        target_long_price1000 = bid1000 - step1000 * (config.target_base_step_level + max(0, config.target_skew_step_level))
        target_long_price1000 = min(target_long_price1000, ask1000 - step1000)
        target_short_price1000 = ask1000 + step1000 * (config.target_base_step_level + min(0, config.target_skew_step_level))
        target_short_price1000 = max(target_short_price1000, bid1000 + step1000)
        if target_long_price1000 >= target_short_price1000:
            msg = f'The target long price {target_long_price1000} >= target short price {target_short_price1000}. This is not allowed. The strategy will not be executed.'
            self._logger.warning(msg)
            return []

        # find tolerance range
        keep_long_price1000_range = [target_long_price1000 - config.keep_offset_deep_level * step1000, target_long_price1000 + config.keep_offset_shallow_level * step1000]
        keep_short_price1000_range = [target_short_price1000 - config.keep_offset_deep_level * step1000, target_short_price1000 + config.keep_offset_shallow_level * step1000]

        ### check if already have the order
        is_long_order_OK = False
        is_short_order_OK = False
        cancel_action_list = []
        for order_dict in monitor.get_house_order_dict_list():
            if order_dict['asset_id'] == bool_market_cred.main_asset_id:
                main_price1000 = order_dict['price1000']
            elif order_dict['asset_id'] == bool_market_cred.counter_asset_id:
                main_price1000 = 1000 - order_dict['price1000']
            else:
                raise ValueError(f'Unknown asset_id {order_dict["asset_id"]}')
            if order_dict['bool_side'] == 'LONG':
                if keep_long_price1000_range[0] <= main_price1000 <= keep_long_price1000_range[1] and order_dict['remaining_size1000'] == int(round(1000 * config.share_size)):
                    is_long_order_OK = True
                else:
                    action = ActionFactory.new_cancel_orders_by_ids(order_ids=[order_dict['id']])
                    cancel_action_list.append(action)
            elif order_dict['bool_side'] == 'SHORT':
                if keep_short_price1000_range[0] <= main_price1000 <= keep_short_price1000_range[1] and order_dict['remaining_size1000'] == int(round(1000 * config.share_size)):
                    is_short_order_OK = True
                else:
                    action = ActionFactory.new_cancel_orders_by_ids(order_ids=[order_dict['id']])
                    cancel_action_list.append(action)

        ### place
        place_action_list = []
        if not is_long_order_OK:
            action = ActionFactory.new_place_bool_market_order(
                main_asset_id=bool_market_cred.main_asset_id,
                counter_asset_id=bool_market_cred.counter_asset_id,
                main_price1000=target_long_price1000,
                size=config.share_size,
                bool_side='LONG',
            )
            place_action_list.append(action)
        if not is_short_order_OK:
            action = ActionFactory.new_place_bool_market_order(
                main_asset_id=bool_market_cred.main_asset_id,
                counter_asset_id=bool_market_cred.counter_asset_id,
                main_price1000=target_short_price1000,
                size=config.share_size,
                bool_side='SHORT',
            )
            place_action_list.append(action)

        ### patience
        patience.start_iteration()
        for action in cancel_action_list:
            patience.proc_actionWish(action=action, iterationRequre=0)
        for action in place_action_list:
            patience.proc_actionWish(action=action, iterationRequre=config.place_patience)
        action_list = patience.finish_iteration()

        return action_list

def __dummy__():
    pass








