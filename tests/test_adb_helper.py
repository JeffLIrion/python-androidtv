import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except:
    # Python2
    from mock import patch


sys.path.insert(0, '..')

from androidtv.adb_helper import ADBPython, ADBServer
from . import patchers
from .patchers import AdbCommandsFakeSuccess
from adb import adb_commands


class TestADBPython(unittest.TestCase):
    """Test the `ADBPython` class."""

    PATCH_INDEX = 0

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        self.adb = ADBPython('IP:PORT')

    def test_connect_success(self):
        """Test when the connect attempt is successful.

        """
        with patchers.patch_connect(True)[self.PATCH_INDEX]:
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

    def test_connect_fail(self):
        """Test when the connect attempt fails.

        """
        with patchers.patch_connect(False)[self.PATCH_INDEX]:
            self.assertFalse(self.adb.connect())
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)

    def test_adb_shell_fail(self):
        """Test when an ADB command is not sent because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_INDEX], patchers.patch_shell(None)[self.PATCH_INDEX]:
            self.assertIsNone(self.adb.shell("TEST"))

    def test_adb_shell_success(self):
        """Test when an ADB command is successfully sent.

        """
        with patchers.patch_connect(True)[self.PATCH_INDEX], patchers.patch_shell("TEST")[self.PATCH_INDEX]:
            self.assertTrue(self.adb.connect())
            self.assertEqual(self.adb.shell("TEST"), "TEST")


class TestADBServer(TestADBPython):
    """Test the `ADBServer` class."""

    PATCH_INDEX = 1

    def setUp(self):
        """Create an `ADBServer` instance.

        """
        self.adb = ADBServer('IP:PORT', 'ADB_SERVER_IP')
