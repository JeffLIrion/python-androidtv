import sys
import unittest


sys.path.insert(0, "..")

from androidtv import constants
from androidtv.androidtv.base_androidtv import BaseAndroidTV
from androidtv.firetv.base_firetv import BaseFireTV


class TestBaseTV(unittest.TestCase):
    def test_base_android_tv(self):
        """Test that ``BaseAndroidTV.__init__`` runs without error."""
        BaseAndroidTV("host")

    def test_base_fire_tv(self):
        """Test that ``BaseFireTV.__init__`` runs without error."""
        BaseFireTV("host")
