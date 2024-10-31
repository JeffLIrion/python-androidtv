import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, "..")

from androidtv.setup_async import setup
from androidtv.androidtv.androidtv_async import AndroidTVAsync
from androidtv.firetv.firetv_async import FireTVAsync

from . import async_patchers
from .async_wrapper import awaiter


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

    @awaiter
    async def test_setup(self):
        """Test that the ``setup`` function works correctly."""
        with self.assertRaises(ValueError):
            await setup("HOST", 5555, device_class="INVALID")

        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[
            self.PATCH_KEY
        ], async_patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            ftv = await setup("HOST", 5555)
            self.assertIsInstance(ftv, FireTVAsync)
            self.assertDictEqual(ftv.device_properties, DEVICE_PROPERTIES_DICT1)

        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[
            self.PATCH_KEY
        ], async_patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            atv = await setup("HOST", 5555)
            self.assertIsInstance(atv, AndroidTVAsync)
            self.assertDictEqual(atv.device_properties, DEVICE_PROPERTIES_DICT2)

        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[
            self.PATCH_KEY
        ], async_patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            ftv = await setup("HOST", 5555, device_class="androidtv")
            self.assertIsInstance(ftv, AndroidTVAsync)
            self.assertDictEqual(ftv.device_properties, DEVICE_PROPERTIES_DICT1)

        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[
            self.PATCH_KEY
        ], async_patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            atv = await setup("HOST", 5555, device_class="firetv")
            self.assertIsInstance(atv, FireTVAsync)
            self.assertDictEqual(atv.device_properties, DEVICE_PROPERTIES_DICT2)


if __name__ == "__main__":
    unittest.main()
