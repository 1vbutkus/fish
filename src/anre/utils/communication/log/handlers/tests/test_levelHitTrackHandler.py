import logging

from anre.utils import testutil
from anre.utils.communication.log.handlers.levelHitTrackHandler import LevelHitTrackHandler


class TestLevelHitTrackHandler(testutil.TestCase):
    def test_smoke(self) -> None:
        levelHitTrackHandler = LevelHitTrackHandler()
        assert not levelHitTrackHandler.fired

        logger = logging.getLogger()
        logger.info('info')
        assert not levelHitTrackHandler.fired

        logger.warning('warning')
        assert not levelHitTrackHandler.fired

        logger.error('error')
        assert levelHitTrackHandler.fired
