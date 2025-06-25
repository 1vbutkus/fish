import unittest
import matplotlib.pyplot as plt

from bird.betfair.broker.brokerFootball.interactiveOu import InteractiveOu
from bird.execution.factory.creator import Creator as ExecutionCreator
from bird.betfair.broker.brokerFootball.shooterOu.lambdaOuTarget import LambdaOuTarget
from bird.execution.strategy.strategyBox.strategyBox import StrategyBox
from bird.execution.strategy.strategies.manual.manual import Manual as ManualStrategy


class TestStrategyBox(unittest.TestCase):

    def test_smoke(self):
        eventId = '32579989'
        source = 'recorded'

        strategy = ManualStrategy.new()
        execution = ExecutionCreator.new_replay(eventId=eventId, source=source, strategy=strategy, targetStarRelTimeMinutes=5)
        monitor = execution.monitor
        strategyBox = execution.strategyBox
        strategyBox._removeNotAlive_firedBetOrderList = False
        assert isinstance(strategyBox, StrategyBox)
        brokerFootball = strategyBox.brokerFootball

        execution.run(steps=60, join=True)
        interactiveOu = InteractiveOu(monitor=monitor, broker=brokerFootball)
        interactiveOu.openFigure()

        ouTarget = LambdaOuTarget(
            goalStrike10Int=15,
            sideOu='LONG',
            sizeOpena=5,
            priceLambda=2.8,
        )
        strategy.request_placeAction_fromOuTarget(ouTarget=ouTarget)
        ouTarget = LambdaOuTarget(
            goalStrike10Int=15,
            sideOu='LONG',
            sizeOpena=5,
            priceLambda=2.85,
        )
        strategy.request_placeAction_fromOuTarget(ouTarget=ouTarget)
        ouTarget = LambdaOuTarget(
            goalStrike10Int=15,
            sideOu='SHORT',
            sizeOpena=5,
            priceLambda=2.65,
        )
        strategy.request_placeAction_fromOuTarget(ouTarget=ouTarget)

        execution.run(steps=2, join=True)

        firedBetOrderList = brokerFootball.get_firedBetOrderList(removeNotAlive=False)
        assert len(firedBetOrderList) == 3
        firedBetOrderList = brokerFootball.get_firedBetOrderList(removeNotAlive=True)
        assert not firedBetOrderList

        execution.run(steps=10, join=True)

        firedBetOrderList = brokerFootball.get_firedBetOrderList()
        assert not firedBetOrderList

        # stop plot
        plt.close(interactiveOu.fig)
        interactiveOu.draw.stop(wait=True)
        assert not interactiveOu.draw.isAlive()
