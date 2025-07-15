from threading import Lock
from typing import List, Tuple

from anre.trading.strategy.action.actions.base import StrategyAction
from anre.trading.strategy.action.actions.cancel_orders_by_ids import CancelOrdersByIds
from anre.trading.strategy.action.actions.place_bool_market_order import PlaceBoolMarketOrder
from anre.trading.strategy.action.actions.place_direct_order import PlaceDirectOrder


class Patience:
    """Objektas, kuris saugo noretus norus ir trakina kada jie sulauke savo sloves ir kada jau laikas nebenoreti"""

    def __init__(self):
        self._passActionList: List[StrategyAction] = []
        self._waitDict = {}
        self._iterationNr = 0
        self._iterationIsStarted: bool = False
        self._lock: Lock = Lock()

    def clear(self):
        with self._lock:
            self._iterationIsStarted = False
            self._passActionList: List[StrategyAction] = []
            self._waitDict = {}

    def start_iteration(self):
        assert not self._iterationIsStarted
        self._iterationNr += 1
        self._iterationIsStarted = True

    def finish_iteration(self) -> List[StrategyAction]:
        assert self._iterationIsStarted
        with self._lock:
            # collect all actions that we want and clean up
            passActionList = self._passActionList.copy()
            self._passActionList = []

            # drop all of those that were not touched in this iteration
            self._waitDict = {
                key: values
                for key, values in self._waitDict.items()
                if values[0] == self._iterationNr
            }

            self._iterationIsStarted = False

        return passActionList

    def proc_actionWish(
        self,
        action: StrategyAction,
        iterationRequre: int = 0,
        pauseRelease: bool = False,
        procLabel: str = 'default',
    ):
        assert isinstance(action, StrategyAction)
        assert isinstance(iterationRequre, int)
        assert isinstance(pauseRelease, bool)
        assert isinstance(procLabel, str)
        assert self._iterationIsStarted
        assert not self._lock.locked()

        key = self._get_key(action=action, procLabel=procLabel)
        self._proc_action(
            key=key, action=action, iterationRequre=iterationRequre, pauseRelease=pauseRelease
        )

    def _get_key(self, action: StrategyAction, procLabel: str = 'default') -> Tuple:
        if isinstance(action, PlaceBoolMarketOrder):
            key = (
                action.__class__.__name__,
                procLabel,
                action.main_token_id,
                action.counter_token_id,
                action.main_price1000,
                action.bool_side,
            )

        elif isinstance(action, PlaceDirectOrder):
            key = (
                action.__class__.__name__,
                procLabel,
                action.token_id,
                action.price,
                action.size,
                action.side,
                action.order_type,
            )

        elif isinstance(action, CancelOrdersByIds):
            key = (action.__class__.__name__, procLabel, tuple(sorted(action.order_ids)))

        else:
            key = (action.__class__.__name__, procLabel, str(action))

        return key

    def _proc_action(
        self, key: Tuple, action: StrategyAction, iterationRequre: int, pauseRelease: bool
    ):
        if key in self._waitDict:
            oldIterationNr, oldAction, oldIterationCount = self._waitDict.pop(key)
            if (iterationRequre == 0) and (not pauseRelease):
                # pass action without comparing
                action.set_approved()
                self._passActionList.append(action)
            else:
                iterationCount = oldIterationCount + 1
                if (iterationRequre <= iterationCount) and (not pauseRelease):
                    # it waited enouth
                    action.set_approved()
                    self._passActionList.append(action)
                else:
                    # keep waiting
                    self._put_intoWaiting(key=key, action=action, iterationCount=iterationCount)

        elif (iterationRequre == 0) and (not pauseRelease):
            action.set_approved()
            self._passActionList.append(action)

        else:
            self._put_intoWaiting(key=key, action=action, iterationCount=0)

    def _put_intoWaiting(self, key, action, iterationCount):
        self._waitDict[key] = (self._iterationNr, action, iterationCount)
