import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, '..')

from androidtv import constants, ha_state_detection_rules_validator, setup
from androidtv.androidtv import AndroidTV
from androidtv.firetv import FireTV
from . import patchers


DEVICE_PROPERTIES_OUTPUT1 = """Amazon
AFTT
SERIALNO
5.1.1
    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff
Device "eth0" does not exist.
"""

DEVICE_PROPERTIES_DICT1 = {'manufacturer': 'Amazon',
                           'model': 'AFTT',
                           'serialno': 'SERIALNO',
                           'sw_version': '5.1.1',
                           'wifimac': 'ab:cd:ef:gh:ij:kl',
                           'ethmac': None}

DEVICE_PROPERTIES_OUTPUT2 = """Not Amazon
AFTT
SERIALNO
5.1.1
Device "wlan0" does not exist.
    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff
"""

DEVICE_PROPERTIES_DICT2 = {'manufacturer': 'Not Amazon',
                           'model': 'AFTT',
                           'serialno': 'SERIALNO',
                           'sw_version': '5.1.1',
                           'wifimac': None,
                           'ethmac': 'ab:cd:ef:gh:ij:kl'}


class TestSetup(unittest.TestCase):
    PATCH_KEY = 'python'

    def test_setup(self):
        """Test that the ``setup`` function works correctly.
        """
        with self.assertRaises(ValueError):
            setup('IP:PORT', device_class='INVALID')

        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            ftv = setup('IP:PORT')
            self.assertIsInstance(ftv, FireTV)
            self.assertDictEqual(ftv.device_properties, DEVICE_PROPERTIES_DICT2)

        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            atv = setup('IP:PORT')
            self.assertIsInstance(atv, AndroidTV)
            self.assertDictEqual(atv.device_properties, DEVICE_PROPERTIES_DICT2)


if __name__ == "__main__":
    unittest.main()
