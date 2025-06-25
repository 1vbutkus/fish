import datetime
import unittest

from dataclass_type_validator import TypeValidationError

from anre.utils.communication.messanger.messageRecord import MessageRecord


class TestMessageRecord(unittest.TestCase):

    def test_smoke(self):
        messageRecord = MessageRecord(
            msg='msg',
            callerName='callerName',
            level=10,
            publishTime=datetime.datetime.utcnow(),
        )
        msgStr = messageRecord.get_formattedMessageStr()
        self.assertIsInstance(msgStr, str)

    def test_errors(self):
        with self.assertRaises(TypeValidationError):
            _ = MessageRecord(
                msg=1,
                callerName='callerName',
                level=10,
                publishTime=datetime.datetime.utcnow(),
            )
