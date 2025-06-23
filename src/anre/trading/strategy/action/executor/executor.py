from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.master_client import MasterClient
from anre.trading.strategy.action.actions.base import StrategyAction
from anre.trading.strategy.action.actions.cancel_orders_by_market import CancelOrdersByMarket
from anre.trading.strategy.action.actions.place_direct_order import PlaceDirectOrder


class StrategyActionExecutor:
    def __init__(self) -> None:
        self._clob_client: ClobClient = MasterClient.get_clob_client()

    def execute_actions(self, action_list: list[StrategyAction]):
        action_list_dict = self._get_action_list_dict_by_class(action_list=action_list)

        for cls_name, action_list in action_list_dict.items():
            if cls_name == 'CancelOrdersByMarket':
                self._execute_cancel_orders_by_market(action_list=action_list)

            elif cls_name == 'CancelOrdersById':
                raise NotImplementedError

            elif cls_name == 'PlaceDirectOrder':
                self._execute_place_direct_order(action_list=action_list)

            else:
                raise ValueError(f'Unknown action class: {cls_name}')

    @staticmethod
    def _get_action_list_dict_by_class(
        action_list: list[StrategyAction],
    ) -> dict[str, list[StrategyAction]]:
        assert all([isinstance(item, StrategyAction) for item in action_list])

        action_list_dict = {}
        for action in action_list:
            cls_name = action.__class__.__name__
            if cls_name not in action_list_dict:
                action_list_dict[cls_name] = []
            action_list_dict[cls_name].append(action)

        assert sum([len(el) for el in action_list_dict.values()]) == len(action_list)
        return action_list_dict

    def _execute_cancel_orders_by_market(self, action_list: list[StrategyAction]):
        for action in action_list:
            assert isinstance(action, CancelOrdersByMarket)
            # mark star
            resp = self._clob_client.cancel_orders_by_market(
                condition_id=action.condition_id,
                asset_id=action.asset_id,
            )
            # mark state

    def _execute_place_direct_order(self, action_list: list[StrategyAction]):
        for action in action_list:
            assert isinstance(action, PlaceDirectOrder)
            # mark star
            resp = self._clob_client.place_order(
                token_id=action.token_id,
                price=action.price,
                size=action.size,
                side=action.side,
                order_type=action.order_type,
            )
            # mark state
