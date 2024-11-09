import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, "..")

from androidtv import setup
from androidtv.androidtv.androidtv_sync import AndroidTVSync
from androidtv.firetv.firetv_sync import FireTVSync
from . import patchers


DEVICE_PROPERTIES_OUTPUT1 = "Amazon\n\n\n123\namazon123"

DEVICE_PROPERTIES_DICT1 = {
    "manufacturer": "Amazon",
    "model": "",
    "serialno": None,
    "sw_version": "123",
    "wifimac": None,
    "ethmac": None,
    "product_id": "amazon123",
}

DEVICE_PROPERTIES_OUTPUT2 = "Not Amazon\n\n\n456\nnotamazon456"

DEVICE_PROPERTIES_DICT2 = {
    "manufacturer": "Not Amazon",
    "model": "",
    "serialno": None,
    "sw_version": "456",
    "wifimac": None,
    "ethmac": None,
    "product_id": "notamazon456",
}


class TestSetup(unittest.TestCase):
    PATCH_KEY = "python"

    def test_setup(self):
        """Test that the ``setup`` function works correctly."""
        with self.assertRaises(ValueError):
            setup("HOST", 5555, device_class="INVALID")

        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(
            DEVICE_PROPERTIES_OUTPUT1
        )[self.PATCH_KEY]:
            ftv = setup("HOST", 5555)
            self.assertIsInstance(ftv, FireTVSync)
            self.assertDictEqual(ftv.device_properties, DEVICE_PROPERTIES_DICT1)

        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(
            DEVICE_PROPERTIES_OUTPUT2
        )[self.PATCH_KEY]:
            atv = setup("HOST", 5555)
            self.assertIsInstance(atv, AndroidTVSync)
            self.assertDictEqual(atv.device_properties, DEVICE_PROPERTIES_DICT2)

        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(
            DEVICE_PROPERTIES_OUTPUT1
        )[self.PATCH_KEY]:
            ftv = setup("HOST", 5555, device_class="androidtv")
            self.assertIsInstance(ftv, AndroidTVSync)
            self.assertDictEqual(ftv.device_properties, DEVICE_PROPERTIES_DICT1)

        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(
            DEVICE_PROPERTIES_OUTPUT2
        )[self.PATCH_KEY]:
            atv = setup("HOST", 5555, device_class="firetv")
            self.assertIsInstance(atv, FireTVSync)
            self.assertDictEqual(atv.device_properties, DEVICE_PROPERTIES_DICT2)


if __name__ == "__main__":
    unittest.main()
