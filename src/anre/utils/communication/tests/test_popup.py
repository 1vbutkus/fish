from anre.utils import testutil
from anre.utils.communication.popup import popupMsg


class TestPopup(testutil.TestCase):
    def test_smoke(self) -> None:
        popupMsg('Test')
