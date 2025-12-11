from anre.connection.polymarket.api.clob import ClobClient
from anre.connection.polymarket.master_client import MasterClient
from anre.trading.strategy.action.actions.atomic.cancel_orders_by_ids import CancelOrdersByIds
from anre.trading.strategy.action.actions.atomic.cancel_orders_by_market import CancelOrdersByMarket
from anre.trading.strategy.action.actions.atomic.place_direct_order import PlaceDirectOrder
from anre.trading.strategy.action.actions.base import StrategyAtomicAction


class StrategyActionExecutor:
    def __init__(self) -> None:
        self._clob_client: ClobClient = MasterClient().get_clob_client()

    def execute_actions(self, action_list: list[StrategyAtomicAction]):
        if not all([action.is_atomic for action in action_list]):
            bad_actions = [action for action in action_list if not action.is_atomic]
            raise ValueError(f'Some actions are not atomic: {bad_actions}')

        action_list_dict = self._get_action_list_dict_by_class(action_list=action_list)
        for cls_name, action_list in action_list_dict.items():
            if cls_name == 'CancelOrdersByMarket':
                self._execute_cancel_orders_by_market(action_list=action_list)

            elif cls_name == 'CancelOrdersByIds':
                self._execute_cancel_orders_by_ids(action_list=action_list)

            elif cls_name == 'PlaceDirectOrder':
                self._execute_place_direct_order(action_list=action_list)

            else:
                raise ValueError(f'Unknown action class: {cls_name}')

    @staticmethod
    def _get_action_list_dict_by_class(
        action_list: list[StrategyAtomicAction],
    ) -> dict[str, list[StrategyAtomicAction]]:
        assert all([isinstance(item, StrategyAtomicAction) for item in action_list])

        action_list_dict = {}
        for action in action_list:
            cls_name = action.__class__.__name__
            if cls_name not in action_list_dict:
                action_list_dict[cls_name] = []
            action_list_dict[cls_name].append(action)

        assert sum([len(el) for el in action_list_dict.values()]) == len(action_list)
        return action_list_dict

    def _execute_cancel_orders_by_market(self, action_list: list[StrategyAtomicAction]):
        for action in action_list:
            assert isinstance(action, CancelOrdersByMarket)
            action.set_started()
            resp = self._clob_client.cancel_orders_by_market(
                condition_id=action.condition_id,
                asset_id=action.asset_id,
            )
            "{'not_canceled': {}, 'canceled': []}"
            action.set_final_status(is_success=True, is_failed=False)

    def _execute_cancel_orders_by_ids(self, action_list: list[StrategyAtomicAction]):
        for action in action_list:
            assert isinstance(action, CancelOrdersByIds)
            action.set_started()
            resp = self._clob_client.cancel_orders_by_ids(
                order_ids=action.order_ids,
            )
            """
            {'not_canceled': {},
            'canceled': ['0x972057f509c7b98cd3ea21e399b239cf937371892541f8bc5e2f88620613b69a']}
            {'not_canceled': {'0x972057f509c7b98cd3ea21e399b239cf937371892541f8bc5e2f88620613b69a': 'order already canceled'},
            'canceled': []}
            """
            # nelabai aisku kaip traktuoti cancel faile, bet tik del to, kad jau nebera co cancalinti. Arba jei dalis orderiu cancelino. KOlkas zymim, kad iskas OK
            action.set_final_status(is_success=True, is_failed=False)

    def _execute_place_direct_order(self, action_list: list[StrategyAtomicAction]):
        for action in action_list:
            assert isinstance(action, PlaceDirectOrder)
            action.set_started()
            resp = self._clob_client.place_order(
                token_id=action.token_id,
                price=action.price1000 / 1000,
                size=action.size1000 / 1000,
                side=action.trade_side,
                order_type=action.order_type,
            )
            """
            {'errorMsg': '',
             'orderID': '0x3eb90476a22ec4a835565fae8fee6132674d5d27e0ad8b233241e21119c45b36',
             'takingAmount': '',
             'makingAmount': '',
             'status': 'live',
             'success': True}
            """
            if resp['success']:
                action.set_created_order_ids(order_ids=[resp['orderID']])
                action.set_final_status(is_success=True, is_failed=False)
            else:
                action.set_final_status(is_success=False, is_failed=True)
