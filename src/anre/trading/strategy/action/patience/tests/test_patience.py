import unittest

from anre.trading.strategy.action.actions.complex.place_bool_market_order import PlaceBoolMarketOrder
from anre.trading.strategy.action.patience.patience import Patience


class TestModelUserBrainReplay(unittest.TestCase):
    def test_happyPath_single(self):
        patience = Patience()

        action = PlaceBoolMarketOrder(
            main_asset_id='AAA',
            counter_asset_id='BBB',
            main_price1000=500,
            size1000=10000,
            bool_side='LONG',
            order_type='GTC',
        )

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert len(actionList) == 1
        assert actionList[0] is action

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert not actionList

    def test_change_mind_single(self):
        patience = Patience()

        action = PlaceBoolMarketOrder(
            main_asset_id='AAA',
            counter_asset_id='BBB',
            main_price1000=500,
            size1000=10000,
            bool_side='LONG',
            order_type='GTC',
        )

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        # do nothing
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert not actionList

    def test_happyPath_two_actions(self):
        patience = Patience()

        action1 = PlaceBoolMarketOrder(
            main_asset_id='AAA',
            counter_asset_id='BBB',
            main_price1000=500,
            size1000=10000,
            bool_side='LONG',
            order_type='GTC',
        )
        action2 = PlaceBoolMarketOrder(
            main_asset_id='AAA',
            counter_asset_id='BBB',
            main_price1000=600,
            size1000=10000,
            bool_side='LONG',
            order_type='GTC',
        )

        # single start, no action
        patience.start_iteration()
        patience.proc_actionWish(action=action1, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert not actionList

        # joins the second
        patience.start_iteration()
        patience.proc_actionWish(action=action1, iterationRequre=2)
        patience.proc_actionWish(action=action2, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        patience.proc_actionWish(action=action1, iterationRequre=2)
        patience.proc_actionWish(action=action2, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert len(actionList) == 1
        assert actionList[0] is action1

        patience.start_iteration()
        patience.proc_actionWish(action=action1, iterationRequre=2)
        patience.proc_actionWish(action=action2, iterationRequre=2)
        actionList = patience.finish_iteration()
        assert len(actionList) == 1
        assert actionList[0] is action2

    def test_pauseRelease(self):
        patience = Patience()

        action = PlaceBoolMarketOrder(
            main_asset_id='AAA',
            counter_asset_id='BBB',
            main_price1000=500,
            size1000=10000,
            bool_side='LONG',
            order_type='GTC',
        )

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=1)
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=1, pauseRelease=True)
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=1, pauseRelease=True)
        actionList = patience.finish_iteration()
        assert not actionList

        patience.start_iteration()
        patience.proc_actionWish(action=action, iterationRequre=1, pauseRelease=False)
        actionList = patience.finish_iteration()
        assert len(actionList) == 1
        assert actionList[0] is action
