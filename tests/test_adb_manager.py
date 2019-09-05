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


def raise_runtime_error(*args, **kwargs):
    raise RuntimeError


class LockedLock(object):
    def acquire(self, *args, **kwargs):
        return False


def return_empty_list(*args, **kwargs):
    return []


class TestADBPython(unittest.TestCase):
    """Test the `ADBPython` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        self.adb = ADBPython('IP:PORT')

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

    def test_adb_shell_fail(self):
        """Test when an ADB command is not sent because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertIsNone(self.adb.shell("TEST"))

        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            with patch.object(self.adb, '_adb_lock', LockedLock):
                self.assertIsNone(self.adb.shell("TEST"))

    def test_adb_shell_success(self):
        """Test when an ADB command is successfully sent.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.assertEqual(self.adb.shell("TEST"), "TEST")
        

class TestADBServer(TestADBPython):
    """Test the `ADBServer` class."""

    PATCH_KEY = 'server'

    def setUp(self):
        """Create an `ADBServer` instance.

        """
        self.adb = ADBServer('IP:PORT', 'ADB_SERVER_IP')

    def test_available(self):
        """Test that the ``available`` property works correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.adb._available = False
            self.assertTrue(self.adb.available)

        with patchers.patch_connect(True)[self.PATCH_KEY], patch('{}.patchers.ClientFakeSuccess.devices'.format(__name__), raise_runtime_error):
            self.assertFalse(self.adb.available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())
            self.adb._available = False
            self.assertTrue(self.adb.available)

        with patch('{}.patchers.DeviceFake.get_serial_no'.format(__name__), raise_runtime_error):
            self.assertFalse(self.adb.available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

        with patch.object(self.adb._adb_client, 'devices', return_empty_list):
            self.assertFalse(self.adb.available)

    def test_connect_fail_server(self):
        """Test that the ``connect`` method works correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.adb.connect())

        with patch('{}.patchers.ClientFakeSuccess.devices'.format(__name__), raise_runtime_error):#, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertFalse(self.adb.connect())


class TestADBPythonWithAuthentication(unittest.TestCase):
    """Test the `ADBPython` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        self.adb = ADBPython('IP:PORT', 'adbkey')

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
