import logging

from anre.utils import testutil
from anre.utils.communication.log.utils import add_loggingLevel


class TestAddLoggingLevel(testutil.TestCase):
    def test_smoke(self) -> None:
        add_loggingLevel('TRACE', logging.DEBUG - 5)
        logging.getLogger(__name__).setLevel("TRACE")
        logging.getLogger(__name__).trace('that worked')  # type: ignore[attr-defined]
        logging.trace('so did this')  # type: ignore[attr-defined]
        logging.TRACE  # type: ignore[attr-defined]
