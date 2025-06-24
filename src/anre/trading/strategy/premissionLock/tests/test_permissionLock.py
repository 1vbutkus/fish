import unittest

from anre.trading.strategy.premissionLock.permissionLock import PermissionLock


class TestPermissionLock(unittest.TestCase):

    def test_happyPath(self):
        permissionLock = PermissionLock()

        assert permissionLock.get_currentValueInt() == 0

        permissionLock.put_lock(10, 'aaa')
        assert permissionLock.get_currentValueInt() == 10

        permissionLock.put_lock(20, 'bbb')
        assert permissionLock.get_currentValueInt() == 20

        permissionLock.release_lock('bbb')
        assert permissionLock.get_currentValueInt() == 10

        permissionLock.release_lock('aaa')
        assert permissionLock.get_currentValueInt() == 0

        permissionLock.put_lock(20, 'c1')
        permissionLock.put_lock(30, 'c2')
        assert permissionLock.get_currentValueInt() == 30
        permissionLock.sudo_releaseAll()
        assert permissionLock.get_currentValueInt() == 0
        permissionLock.release_lock('c1', raiseIfMissing=True)
        permissionLock.release_lock('c2', raiseIfMissing=True)

    def test_asserts(self):
        permissionLock = PermissionLock()

        with self.assertRaises(AssertionError):
            permissionLock.release_lock('aaa')

        permissionLock.put_lock(10, 'aaa')
        assert permissionLock.get_currentValueInt() == 10

        with self.assertRaises(AssertionError):
            permissionLock.put_lock(10, 'aaa')
