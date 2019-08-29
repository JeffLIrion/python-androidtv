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


class TestADBPython(unittest.TestCase):
    """Test the `ADBPython` class."""

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        self.adb = ADBPython('IP:PORT')

    @patchers.PATCH_PYTHON_ADB_CONNECT_SUCCESS
    def test_connect_success(self):
        """Test when the connect attempt is successful.

        """
        self.assertTrue(self.adb.connect())
        self.assertTrue(self.adb.available)
        self.assertTrue(self.adb._available)

    @patchers.PATCH_PYTHON_ADB_CONNECT_FAIL
    def test_connect_fail(self):
        """Test when the connect attempt fails.

        """
        self.assertFalse(self.adb.connect())
        self.assertFalse(self.adb.available)
        self.assertFalse(self.adb._available)

    def test_adb_shell_fail(self):
        """Test when an ADB command is not sent because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.PATCH_PYTHON_ADB_COMMAND_SUCCESS:
            self.assertIsNone(self.adb.shell("TEST"))

    @patchers.PATCH_PYTHON_ADB_CONNECT_SUCCESS
    def test_adb_shell_success(self):
        """Test when an ADB command is successfully sent.

        """
        self.assertTrue(self.adb.connect())
        with patchers.PATCH_PYTHON_ADB_COMMAND_SUCCESS:
            self.assertEqual("TEST", self.adb.shell("TEST"))


class TestADBServer(unittest.TestCase):
    """Test the `ADBServer` class."""

    def setUp(self):
        """Create an `ADBServer` instance.

        """
        self.adb = ADBServer('IP:PORT', 'ADB_SERVER_IP')

    def test_connect_success(self):
        """Test when the connect attempt is successful.

        """
        with patchers.PATCH_ADB_SERVER_CONNECT_SUCCESS, patchers.PATCH_ADB_SERVER_AVAILABLE2:
            self.assertTrue(self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)


    def test_connect_fail(self):
        """Test when the connect attempt fails.

        """
        with patchers.PATCH_ADB_SERVER_CONNECT_FAIL:
            self.assertFalse(self.adb.connect())
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)

    def test_adb_shell_fail(self):
        """Test when an ADB command is not sent because the device is unavailable.

        """
        with patchers.PATCH_ADB_SERVER_CONNECT_SUCCESS, patchers.PATCH_ADB_SERVER_UNAVAILABLE:
            self.assertIsNone(self.adb.shell("TEST"))

    def test_adb_shell_success(self):
        """Test when an ADB command is successfully sent.

        """
        with patchers.PATCH_ADB_SERVER_CONNECT_SUCCESS, patchers.PATCH_ADB_SERVER_AVAILABLE2:
            self.assertTrue(self.adb.connect())
            self.assertEqual("TEST", self.adb.shell("TEST"))

