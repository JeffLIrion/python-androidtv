import sys
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

sys.path.insert(0, '..')

from androidtv import constants
from androidtv.firetv import FireTV
from . import patchers


DEVICE_PROPERTIES_OUTPUT1 = """Amazon
AFTT
SERIALNO
5.1.1
link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff
Device "eth0" does not exist.
"""


class TestFireTVPython(unittest.TestCase):
    PATCH_KEY = 'python'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            self.ftv = FireTV('IP:PORT')

    def test_state_detection(self):
        """Check that the state detection works as expected.

        """
        with patch('androidtv.firetv.FireTV.get_properties', return_value=[True, True, 1, constants.APP_NETFLIX, 3, []]):
            state, _, _ = self.ftv.update()
            self.assertEqual(state, constants.STATE_PLAYING)


if __name__ == "__main__":
    unittest.main()
