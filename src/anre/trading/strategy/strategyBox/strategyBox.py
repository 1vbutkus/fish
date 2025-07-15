"""Sito objekto tikslas buti jungtimi tarp executiono ir tikros strategijos

I sita sluoksnis turi sueiti viskas, kad nepriklausotume nuo strategijos geros valios. Konkreciai:

* Jei situacija ne stabili, tai strategija jokiu budu negali plasinti orderiu. Gali tik cancelinti.
* RiskModul Jei norime taisykliu rinkinio, kuris virs strategijos dar kazka tikrins, tai cia puiki proga.

"""

import logging
import traceback
from collections import defaultdict
from threading import Lock, Thread
from typing import Any, Dict, List, Optional, Tuple

from anre.trading.monitor.base import BaseMonitor
from anre.trading.strategy.action.actions.base import StrategyAction
from anre.trading.strategy.action.executor.executor import StrategyActionExecutor
from anre.trading.strategy.brain.brains.base.brainBase import StrategyBrain
from anre.trading.strategy.premissionLock.permissionLock import PermissionLock
from anre.utils.communication.messanger.messenger import Messenger
from anre.utils.functionsRunLog import FunctionsRunLog
from anre.utils.time.timer.iTimer import ITimer
from anre.utils.time.timer.timerReal import TimerReal
from anre.trading.strategy.patience.patience import Patience

logger = logging.getLogger(__name__)


class StrategyBox:
    def __init__(
        self,
        strategy_brain: StrategyBrain,
        monitor: BaseMonitor,
        quiet: bool = False,
        raise_if_error: bool = True,
    ):
        assert isinstance(strategy_brain, StrategyBrain)
        assert isinstance(monitor, BaseMonitor)
        assert raise_if_error is None or isinstance(raise_if_error, bool)

        assert not strategy_brain.is_setting_object_finished
        strategy_brain.set_objects(monitor=monitor)
        assert strategy_brain.is_setting_object_finished

        self._strategy_brain: StrategyBrain = strategy_brain
        self._timer: ITimer = TimerReal()
        self._monitor: BaseMonitor = monitor
        self._aliveActionList: List[StrategyAction] = []
        self._updateLock = Lock()
        self._lastIterationStartTime = 0.0
        self._lastIterationFinishTime = 0.0
        self._raiseIfError: bool = raise_if_error
        self._messenger: Messenger = Messenger.new(timer=self._timer, quiet=quiet)
        self.functionsRunLog = FunctionsRunLog()
        self.permissionLock = PermissionLock(allowedValues={0, 20, 30, 40})
        self._latestBookChangeTimeSec_fromBetOrders: float = 0.0

        self._job_execute_actionList: Optional[Thread] = None
        self._cacheDict: Dict[str, Tuple[float, Any]] = defaultdict(lambda: (0.0, None))

    def __del__(self):
        # qa:
        try:
            if self._aliveActionList:
                msg = f'StrategyBox.__del__: There are actions in self._aliveActionLis: {len(self._aliveActionList)}'
                logger.warning(msg)
        except BaseException:
            pass

    @property
    def strategy_brain(self) -> StrategyBrain:
        return self._strategy_brain

    @property
    def monitor(self) -> BaseMonitor:
        return self._monitor

    def iteration(self):
        if not self._updateLock.locked():
            with self._updateLock:
                self._lastIterationStartTime = self._timer.nowS()
                if self._lastIterationFinishTime < self._lastIterationStartTime - 30:
                    if self._lastIterationFinishTime > 0:
                        _gapTimeSec = self._lastIterationStartTime - self._lastIterationFinishTime
                        msg = f'StrategyBox._iteration was not running for {round(_gapTimeSec, 3)} seconds. Where stuck happened?'
                        self._messenger.warning(msg)
                    else:
                        # it is OK, just the first iteration
                        pass

                self._iteration_internalCore()
                self._lastIterationFinishTime = self._timer.nowS()

                takesTime = self._lastIterationFinishTime - self._lastIterationStartTime
                if takesTime > 1.0:
                    msg = 'StrategyBox.iteration took too long ({0:.2f} s).\n{reportDf}'.format(
                        takesTime, reportDf=str(self.functionsRunLog.get_reportDf())
                    )
                    self._messenger.warning(msg)

        else:
            msg = 'Someone else was trying to run StrategyBox.iteration while already in iteration. Not good at all. This request will be skipped.'
            self._messenger.error(msg)

    def _iteration_internalCore(self):
        action_freeze = self.get_is_still_executing()

        # qa
        self.functionsRunLog.runFunction(self._qa_all, '_qa_all')

        # get action list
        action_list = []
        try:
            action_list = self.functionsRunLog.runFunction(
                self._strategy_brain.update_state_and_get_action_list,
                '_strategy_brain.update_state_and_get_action_list',
                action_freeze=action_freeze,
            )

        except BaseException as e:
            msg = f'An error happened in strategy request. See below what happened and what was done next. Error: {e.__class__.__name__}({e}); traceback: {traceback.format_exc()}'
            self._messenger.error(msg=msg)

            if self._raiseIfError:
                raise

            # TODO: jei ivyko klaida, tai reikia on the fly pakeisti braina i patikim1 ir patikrinta viarianta. Kolkas tokio neturime
            raise
            # from strategies.birch.iter_02.src.strategy.strategies.combo_02.combo02 import Combo02
            # if isinstance(self._strategy, Combo02):
            #     self._strategy.update_config(activeBrain='standAloneSimpleAutoClose')
            #     msg = f'The strategy config was swithced to standAloneSimpleAutoClose'
            #     self._messenger.warning(msg=msg)
            #
            # else:
            #     from bird.execution.strategy.strategies.passive.passive import Passive as PassiveStrategy
            #     strategy = PassiveStrategy.new()
            #     strategy.set_objects(monitor=self._monitor, brokerFootball=self._brokerFootball, messenger=self._messenger)
            #     strategy.update_config(cancelAllOrders=True)
            #     self._strategy = strategy
            #     msg = f'The strategy was replased to passive not to make ony other actions.'
            #     self._messenger.warning(msg=msg)

        #
        self.functionsRunLog.runFunction(
            self._execute_action_list, '_execute_actionList', action_list=action_list
        )

        # log same state
        self.functionsRunLog.runFunction(self._log_state, '_log_state')

    def _log_state(self):
        pass

    def _execute_action_list(self, action_list: [StrategyAction]):
        self._job_execute_actionList = self._create_thread(
            target=self._execute_actionList_core,
            action_list=action_list,
        )
        self._job_execute_actionList.start()

    def get_is_still_executing(self) -> bool:
        """Ar place funkcija visdar sukasi"""
        isAlive = (
            self._job_execute_actionList is not None and self._job_execute_actionList.is_alive()
        )
        return isAlive

    @classmethod
    def _create_thread(cls, target, **kwargs):
        thread = Thread(
            name=target.__name__,
            target=target,
            kwargs=kwargs,
        )
        return thread

    def _execute_actionList_core(self, action_list: [StrategyAction]):
        print(f"Call strategyBox._execute_actionList_core: {action_list}")

        # permissionLockInt = self.permissionLock.get_currentValueInt()
        #
        # if permissionLockInt == 0:
        #
        #     # NORMAL-TRADE
        #     gameMarketStatus = self._monitor.gameMarketStatus.getGtt_gameMarketStatus()
        #     if gameMarketStatus == 'OPEN':
        #         self._brokerFootball.set_disabled(disabled=False)
        #         isOkForTrade = self._monitor.stable.getGtt_isOk_for_algoTrading()
        #         if isOkForTrade:
        #             ActionPalette.execute_actionList(actionList=action_list, brokerFootball=self._brokerFootball)
        #
        #         else:
        #             actionList_cancelOnly = ActionPalette.convertAndFilter_actionList_toNoPlace(actionList=action_list)
        #             ActionPalette.execute_actionList(actionList=actionList_cancelOnly, brokerFootball=self._brokerFootball)
        #
        #     else:
        #         self._brokerFootball.set_disabled(disabled=True)
        #         actionList_cancelOnly = ActionPalette.convertAndFilter_actionList_toNoPlace(actionList=action_list)
        #         ActionPalette.execute_actionList(actionList=actionList_cancelOnly, brokerFootball=self._brokerFootball)
        #
        #         actionList_isPlace = ActionPalette.filter_actionList_isPlace(actionList=action_list)
        #         if actionList_isPlace:
        #             msg = "Rinka nera OPEN, bet strategija sugalvojo delioti orderius."
        #             self.brokerFootball.messenger.warning(msg)
        #
        # elif permissionLockInt == 10:
        #     # CANCEL-CLOSE-ONLY
        #     msg = f'Check for CANCEL-CLOSE-ONLY is not implemented.'
        #     logger.warning(msg)
        #
        # elif permissionLockInt == 20:
        #     # CANCEL-ONLY
        #     self._brokerFootball.set_disabled(disabled=True)
        #     actionList_cancelOnly = ActionPalette.convertAndFilter_actionList_toNoPlace(actionList=action_list)
        #     ActionPalette.execute_actionList(actionList=actionList_cancelOnly, brokerFootball=self._brokerFootball)
        #
        # elif permissionLockInt == 30:
        #     # SUSPEND
        #     # do nothing all the events will be repealed later
        #     self._brokerFootball.set_disabled(disabled=True)
        #     pass
        #
        # elif permissionLockInt == 40:
        #     # BACKOFF: do not execute any actions + actively cancel if any
        #     key = '_execute_actionList_core_BACKOFF'
        #     timeSec, _ = self._cacheDict[key]
        #     if timeSec < self._timer.nowS(-10):
        #         self._brokerFootball.set_disabled(disabled=True)
        #         # active cancel
        #         goalCount = self._monitor.goalCount.getGtt_goalCount()
        #         marketIds = self._monitor.connector.catalog.get_marketIds_active(goalCount=goalCount)
        #         openOrderDict = self._monitor.connector.feedAggregate.get_openOrderDict(marketIds=marketIds)
        #         marketIds_toCancel = [el['marketId'] for el in openOrderDict.values()]
        #         if marketIds_toCancel:
        #             self._brokerFootball.cancel_allBetOrders_inMarkets(marketIds=marketIds_toCancel)
        #         self._cacheDict[key] = (self._timer.nowS(), None)
        #
        # else:
        #     msg = f'permissionLock value is not supported {permissionLockInt=}'
        #     raise NotImplementedError(msg)
        #
        # ### repeal all that was not triggered
        # for action in action_list:
        #     if not action.isTriggered:
        #         action.repeal()
        #
        # ### move all actions to aliveActionList for further tracking
        # _actionList_subset = [action for action in action_list if action.isTriggered]
        # self._aliveActionList.extend(_actionList_subset)

    def _qa_all(self):
        ### only active action in _aliveActionList
        if any([action.isFinished for action in self._aliveActionList]):
            msg = 'There are actions that are finished, but still in _aliveActionList'
            self._messenger.warning(msg)

        ###
        self._qa_openOrderAndActiveAction()

    def _qa_openOrderAndActiveAction(self):
        """Tikrinam rysi tarp openOrder ir jo tevo

        # ar yra betOrder be tevu
        # ar matom betOrder, knygoje, nors jis pazymetas kaip nebeaktyvus
        # ar matom betOrdery knygoj,e nors jo actionas jau nebeaktyvus - arba istrintas

        # jei randamas netinkamas , tai ispejimas - bet tik karta
        """
        pass

        # monitor = self._monitor
        # goalCount = monitor.goalCount.getGtt_goalCount()
        # ouMarketIds = monitor.connector.catalog.get_ouMarketIds_active(goalCount=goalCount)
        # openOrderDict = monitor.connector.feedAggregate.get_openOrderDict(marketIds=ouMarketIds)
        # # filter with same delay, so that it would not cased race condition
        # _nowDt = monitor.connector.timer.nowDt(-1.5)
        # openOrderDict = {key: value for key, value in openOrderDict.items() if value['placedTime'] < _nowDt}
        #
        # aliveActionDict = {aliveAction.actionId: aliveAction for aliveAction in self._aliveActionList if aliveAction.hasPlaceElement}
        #
        # for betId, openOrder in openOrderDict.items():
        #     if betId not in self._qa_warnedBetId:
        #         if betId in self._betIdMapToActionId:
        #             actionId = self._betIdMapToActionId[betId]
        #             if actionId in aliveActionDict:
        #                 action = aliveActionDict[actionId]
        #                 if action.isFinished:
        #                     msg = f'betId(`{betId}`) has link to action(actionId={actionId}), but action is finished: {openOrder=}'
        #                     self._messenger.warning(msg=msg)
        #                     self._qa_warnedBetId.add(betId)
        #             else:
        #                 msg = f'betId(`{betId}`) has link to action(actionId={actionId}), but action is no longer in _aliveActionList: {openOrder=}'
        #                 self._messenger.warning(msg=msg)
        #                 self._qa_warnedBetId.add(betId)
        #
        #         else:
        #             # # neaisku ar cia reikia pranesineti ar ka veikti
        #             # msg = f'betId(`{betId}`) not in betOrderIdMapToAction: {openOrder=}'
        #             # self._messenger.warning(msg=msg)
        #             self._qa_warnedBetId.add(betId)


def __dummy__():
    from anre.trading.monitor.monitors.boolMarket.flyBoolMarket import (
        FlyBoolMarket as FlyBoolMarketMonitor,
    )
    from anre.trading.strategy.action.factory import Factory as ActionFactory
    from anre.trading.strategy.brain.brains.dummy.dummy import Dummy as DummyStrategyBrain

    # client = MasterClient()
    # simplified_markets_info_list = client.clob_client.get_sampling_simplified_markets_info_list()
    # simplified_markets_info_list.sort(key=lambda x: x['rewards']['min_size'])
    # condition_id = simplified_markets_info_list[100]['condition_id']
    condition_id = '0x9a68a7a12600327a3c388d7ad4d9a0bfcdf60870811427fcc01fab0c4410824c'

    patience = Patience()
    executor = StrategyActionExecutor()

    strategy_brain = DummyStrategyBrain.new()
    monitor = FlyBoolMarketMonitor(condition_id=condition_id, default_gtt=3600)


    monitor.iteration()

    # monitor.get_top_level_price_dict()
    bool_market_cred = monitor.market_info_parser.bool_market_cred
    public_market_order_book, house_order_book, net_market_order_book = (
        monitor.get_market_order_books()
    )
    bid1000, ask1000 = net_market_order_book.get_main_asset_best_price1000s()

    tick1000 = monitor.get_tick1000()
    step1000 = tick1000
    target_level: int = 1
    keep_offset_shallow_level = 0
    keep_offset_deep_level = 0
    size = 10

    target_long_price1000 = bid1000 - step1000 * target_level
    target_long_price1000 = min(target_long_price1000, ask1000 - tick1000)
    target_short_price1000 = ask1000 + step1000 * target_level
    target_short_price1000 = max(target_short_price1000, bid1000 + tick1000)

    keep_long_price1000_range = [target_long_price1000 - keep_offset_deep_level * step1000, target_long_price1000 + keep_offset_shallow_level * step1000]
    keep_short_price1000_range = [target_short_price1000 - keep_offset_deep_level * step1000, target_short_price1000 + keep_offset_shallow_level * step1000]




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
            if keep_long_price1000_range[0] <= main_price1000 <= keep_long_price1000_range[1] and order_dict['remaining_size1000'] == int(round(1000*size)):
                is_long_order_OK = True
            else:
                action = ActionFactory.new_cancel_orders_by_ids(order_ids=[order_dict['id']])
                cancel_action_list.append(action)
        elif order_dict['bool_side'] == 'SHORT':
            if keep_short_price1000_range[0] <= main_price1000 <= keep_short_price1000_range[1] and order_dict['remaining_size1000'] == int(round(1000*size)):
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
            size=size,
            bool_side='LONG',
        )
        place_action_list.append(action)
    if not is_short_order_OK:
        action = ActionFactory.new_place_bool_market_order(
            main_asset_id=bool_market_cred.main_asset_id,
            counter_asset_id=bool_market_cred.counter_asset_id,
            main_price1000=target_short_price1000,
            size=10,
            bool_side='SHORT',
        )
        place_action_list.append(action)



    ### patience
    patience.start_iteration()
    for action in cancel_action_list:
        patience.proc_actionWish(action=action, iterationRequre=0)
    for action in place_action_list:
        patience.proc_actionWish(action=action, iterationRequre=1)
    action_list = patience.finish_iteration()

    ### execute
    executor.execute_actions(action_list=action_list)



