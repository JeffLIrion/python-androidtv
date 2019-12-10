from contextlib import contextmanager
import sys
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

sys.path.insert(0, '..')

from androidtv.adb_manager import ADBPython, ADBServer
from . import patchers


if sys.version_info[0] == 2:
    FileNotFoundError = IOError


class Read(object):
    """Mock an opened file that can be read."""
    def read(self):
        return ''


class ReadFail(object):
    """Mock an opened file that cannot be read."""
    def read(self):
        raise FileNotFoundError


@contextmanager
def open_priv(infile):
    """A patch that will read the private key but not the public key."""
    try:
        if infile == 'adbkey':
            yield Read()
        else:
            yield ReadFail()
    finally:
        pass


@contextmanager
def open_priv_pub(infile):
    try:
        yield Read()
    finally:
        pass


class LockedLock(object):
    @staticmethod
    def acquire(*args, **kwargs):
        return False


def return_empty_list(*args, **kwargs):
    return []


class TestADBPython(unittest.TestCase):
    """Test the `ADBPython` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPython('HOST', 5555)

    def test_connect_success(self):
        """Test when the connect attempt is successful.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

    def test_connect_fail(self):
        """Test when the connect attempt fails.

        """
        with patchers.patch_connect(False)[self.PATCH_KEY]:
            self.assertFalse(self.adb.connect())
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

        with patchers.PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION[self.PATCH_KEY]:
            self.assertFalse(self.adb.connect())
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)

    def test_connect_fail_lock(self):
        """Test when the connect attempt fails due to the lock.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patch.object(self.adb, '_adb_lock', LockedLock):
                self.assertFalse(self.adb.connect())
                self.assertFalse(self.adb.available)
                self.assertFalse(self.adb._available)

    def test_adb_shell_fail(self):
        """Test when an ADB shell command is not sent because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertIsNone(self.adb.shell("TEST"))

        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            with patch.object(self.adb, '_adb_lock', LockedLock):
                self.assertIsNone(self.adb.shell("TEST"))

    def test_adb_shell_success(self):
        """Test when an ADB shell command is successfully sent.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertEqual(self.adb.shell("TEST"), "TEST")

    def test_adb_push_fail(self):
        """Test when an ADB push command is not executed because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
                self.adb.push("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
                patch_push.assert_not_called()

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
                self.assertTrue(self.adb.connect())
                with patch.object(self.adb, '_adb_lock', LockedLock):
                    self.adb.push("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")
                    patch_push.assert_not_called()

    def test_adb_push_success(self):
        """Test when an ADB push command is successfully executed.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
                self.assertTrue(self.adb.connect())
                self.adb.push("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")
                self.assertEqual(patch_push.call_count, 1)

    def test_adb_pull_fail(self):
        """Test when an ADB pull command is not executed because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
                self.adb.pull("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
                patch_pull.assert_not_called()

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
                self.assertTrue(self.adb.connect())
                with patch.object(self.adb, '_adb_lock', LockedLock):
                    self.adb.pull("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")
                    patch_pull.assert_not_called()

    def test_adb_pull_success(self):
        """Test when an ADB pull command is successfully executed.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
                self.assertTrue(self.adb.connect())
                self.adb.pull("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")
                self.assertEqual(patch_pull.call_count, 1)


class TestADBServer(TestADBPython):
    """Test the `ADBServer` class."""

    PATCH_KEY = 'server'

    def setUp(self):
        """Create an `ADBServer` instance.

        """
        self.adb = ADBServer('HOST', 5555, 'ADB_SERVER_IP')

    def test_available(self):
        """Test that the ``available`` property works correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.adb._available = False
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

        with patchers.patch_connect(True)[self.PATCH_KEY], patch('{}.patchers.ClientFakeSuccess.devices'.format(__name__), side_effect=RuntimeError):
            self.assertFalse(self.adb.available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

        with patch('{}.patchers.DeviceFake.get_serial_no'.format(__name__), side_effect=RuntimeError):
            self.assertFalse(self.adb.available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

        with patch.object(self.adb._adb_client, 'devices', return_value=[]):
            self.assertFalse(self.adb.available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

        with patchers.PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION[self.PATCH_KEY]:
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)

    def test_connect_fail_server(self):
        """Test that the ``connect`` method works correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

        with patch('{}.patchers.ClientFakeSuccess.devices'.format(__name__), side_effect=RuntimeError):
            self.assertFalse(self.adb.connect())
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)


class TestADBPythonWithAuthentication(unittest.TestCase):
    """Test the `ADBPython` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPython('HOST', 5555, 'adbkey')

    def test_connect_success_with_priv_key(self):
        """Test when the connect attempt is successful when using a private key.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patch('androidtv.adb_manager.open', open_priv), patch('androidtv.adb_manager.PythonRSASigner', return_value=None):
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

    def test_connect_success_with_priv_pub_key(self):
        """Test when the connect attempt is successful when using private and public keys.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patch('androidtv.adb_manager.open', open_priv_pub), patch('androidtv.adb_manager.PythonRSASigner', return_value=None):
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)


class TestADBPythonClose(unittest.TestCase):
    """Test the `ADBPython.close` method."""

    PATCH_KEY = 'python'

    def test_close(self):
        """Test the `ADBPython.close` method.
        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPython('HOST', 5555)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

            self.adb.close()
            self.assertFalse(self.adb.available)
