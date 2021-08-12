from contextlib import contextmanager
import sys
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

sys.path.insert(0, '..')

from adb_shell.transport.tcp_transport import TcpTransport
from androidtv.adb_manager.adb_manager_sync import _acquire, ADBPythonSync, ADBServerSync
from androidtv.exceptions import LockNotAcquiredException
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


PNG_IMAGE = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0fa\x00\x00\x0fa\x01\xa8?\xa7i\x00\x00\x00\x0eIDAT\x18\x95c`\x18\x05\x83\x13\x00\x00\x01\x9a\x00\x01\x16\xca\xd3i\x00\x00\x00\x00IEND\xaeB`\x82'

PNG_IMAGE_NEEDS_REPLACING = PNG_IMAGE[:5] + b'\r' + PNG_IMAGE[5:]

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


class FakeLock(object):
    def __init__(self, *args, **kwargs):
        self._acquired = True

    def acquire(self, *args, **kwargs):
        if self._acquired:
            self._acquired = False
            return True
        return self._acquired

    def release(self, *args, **kwargs):
        self._acquired = True


class LockedLock(FakeLock):
    def __init__(self, *args, **kwargs):
        self._acquired = False


class TestADBPythonSync(unittest.TestCase):
    """Test the `ADBPythonSync` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPythonSync` instance.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPythonSync('HOST', 5555)

    def test_locked_lock(self):
        """Test that the ``FakeLock`` class works as expected.

        """
        with patch.object(self.adb, '_adb_lock', FakeLock()):
            with _acquire(self.adb._adb_lock):
                with self.assertRaises(LockNotAcquiredException):
                    with _acquire(self.adb._adb_lock):
                        pass

            with _acquire(self.adb._adb_lock) as acquired:
                self.assertTrue(acquired)

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

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION[self.PATCH_KEY]:
                self.assertFalse(self.adb.connect())
                self.assertFalse(self.adb.available)
                self.assertFalse(self.adb._available)

    def test_connect_fail_lock(self):
        """Test when the connect attempt fails due to the lock.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patch.object(self.adb, '_adb_lock', LockedLock()):
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
            with patch.object(self.adb, '_adb_lock', LockedLock()):
                with self.assertRaises(LockNotAcquiredException):
                    self.adb.shell("TEST")

                with self.assertRaises(LockNotAcquiredException):
                    self.adb.shell("TEST2")

    def test_adb_shell_success(self):
        """Test when an ADB shell command is successfully sent.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertEqual(self.adb.shell("TEST"), "TEST")

    def test_adb_shell_fail_lock_released(self):
        """Test that the ADB lock gets released when an exception is raised.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

        with patchers.patch_shell("TEST", error=True)[self.PATCH_KEY], patch.object(self.adb, '_adb_lock', FakeLock()):
            with patch('{}.FakeLock.release'.format(__name__)) as release:
                with self.assertRaises(Exception):
                    self.adb.shell("TEST")
                assert release.called

    def test_adb_shell_lock_not_acquired_not_released(self):
        """Test that the lock does not get released if it is not acquired.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertEqual(self.adb.shell("TEST"), "TEST")

        with patchers.patch_shell("TEST")[self.PATCH_KEY], patch.object(self.adb, '_adb_lock', LockedLock()):
            with patch('{}.LockedLock.release'.format(__name__)) as release:
                with self.assertRaises(LockNotAcquiredException):
                    self.adb.shell("TEST")

                release.assert_not_called()

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
                with patch.object(self.adb, '_adb_lock', LockedLock()):
                    with self.assertRaises(LockNotAcquiredException):
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
                with patch.object(self.adb, '_adb_lock', LockedLock()):
                    with self.assertRaises(LockNotAcquiredException):
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

    def test_adb_screencap_fail_unavailable(self):
        """Test when an ADB screencap command fails because the connection is unavailable.

        """
        self.assertFalse(self.adb.available)
        self.assertIsNone(self.adb.screencap())

    def test_adb_screencap_lock_not_acquired(self):
        """Test when an ADB screencap command fails because the ADB lock could not be acquired.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertEqual(self.adb.shell("TEST"), "TEST")

        with patchers.patch_shell(PNG_IMAGE)[self.PATCH_KEY], patch.object(self.adb, '_adb_lock', LockedLock()):
            with patch('{}.LockedLock.release'.format(__name__)) as release:
                with self.assertRaises(LockNotAcquiredException):
                    self.adb.screencap()

                release.assert_not_called()

    def test_adb_screencap_success(self):
        """Test the `screencap` method.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(PNG_IMAGE)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

            if isinstance(self.adb, ADBPythonSync):
                self.assertEqual(self.adb.screencap(), PNG_IMAGE)

                with patchers.patch_shell(PNG_IMAGE_NEEDS_REPLACING)[self.PATCH_KEY]:
                    self.assertEqual(self.adb.screencap(), PNG_IMAGE)

            else:
                with patch.object(self.adb._adb_device, 'screencap', return_value=PNG_IMAGE):
                    self.assertEqual(self.adb.screencap(), PNG_IMAGE)


class TestADBPythonUsbSync(TestADBPythonSync):
    """Test the `ADBPythonSync` class using a USB connection."""

    def setUp(self):
        """Create an `ADBPythonSync` instance with a USB connection.

        """
        # Patch the real `AdbDeviceUsb` with the fake `AdbDeviceTcpFake`
        with patchers.PATCH_ADB_DEVICE_USB, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPythonSync('', 5555)


class TestADBServerSync(TestADBPythonSync):
    """Test the `ADBServerSync` class."""

    PATCH_KEY = 'server'

    def setUp(self):
        """Create an `ADBServerSync` instance.

        """
        self.adb = ADBServerSync('HOST', 5555, 'ADB_SERVER_IP')

    def test_connect_fail_server(self):
        """Test that the ``connect`` method works correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

            with patchers.PATCH_ADB_SERVER_RUNTIME_ERROR:
                self.assertFalse(self.adb.connect())
                self.assertFalse(self.adb.available)
                self.assertFalse(self.adb._available)


class TestADBPythonSyncWithAuthentication(unittest.TestCase):
    """Test the `ADBPythonSync` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPythonSync` instance.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPythonSync('HOST', 5555, 'adbkey')

    def test_connect_success_with_priv_key(self):
        """Test when the connect attempt is successful when using a private key.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patch('androidtv.adb_manager.adb_manager_sync.open', open_priv), patch('androidtv.adb_manager.adb_manager_sync.PythonRSASigner', return_value="TEST"):
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patch('androidtv.adb_manager.adb_manager_sync.open') as patch_open:
                self.assertTrue(self.adb.connect())
                self.assertTrue(self.adb.available)
                self.assertTrue(self.adb._available)
                assert not patch_open.called

    def test_connect_success_with_priv_pub_key(self):
        """Test when the connect attempt is successful when using private and public keys.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patch('androidtv.adb_manager.adb_manager_sync.open', open_priv_pub), patch('androidtv.adb_manager.adb_manager_sync.PythonRSASigner', return_value=None):
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)


class TestADBPythonSyncClose(unittest.TestCase):
    """Test the `ADBPythonSync.close` method."""

    PATCH_KEY = 'python'

    def test_close(self):
        """Test the `ADBPythonSync.close` method.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPythonSync('HOST', 5555)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

            self.adb.close()
            self.assertFalse(self.adb.available)
