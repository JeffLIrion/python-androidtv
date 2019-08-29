import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except:
    # Python2
    from mock import patch


sys.path.insert(0, '..')

from androidtv.adb import ADBPython, ADBServer
from . import patchers


class TestADBPython(unittest.TestCase):
    """TODO."""

    def setUp(self):
        """TODO."""
        self.adb = ADBPython('IP:PORT')

    @patchers.PATCH_PYTHON_ADB_CONNECT_SUCCESS
    def test_connect_success(self):
        """TODO."""
        self.assertTrue(self.adb.connect())
        self.assertTrue(self.adb.available)
        self.assertTrue(self.adb._available)

    @patchers.PATCH_PYTHON_ADB_CONNECT_FAIL
    def test_connect_fail(self):
        """TODO."""
        self.assertFalse(self.adb.connect())
        self.assertFalse(self.adb.available)
        self.assertFalse(self.adb._available)
