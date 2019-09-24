import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, '..')

from androidtv import setup
from androidtv.androidtv import AndroidTV
from androidtv.firetv import FireTV
from . import patchers


DEVICE_PROPERTIES_OUTPUT1 = "Amazon\n\n\n\n\n."

DEVICE_PROPERTIES_DICT1 = {'manufacturer': 'Amazon',
                           'model': '',
                           'serialno': None,
                           'sw_version': '',
                           'wifimac': None,
                           'ethmac': None}

DEVICE_PROPERTIES_OUTPUT2 = "Not Amazon\n\n\n\n\n."

DEVICE_PROPERTIES_DICT2 = {'manufacturer': 'Not Amazon',
                           'model': '',
                           'serialno': None,
                           'sw_version': '',
                           'wifimac': None,
                           'ethmac': None}


class TestSetup(unittest.TestCase):
    PATCH_KEY = 'python'

    def test_setup(self):
        """Test that the ``setup`` function works correctly.
        """
        with self.assertRaises(ValueError):
            setup('IP:5555', device_class='INVALID')

        with patchers.patch_adb_device, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            ftv = setup('IP:5555')
            self.assertIsInstance(ftv, FireTV)
            self.assertDictEqual(ftv.device_properties, DEVICE_PROPERTIES_DICT1)

        with patchers.patch_adb_device, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            atv = setup('IP:5555')
            self.assertIsInstance(atv, AndroidTV)
            self.assertDictEqual(atv.device_properties, DEVICE_PROPERTIES_DICT2)

        with patchers.patch_adb_device, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            ftv = setup('IP:5555', device_class='androidtv')
            self.assertIsInstance(ftv, AndroidTV)
            self.assertDictEqual(ftv.device_properties, DEVICE_PROPERTIES_DICT1)

        with patchers.patch_adb_device, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            atv = setup('IP:5555', device_class='firetv')
            self.assertIsInstance(atv, FireTV)
            self.assertDictEqual(atv.device_properties, DEVICE_PROPERTIES_DICT2)


if __name__ == "__main__":
    unittest.main()
