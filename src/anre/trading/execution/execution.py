import logging
import threading
import time
from threading import Event

from anre.connection.polymarket.master_client import MasterClient
from anre.trading.monitor.base import BaseMonitor
from anre.trading.monitor.monitors.boolMarket.flyBoolMarket import (
    FlyBoolMarket as FlyBoolMarketMonitor,
)
from anre.trading.strategy.brain.brains.balance_market_maker.balance_market_maker import (
    BalanceMarketMaker as BalanceMarketMakerStrategyBrain,
)
from anre.trading.strategy.strategyBox.strategyBox import StrategyBox
from anre.utils.time.timer.timerReal import TimerReal


class Execution:
    def __init__(self, monitor: BaseMonitor, strategy_box: StrategyBox, timer: TimerReal):
        assert isinstance(monitor, BaseMonitor)
        assert isinstance(strategy_box, StrategyBox)

        self._monitor: BaseMonitor = monitor
        self._strategy_box = strategy_box
        self._timer = timer
        self._lastIterationStartTime = 0
        self._finishEvent = Event()
        self._logger = logging.getLogger(__name__)
        self._runThread = None

    def run(self, join: bool = False):
        assert not self._finishEvent.is_set()
        assert self._runThread is None or not self._runThread.is_alive()

        if join:  # cia hack'as, kad profilinimas viektu - bet gal net galima ir palikti - tik pagalvoti reikia del side efektu
            self._run()
        else:
            self._runThread = threading.Thread(
                name=f'{self.__class__.__name__}._run', target=self._run, daemon=False
            )
            self._runThread.start()
            if join:
                self.join()

    def join(self):
        assert self._runThread is not None, 'Execution has not started, so it can not be joined.'
        assert self._runThread.is_alive(), 'Execution is not alive, so it can not be joined.'
        self._runThread.join()
        assert not self._runThread.is_alive(), (
            'Thread is suppose to be not alive, but somehow it is still alive'
        )
        self._runThread = None

    def is_finished(self) -> bool:
        return self._finishEvent.is_set()

    def is_alive(self) -> bool:
        return self._runThread is not None and self._runThread.is_alive()

    def _iteration(self):
        waitParam = 5

        # check time and wait as needed
        takesTime = self._timer.nowS() - self._lastIterationStartTime
        if takesTime > waitParam:
            if self._lastIterationStartTime > 0:
                self._logger.warning(
                    f'A single iteration of Execution is bigger then waitParam(`{waitParam}`): {takesTime=}'
                )
        waitInstanceSec = max(0.0, waitParam - takesTime)
        self._wait(waitSec=waitInstanceSec)

        if self._finishEvent.is_set():
            return None

        self._lastIterationStartTime = self._timer.nowS()

        # real start of iteration
        keepRunning = True

        # kai bus feedas, tai bus galima per feed bridge viska daryti
        self._monitor.iteration(gtt=-1)
        self._monitor.assert_up_to_date(gtt=1)

        # patikrinam ar vis dar aktualus marketas
        ###

        # strategy iteration. Make decisions and actions
        if keepRunning:
            self._strategy_box.iteration()

        if not keepRunning:
            self.finish(isInternalFinish=True)

    def _wait(self, waitSec: float):
        time.sleep(waitSec)

    def _run(self):
        while not self._finishEvent.is_set():
            self._iteration()

    def finish(self, isInternalFinish: bool = False):
        """Jei uzdarymas buvo suplanuotas isvidaus, tai internalFinish, visi kiti atvejai (t.y. manual aba uzluzimai) tai False"""
        assert isinstance(isInternalFinish, bool)
        self._isInternalFinish = isInternalFinish and not self._isManualStop
        self._finishEvent.set()

    def manualStop(self):
        """Mark that the end is not properly"""
        self._isManualStop = True
        self.finish(isInternalFinish=False)


def __dummy__():
    from dataclasses import replace

    client = MasterClient()
    # simplified_markets_info_list = client.clob_client.get_sampling_simplified_markets_info_list()
    # simplified_markets_info_list.sort(key=lambda x: x['rewards']['min_size'])
    # condition_id = simplified_markets_info_list[100]['condition_id']
    # condition_id = '0x9a68a7a12600327a3c388d7ad4d9a0bfcdf60870811427fcc01fab0c4410824c'

    "https://polymarket.com/event/which-countries-will-airdrop-aid-into-gaza/will-saudi-arabia-airdrop-aid-into-gaza?tid=1753937425640"

    # slug = 'will-hamaz-disarm-by-december-31'
    # client.gamma_client.get_market_info_list(slug=slug)[0]['conditionId']
    # condition_id = '0xa6bbe26fd234b7d93578e781f0a5d60fade908886ae723b5ed26e56295845673'  # will-saudi-arabia-airdrop-aid-into-gaza
    # condition_id = '0x301d94fc95cf16b9c29306e7ecae924d965359055c1d85965b97861a9dae33e7'  # trump-x-elon-talk-by-august-31
    condition_id = '0x11db077700a35d7415b6198c5e5a53adcf1db1819a09831f7eaf148f88243c40'  # will-hamaz-disarm-by-december-31

    # strategy_brain = FixedMarketMakerStrategyBrain.new(share_size=50, target_base_step_level=0)
    strategy_brain = BalanceMarketMakerStrategyBrain.new(
        share_size=25,
        target_base_step_level=1,
        target_skew_up_coefficient=0.5,
        target_skew_down_coefficient=0.4,
    )

    # strategy_brain._config = replace(strategy_brain._config, target_base_step_level = 1)

    self = monitor = FlyBoolMarketMonitor(condition_id=condition_id, default_gtt=3600)
    monitor.iteration(gtt=1)



    timer = monitor._timer
    strategy_box = StrategyBox(
        monitor=monitor,
        strategy_brain=strategy_brain,
    )

    cls = Execution
    self = execution = cls(monitor=monitor, strategy_box=strategy_box, timer=timer)

    execution.run(join=False)

    # execution.manualStop()
    execution.is_alive()

    ####
    strategy_box.strategy_brain._config = replace(
        strategy_box.strategy_brain._config,
        share_size=100,
        target_base_step_level=1,
        target_skew_up_coefficient=1,
        target_skew_down_coefficient=0.4,
    )

    self = strategy_box.strategy_brain
