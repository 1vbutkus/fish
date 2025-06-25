"""Sito objekto tikslas buti jungtimi tarp executiono ir tikros strategijos

I sita sluoksnis turi sueiti viskas, kad nepriklausotume nuo strategijos geros valios. Konkreciai:

* Jei situacija ne stabili, tai strategija jokiu budu negali plasinti orderiu. Gali tik cancelinti.
* RiskModul Jei norime taisykliu rinkinio, kuris virs strategijos dar kazka tikrins, tai cia puiki proga.

"""
from typing import Dict, List, Optional, Tuple, Any
import traceback
import numpy as np
import logging
from threading import Lock, Thread
from collections import defaultdict

from anre.utils.dotNest.dotNest import DotNest
from anre.trading.monitor.iMonitor import IMonitor
from anre.utils.time.timer.iTimer import ITimer
from anre.utils.time.timer.timerReal import TimerReal
from anre.trading.strategy.brain.brains.base.brainBase import StrategyBrain
from anre.trading.strategy.action.actions.base import StrategyAction
from anre.utils.functionsRunLog import FunctionsRunLog
from anre.trading.strategy.premissionLock.permissionLock import PermissionLock
from anre.utils.communication.messanger.messenger import Messenger


logger = logging.getLogger(__name__)


class StrategyBox:

    def __init__(self, strategy_brain: StrategyBrain, monitor: IMonitor, quiet: bool = False, raiseIfError: bool = True):

        assert isinstance(strategy_brain, StrategyBrain)
        assert isinstance(monitor, IMonitor)
        assert raiseIfError is None or isinstance(raiseIfError, bool)

        assert not strategy_brain.isSetObjects
        strategy_brain.set_objects(monitor=monitor)
        assert strategy_brain.isSetObjects

        self._strategy_brain: StrategyBrain = strategy_brain
        self._timer: ITimer = TimerReal()
        self._monitor: IMonitor = monitor
        self._aliveActionList: List[StrategyAction] = []
        self._updateLock = Lock()
        self._lastIterationStartTime = 0.
        self._lastIterationFinishTime = 0.
        self._raiseIfError: bool = raiseIfError
        self._messenger: Messenger = Messenger(timer=self._timer, quiet=quiet)
        self.functionsRunLog = FunctionsRunLog()
        self.permissionLock = PermissionLock(allowedValues={0, 20, 30, 40})
        self._latestBookChangeTimeSec_fromBetOrders: float = 0.

        self._job_execute_actionList: Optional[Thread] = None
        self._cacheDict: Dict[str, Tuple[float, Any]] = defaultdict(lambda: (0., None))

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
    def monitor(self) -> IMonitor:
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
                if takesTime > 1.:
                    msg = 'StrategyBox.iteration took too long ({0:.2f} s).\n{reportDf}'.format(takesTime, reportDf=str(self.functionsRunLog.get_reportDf()))
                    self._messenger.warning(msg)

        else:
            msg = 'Someone else was trying to run StrategyBox.iteration while already in iteration. Not good at all. This request will be skipped.'
            self._messenger.error(msg)

    def _iteration_internalCore(self):

        actionFreeze = self.get_isExecuteActionListAlive()

        # we need this before decisions.
        self.functionsRunLog.runFunction(self._update_aliveActionList_withElementAttributes, '_update_aliveActionList_withElementAttributes')

        #
        self.functionsRunLog.runFunction(self._update_ouInfo_inAlivePlaceActions, '_update_ouInfo_inAlivePlaceActions')

        # qa
        self.functionsRunLog.runFunction(self._qa_all, '_qa_all')

        # get action list
        actionList = []
        try:
            # actionList = self._strategy.updateStateAndGet_actionList(actionFreeze=actionFreeze)
            actionList = self.functionsRunLog.runFunction(self._strategy.updateStateAndGet_actionList, '_strategy.updateStateAndGet_actionList', actionFreeze=actionFreeze)

        except HuntingError:
            raise

        except BaseException as e:
            msg = f'An error happened in strategy request eventId={self.monitor.connector.eventId}. See below what happened and what was done next. Error: {e.__class__.__name__}({e}); traceback: {traceback.format_exc()}'
            self._messenger.error(msg=msg)

            if self._raiseIfError:
                raise

            from strategies.birch.iter_02.src.strategy.strategies.combo_02.combo02 import Combo02
            if isinstance(self._strategy, Combo02):
                self._strategy.update_config(activeBrain='standAloneSimpleAutoClose')
                msg = f'The strategy config was swithced to standAloneSimpleAutoClose'
                self._messenger.warning(msg=msg)

            else:
                from bird.execution.strategy.strategies.passive.passive import Passive as PassiveStrategy
                strategy = PassiveStrategy.new()
                strategy.set_objects(monitor=self._monitor, brokerFootball=self._brokerFootball, messenger=self._messenger)
                strategy.update_config(cancelAllOrders=True)
                self._strategy = strategy
                msg = f'The strategy was replased to passive not to make ony other actions.'
                self._messenger.warning(msg=msg)

        #
        self.functionsRunLog.runFunction(self._execute_actionList, '_execute_actionList', actionList=actionList)

        #
        self.functionsRunLog.runFunction(self._update_aliveActionList_withElementAttributes, '_update_aliveActionList_withElementAttributes')

        # log same state
        self.functionsRunLog.runFunction(self._log_state, '_log_state')

        #self._checkAndUpdateIfNeeded_plot()
        self.functionsRunLog.runFunction(self._checkAndUpdateIfNeeded_plot, '_checkAndUpdateIfNeeded_plot')

    def _log_state(self):
        key = '_log_state'
        nextCheckTimeSec, _ = self._cacheDict[key]
        if nextCheckTimeSec <= self._timer.nowS():
            lastSnapDict = self._monitor.data.get_lastSnapDict()
            takeRenameDict = {
                'gameTime.gameMinute': 'gameMinute',
                'portfolioOu.reading.profitNetFinalPortfolioMean': 'netProfitMean',
                'portfolioOu.reading.profitNetFinalPortfolioStd': 'netProfitStd',
                'portfolioOu.reading.openaGrossExpPortfolio0': 'openaGrossExpPortfolio0',
            }
            valueDict = DotNest.collect_valueDict(nest=lastSnapDict, takeRenameDict=takeRenameDict)
            msg = f'Monitor heartbeat: {valueDict}'
            self._messenger.info(msg)

            # self._messenger.info()
            self._cacheDict[key] = (self._timer.nowS() + 60, True)

    def _execute_actionList(self, actionList: [IAction]):
        wait = self._isSimulation
        self._execute_actionList_withWaitOption(actionList=actionList, wait=wait)

    def _execute_actionList_withWaitOption(self, actionList: [IAction], wait: bool = True):
        self._job_execute_actionList = self._create_thread(
            target=self._execute_actionList_core,
            actionList=actionList,
        )
        self._job_execute_actionList.start()

        if wait:
            self._job_execute_actionList.join()

    def get_isExecuteActionListAlive(self) -> bool:
        """Ar place funkcija visdar sukasi"""
        isAlive = self._job_execute_actionList is not None and self._job_execute_actionList.is_alive()
        return isAlive

    @classmethod
    def _create_thread(cls, target, **kwargs):
        thread = Thread(
            name=target.__name__,
            target=target,
            kwargs=kwargs,
        )
        return thread

    def _execute_actionList_core(self, actionList: [IAction]):

        permissionLockInt = self.permissionLock.get_currentValueInt()

        if permissionLockInt == 0:

            # NORMAL-TRADE
            gameMarketStatus = self._monitor.gameMarketStatus.getGtt_gameMarketStatus()
            if gameMarketStatus == 'OPEN':
                self._brokerFootball.set_disabled(disabled=False)
                isOkForTrade = self._monitor.stable.getGtt_isOk_for_algoTrading()
                if isOkForTrade:
                    ActionPalette.execute_actionList(actionList=actionList, brokerFootball=self._brokerFootball)

                else:
                    actionList_cancelOnly = ActionPalette.convertAndFilter_actionList_toNoPlace(actionList=actionList)
                    ActionPalette.execute_actionList(actionList=actionList_cancelOnly, brokerFootball=self._brokerFootball)

            else:
                self._brokerFootball.set_disabled(disabled=True)
                actionList_cancelOnly = ActionPalette.convertAndFilter_actionList_toNoPlace(actionList=actionList)
                ActionPalette.execute_actionList(actionList=actionList_cancelOnly, brokerFootball=self._brokerFootball)

                actionList_isPlace = ActionPalette.filter_actionList_isPlace(actionList=actionList)
                if actionList_isPlace:
                    msg = "Rinka nera OPEN, bet strategija sugalvojo delioti orderius."
                    self.brokerFootball.messenger.warning(msg)

        elif permissionLockInt == 10:
            # CANCEL-CLOSE-ONLY
            msg = f'Check for CANCEL-CLOSE-ONLY is not implemented.'
            logger.warning(msg)

        elif permissionLockInt == 20:
            # CANCEL-ONLY
            self._brokerFootball.set_disabled(disabled=True)
            actionList_cancelOnly = ActionPalette.convertAndFilter_actionList_toNoPlace(actionList=actionList)
            ActionPalette.execute_actionList(actionList=actionList_cancelOnly, brokerFootball=self._brokerFootball)

        elif permissionLockInt == 30:
            # SUSPEND
            # do nothing all the events will be repealed later
            self._brokerFootball.set_disabled(disabled=True)
            pass

        elif permissionLockInt == 40:
            # BACKOFF: do not execute any actions + actively cancel if any
            key = '_execute_actionList_core_BACKOFF'
            timeSec, _ = self._cacheDict[key]
            if timeSec < self._timer.nowS(-10):
                self._brokerFootball.set_disabled(disabled=True)
                # active cancel
                goalCount = self._monitor.goalCount.getGtt_goalCount()
                marketIds = self._monitor.connector.catalog.get_marketIds_active(goalCount=goalCount)
                openOrderDict = self._monitor.connector.feedAggregate.get_openOrderDict(marketIds=marketIds)
                marketIds_toCancel = [el['marketId'] for el in openOrderDict.values()]
                if marketIds_toCancel:
                    self._brokerFootball.cancel_allBetOrders_inMarkets(marketIds=marketIds_toCancel)
                self._cacheDict[key] = (self._timer.nowS(), None)

        else:
            msg = f'permissionLock value is not supported {permissionLockInt=}'
            raise NotImplementedError(msg)

        ### repeal all that was not triggered
        for action in actionList:
            if not action.isTriggered:
                action.repeal()

        ### move all actions to aliveActionList for further tracking
        _actionList_subset = [action for action in actionList if action.isTriggered]
        self._aliveActionList.extend(_actionList_subset)

    def _update_aliveActionList_withElementAttributes(self):

        if not self._aliveActionList:
            return None

        nowS = self._monitor.connector.timer.nowS()
        goalCount = self._monitor.goalCount.getGtt_goalCount()
        marketIds = self._monitor.connector.catalog.get_ouMarketIds_active(goalCount=goalCount)
        openOrderDict = self._monitor.connector.feedAggregate.get_openOrderDict(marketIds=marketIds)

        for action in self._aliveActionList:
            assert action.isTriggered, f'All actions in this place should be triggered: {self}'

            if action.hasPlaceElement:
                assert not action.isFinished, f'Finished action should not get to this place: {self}'
                assert isinstance(action, (PlaceOuTarget, ReplaceOuTargetIfPossible))
                betOrderList = action.get_betOrderList()
                if any([not betOrder.get_isPlaceFinish() and betOrder.get_isPlaceAlive() for betOrder in betOrderList]):
                    action.attr['strategyBox.isInFired'] = True
                    # mes norime gauti mapinga kuo greiciau, net kol jis dar yra isInFired, neskitu ateju galime gautiwarningus,kasciaper jobanas orderispasmus.
                    for betOrder in betOrderList:
                        for betOrderId in betOrder.get_relatedBetIdSet():
                            self._betIdMapToActionId[betOrderId] = action.actionId

                else:
                    ### mark that is no longer isInFired and pats its betOrderId
                    if action.attr.get('strategyBox.isInFired') is not False:   # this needs to bu run one tim only, that is way this if
                        action.attr['strategyBox.isInFired'] = False
                        for betOrder in betOrderList:
                            assert (betOrder.isConfirmed != betOrder.isRejected), f'Bad betOrder detected, isConfirmed={betOrder.isConfirmed}, isRejected={betOrder.isRejected}: {betOrder}'
                            # mark related betOrderId to mapping
                            for betOrderId in betOrder.get_relatedBetIdSet():
                                self._betIdMapToActionId[betOrderId] = action.actionId

                            ### collect latest update time
                            self._latestBookChangeTimeSec_fromBetOrders = max(betOrder.get_latestBookChangeTimeSec(), self._latestBookChangeTimeSec_fromBetOrders)

                    ### check that action is still active (or not)
                    # this action considered active if it has at least one betOrder that not isFinish
                    isFinishList = [betOrder.getUpdate_isFinish(isInBook=(betOrder.betId in openOrderDict)) for betOrder in betOrderList]
                    if all(isFinishList):
                        action.set_isFinished()

            elif isinstance(action, CancelPlaceOuTarget):
                if action.isFinished:
                    assert action.oldAction.isFinished, f'Cancel action should not be finished until its oldAction isfinished'

                else:
                    if action.oldAction.isFinished:
                        action.set_isFinished()

                        ### collect latest update time
                        betOrderList = action.oldAction.get_betOrderList()
                        for betOrder in betOrderList:
                            self._latestBookChangeTimeSec_fromBetOrders = max(betOrder.get_latestBookChangeTimeSec(), self._latestBookChangeTimeSec_fromBetOrders)

                    else:
                        assert action.triggerTimeSec, f'Action is triggered, but do not have triggerTimeSec, {action=}'
                        if action.triggerTimeSec < nowS - 6:
                            # We get get into this place by several ways (as far as I know):
                            # a) The cancel action was refected by betfair, the oerder still active and we want to cancel it
                            # b) The order is cancaled, wile it is still waiting to finish placing.
                            # c) The cancel itself has stuck - that sometimes happens. Betfar takes long time to respond.
                             if any([(betOrder.isExecutable and not betOrder.get_isCancelAlive()) for betOrder in action.oldAction.get_betOrderList()]):
                                # we want to cancel iff any order is executable and cancel is not active, otherewhise, there is no point of repeating.
                                msg = f'Repeated cancel action: {action}, openOrderIds={dict(openOrderDict)}'   # printing openOrderIds is also temp
                                logger.warning(msg)   # this is temp warning, later this can be turned into info
                                action.execute_single_retry(brokerFootball=self._brokerFootball)  # repeate action

            else:
                # TODO: dev not implimented. Cia reikia kiekvienam atejui atskirai pagalvoti kada actionas tampa isFinished, o else raisinti klaida
                action.set_isFinished()

        # drop all not active
        finishedActionList = [action for action in self._aliveActionList if action.isFinished]
        self._aliveActionList = [action for action in self._aliveActionList if not action.isFinished]
        self._qa_checkFinishedActions_repeatedAction(finishedActionList=finishedActionList)

    def _qa_all(self):

        ### only active action in _aliveActionList
        if any([action.isFinished for action in self._aliveActionList]):
            msg = 'There are actions that are finished, but still in _aliveActionList'
            self.messenger.warning(msg)

        ###
        self._qa_openOrderAndActiveAction()

        ### check if
        self._qa_check_orderStreamUpdates()

    def _qa_check_orderStreamUpdates(self):

        key = '_qa_check_orderStreamUpdates'
        nextCheckTimeSec, badStrikeInt = self._cacheDict[key]
        if nextCheckTimeSec <= self._timer.nowS():

            badStrikeInt = 0 if badStrikeInt is None else badStrikeInt
            lastOrderBookChangeTimeSec_expected = self._latestBookChangeTimeSec_fromBetOrders
            lastOrderBookChangeTimeSec_actual = self._monitor.connector.feedAggregate.get_lastOrderChangePt() / 1000
            if lastOrderBookChangeTimeSec_actual < lastOrderBookChangeTimeSec_expected - 5:
                badStrikeInt += 1
                logger.warning(f'The system shows that orderListiner was not updated, just warning - doing nothing {badStrikeInt=}.')

                if badStrikeInt == 3:
                    logger.warning(f'The system shows that orderListiner was not updated, {badStrikeInt=}. We reached the moment where we want to backoff until it is OK.')
                    self.permissionLock.put_lock_backoff(owner=f'strategyBox.{key}')

            else:
                if badStrikeInt > 0:
                    badStrikeInt = 0
                    self.permissionLock.release_lock(owner=f'strategyBox.{key}', raiseIfMissing=False)

        self._cacheDict[key] = (self._timer.nowS() + 5, badStrikeInt)

    def _qa_checkFinishedActions_repeatedAction(self, finishedActionList: List[IAction]):

        for action in finishedActionList:
            assert isinstance(action, IAction)
            assert action.isFinished
            if action.hasPlaceElement:
                assert isinstance(action, (PlaceOuTarget, ReplaceOuTargetIfPossible))
                key = (action.ouTarget.goalStrike10Int, action.ouTarget.sideOu)
                if key in self._qa_placeActionRepeatDict:
                    if action.isCanceled:
                        recDict = self._qa_placeActionRepeatDict[key]
                        nowS = self._monitor.connector.timer.nowS()
                        if action.isCloseEnough(other=recDict['lastAction']) and nowS - recDict['lastTimeSec'] < 10:   # note sita konstanta turi sasaju su strategijoje naudojama _strikeTimeoutSec:
                            recDict['strikeCount'] += 1
                            recDict['lastTimeSec'] = nowS
                            recDict['lastAction'] = action

                            if recDict['strikeCount'] > 4:
                                msg = f'Repeated actions of failed placeAction identified, please be more patience: {recDict=}'
                                self._messenger.warning(msg)
                                # temp rase to find same test cases
                                # raise AssertionError(msg)

                        else:
                            # strike is over, deleting
                            del self._qa_placeActionRepeatDict[key]

                    else:
                        # strike is over, deleting
                        del self._qa_placeActionRepeatDict[key]

                else:
                    if action.isCanceled:
                        self._qa_placeActionRepeatDict[key] = {
                            'strikeCount': 1,
                            'lastTimeSec': self._monitor.connector.timer.nowS(),
                            'lastAction': action,
                        }
                    else:
                        pass   # do nothing

    def _qa_openOrderAndActiveAction(self):
        """Tikrinam rysi tarp openOrder ir jo tevo

        # ar yra betOrder be tevu
        # ar matom betOrder, knygoje, nors jis pazymetas kaip nebeaktyvus
        # ar matom betOrdery knygoj,e nors jo actionas jau nebeaktyvus - arba istrintas

        # jei randamas netinkamas , tai ispejimas - bet tik karta
        """

        monitor = self._monitor
        goalCount = monitor.goalCount.getGtt_goalCount()
        ouMarketIds = monitor.connector.catalog.get_ouMarketIds_active(goalCount=goalCount)
        openOrderDict = monitor.connector.feedAggregate.get_openOrderDict(marketIds=ouMarketIds)
        # filter with same delay, so that it would not cased race condition
        _nowDt = monitor.connector.timer.nowDt(-1.5)
        openOrderDict = {key: value for key, value in openOrderDict.items() if value['placedTime'] < _nowDt}

        aliveActionDict = {aliveAction.actionId: aliveAction for aliveAction in self._aliveActionList if aliveAction.hasPlaceElement}

        for betId, openOrder in openOrderDict.items():
            if betId not in self._qa_warnedBetId:
                if betId in self._betIdMapToActionId:
                    actionId = self._betIdMapToActionId[betId]
                    if actionId in aliveActionDict:
                        action = aliveActionDict[actionId]
                        if action.isFinished:
                            msg = f'betId(`{betId}`) has link to action(actionId={actionId}), but action is finished: {openOrder=}'
                            self._messenger.warning(msg=msg)
                            self._qa_warnedBetId.add(betId)
                    else:
                        msg = f'betId(`{betId}`) has link to action(actionId={actionId}), but action is no longer in _aliveActionList: {openOrder=}'
                        self._messenger.warning(msg=msg)
                        self._qa_warnedBetId.add(betId)

                else:
                    # TODO: neaisku ar cia reikia pranesineti ar ka veikti
                    # msg = f'betId(`{betId}`) not in betOrderIdMapToAction: {openOrder=}'
                    # self._messenger.warning(msg=msg)
                    self._qa_warnedBetId.add(betId)

    def _update_ouInfo_inAlivePlaceActions(self):

        if not self._aliveActionList:
            return None

        goalCount = self._monitor.goalCount.getGtt_goalCount()
        marketIds = self._monitor.connector.catalog.get_ouMarketIds_active(goalCount=goalCount)
        openOrderDict = self._monitor.connector.feedAggregate.get_openOrderDict(marketIds=marketIds)

        for action in self._aliveActionList:
            if action.hasPlaceElement:
                assert isinstance(action, (PlaceOuTarget, ReplaceOuTargetIfPossible))
                betOrderList = action.get_betOrderList()
                if all([betOrder.get_isPlaceFinish() for betOrder in betOrderList]):

                    ### get remainingMaxOpena and muOpenaProdSum
                    remainingMaxOpena = 0.
                    muOpenaProdSum = 0.
                    for betOrder in betOrderList:
                        if betOrder.isConfirmed:
                            betId = betOrder.betId
                            assert betId

                            # Note: openOrderDict can be late. Thus, if we dont see it now, it does not mean it is not forever
                            openOrder = openOrderDict.get(betId)
                            if openOrder:
                                assert 'ouInfo' in betOrder.attr
                                ouBetOrderInfo = betOrder.attr['ouInfo']
                                if ouBetOrderInfo['goalCount'] != goalCount:
                                    msg = f'Goal count is not matching. We do not expect to find order in openOrderDict if this happens. Cancel order and hope for the best. {betOrder=}, {ouBetOrderInfo=}'
                                    self._messenger.warning(msg)
                                    betOrderCreds = [betOrder.get_betOrderCred()]
                                    self._brokerFootball.cancel_betOrders(betOrderCreds=betOrderCreds)

                                goalStrike10Int = ouBetOrderInfo['goalStrike10Int']
                                marketIdx = self._monitor.connector.catalog.get_idx_ofGoalStrike10IntArr(goalStrike10Int=goalStrike10Int)
                                probEq = self._monitor.data.snapshot.portfolioOu.table.probEq[marketIdx]
                                sizeRemaining = openOrder['sizeRemaining']
                                price = openOrder['price']
                                _remainingMaxOpena = Definition.get_openaMax_fromPrice(price=price, stake=sizeRemaining, probEq=probEq)
                                _mu = ouBetOrderInfo['mu']
                                remainingMaxOpena += _remainingMaxOpena
                                muOpenaProdSum += _mu * _remainingMaxOpena

                    mu = muOpenaProdSum / remainingMaxOpena if remainingMaxOpena > 0 else np.nan
                    action.attr['strategyBox.ouInfo.mu'] = mu
                    action.attr['strategyBox.ouInfo.remainingMaxOpena'] = remainingMaxOpena

    #########################################   plot   ######################################

    def _checkAndUpdateIfNeeded_plot(self):
        if self._monitor.plot.muSnapshot.currentDynamicGraph is not None and self._monitor.plot.muSnapshot.currentDynamicGraph.fig is not None:
            self._plotData = self._plot_get_data()
            if self._plotObjDict:
                self._plot_plotUpdate()
            else:
                ax, = self._monitor.plot.muSnapshot.currentDynamicGraph.fig.get_axes()
                self._plotObjDict = self._plot_plotInit(ax=ax, plotData=self._plotData)
        else:
            self._plotObjDict = {}

    def _plot_get_data(self) -> Dict:

        expTimePropTogo = self._monitor.data.snapshot.gameTime.expTimePropTogo
        goalCount = self._monitor.goalCount.getGtt_goalCount()
        marketIds_overUnder = self._monitor.connector.catalog.marketIds_overUnder
        firedOrderPlotDataDict_last = self._firedOrderPlotDataDict_last

        firedOrderPlotDataDict_active = {}
        firedBetOrderList = self._brokerFootball.get_firedBetOrderList(removeNotAlive=self._removeNotAlive_firedBetOrderList)
        for betOrder in firedBetOrderList:
            if betOrder.marketId in marketIds_overUnder:
                _id = betOrder.customerOrderRef
                assert _id
                # check if already calculated
                if betOrder.betId in firedOrderPlotDataDict_last:
                    firedOrderPlotDataDict_active[_id] = firedOrderPlotDataDict_last[_id]
                else:
                    assert 'ouInfo' in betOrder.attr, f'We expect all ouBetOrders will have ouInfo in attr. Please check how those orders where created.'
                    ouInfo = betOrder.attr['ouInfo']
                    firedOrderPlotDataDict_active[_id] = (ouInfo['mu'], ouInfo['sideOu'], ouInfo['goalStrike10Int'] / 10)

        self._firedOrderPlotDataDict_last = firedOrderPlotDataDict_active

        plotData = {
            'LONG': {
                'lambda': [],
                'goalStrike': [],
            },
            'SHORT': {
                'lambda': [],
                'goalStrike': [],
            }
        }
        for _, (mu, sideRunner, goalStrike) in firedOrderPlotDataDict_active.items():
            plotData[sideRunner]['lambda'].append(mu / expTimePropTogo)
            plotData[sideRunner]['goalStrike'].append(goalStrike)

        return plotData

    @staticmethod
    def _plot_plotInit(ax, plotData: dict) -> Dict:

        line_long, = ax.plot(plotData['LONG']['lambda'], plotData['LONG']['goalStrike'], "1", color='b', markersize=15, alpha=0.6)
        line_short, = ax.plot(plotData['SHORT']['lambda'], plotData['SHORT']['goalStrike'], "1", color='r', markersize=15, alpha=0.6)

        return {
            'lines': {
                'LONG': line_long,
                'SHORT': line_short,
            }
        }

    def _plot_plotUpdate(self):
        if self._plotObjDict:
            # print(" --- tik ---")
            for key, line in self._plotObjDict['lines'].items():
                data = self._plotData[key]
                line.set_data(data['lambda'], data['goalStrike'])
