import unittest

from anre.utils.communication.messanger.messageRecord import MessageRecord
from anre.utils.communication.messanger.messenger import Messenger


class TestMessenger(unittest.TestCase):
    def test_default(self):
        messenger = Messenger.new(alarmLevel=100, popLevel=100)
        messenger.info('Some info message 1')
        messenger.info('Some info message 2')
        messenger.warning('Some warning message 1')
        messenger.error('Some error message 1')

        assert messenger.get_msgCount() == 4
        assert messenger.get_msgCount('INFO') == 2
        assert messenger.get_msgCount('WARNING') == 1
        assert messenger.get_msgCount('ERROR') == 1

    def test_extraFeatures_quiet(self):
        messenger = Messenger.new(collectMessages=True, quiet=True)
        messenger.info('Some info message 1')
        messenger.info('Some info message 2')
        messenger.warning('Some warning message 1')
        messenger.error('Some error message 1')

        assert messenger.get_msgCount() == 4
        assert messenger.get_msgCount('INFO') == 2
        assert messenger.get_msgCount('WARNING') == 1
        assert messenger.get_msgCount('ERROR') == 1

        assert len(messenger.get_messageLog()) == 4
        messenger.clear_messageLog()
        assert len(messenger.get_messageLog()) == 0

    def test_callback(self):
        class Counter:
            def __init__(self):
                self.value = 0

            def callback(self, msgRec: MessageRecord):
                if msgRec.levelStr in ['ERROR', 'WARNING']:
                    self.value += 1

        counter = Counter()
        messenger = Messenger.new(alarmLevel=100, popLevel=100)
        messenger.register_callback(callback=counter.callback)

        messenger.info('Some info message 1')
        messenger.info('Some info message 2')
        messenger.warning('Some warning message 1')

        assert counter.value == 1
