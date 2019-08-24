import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, '..')

from androidtv import constants
from androidtv.firetv import FireTV


# `adb shell getprop ro.product.manufacturer && getprop ro.product.model && getprop ro.serialno && getprop ro.build.version.release && ip addr show wlan0 | grep -m 1 ether && ip addr show eth0 | grep -m 1 ether`
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

DEVICE_PROPERTIES_OUTPUT2 = """Amazon
AFTT
 
5.1.1
    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff
Device "eth0" does not exist.
"""

DEVICE_PROPERTIES_DICT2 = {'manufacturer': 'Amazon',
                           'model': 'AFTT',
                           'serialno': None,
                           'sw_version': '5.1.1',
                           'wifimac': 'ab:cd:ef:gh:ij:kl',
                           'ethmac': None}

# `adb shell CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP`
CURRENT_APP_OUTPUT = "com.amazon.tv.launcher"

# `adb shell CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'`
MEDIA_SESSION_STATE_OUTPUT = "com.amazon.tv.launcher\nstate=PlaybackState {state=2, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}"

# `adb shell ps | grep u0_a`
RUNNING_APPS_OUTPUT = """u0_a18    316   197   1189204 115000 ffffffff 00000000 S com.netflix.ninja
u0_a2     15121 197   998628 24628 ffffffff 00000000 S com.amazon.device.controllermanager"""

RUNNING_APPS_LIST = ['com.netflix.ninja', 'com.amazon.device.controllermanager']

# `adb shell dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && (dumpsys media_session | grep -m 1 'state=PlaybackState {' || echo) && dumpsys window windows | grep mCurrentFocus && ps | grep u0_a`
GET_PROPERTIES_OUTPUT1 = ""
GET_PROPERTIES_DICT1 = {'screen_on': False,
                        'awake': False,
                        'wake_lock_size': -1,
                        'media_session_state': None,
                        'current_app': None,
                        'running_apps': None}
STATE1 = (constants.STATE_OFF, None, None)

# `adb shell dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && ps | grep u0_a`
GET_PROPERTIES_OUTPUT2 = "1"
GET_PROPERTIES_DICT2 = {'screen_on': True,
                        'awake': False,
                        'wake_lock_size': -1,
                        'media_session_state': None,
                        'current_app': None,
                        'running_apps': None}
STATE2 = (constants.STATE_IDLE, None, None)

# `adb shell dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && ps | grep u0_a`
GET_PROPERTIES_OUTPUT3 = """11Wake Locks: size=2
com.amazon.tv.launcher

u0_a2     17243 197   998628 24932 ffffffff 00000000 S com.amazon.device.controllermanager
u0_a2     17374 197   995368 20764 ffffffff 00000000 S com.amazon.device.controllermanager:BluetoothReceiver"""
GET_PROPERTIES_DICT3 = {'screen_on': True,
                        'awake': True,
                        'wake_lock_size': 2,
                        'media_session_state': None,
                        'current_app': 'com.amazon.tv.launcher',
                        'running_apps': ['com.amazon.device.controllermanager', 'com.amazon.device.controllermanager:BluetoothReceiver']}
STATE3 = (constants.STATE_STANDBY, 'com.amazon.tv.launcher', ['com.amazon.device.controllermanager', 'com.amazon.device.controllermanager:BluetoothReceiver'])

GET_PROPERTIES_DICT_NONE = {'screen_on': None,
                            'awake': None,
                            'wake_lock_size': None,
                            'media_session_state': None,
                            'current_app': None,
                            'running_apps': None}

STATE_DETECTION_RULES1 = {'com.amazon.tv.launcher': ['off']}
STATE_DETECTION_RULES2 = {'com.amazon.tv.launcher': ['media_session_state', 'off']}
STATE_DETECTION_RULES3 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES4 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 1}}, 'paused']}
STATE_DETECTION_RULES5 = {'com.amazon.tv.launcher': ['audio_state']}

STATE_DETECTION_RULES_INVALID1 = {'com.amazon.tv.launcher': 'off'}
STATE_DETECTION_RULES_INVALID2 = {'com.amazon.tv.launcher': ['stopped']}
STATE_DETECTION_RULES_INVALID3 = {'com.amazon.tv.launcher': [{'off': {'invalid': 1}}]}


def adb_shell_patched(self, cmd):
    self.adb_shell_cmd = cmd
    if not hasattr(self, 'adb_shell_output') or not self._available:
        self.adb_shell_output = None
    return self.adb_shell_output


def connect_patched(self, always_log_errors=True):
    self._adb = True
    self._available = True
    return self._available


class TestFireTV(unittest.TestCase):
    def setUp(self):
        with patch('androidtv.basetv.BaseTV.connect', connect_patched), patch('androidtv.basetv.BaseTV._adb_shell_python_adb', adb_shell_patched):
            self.ftv = FireTV('127.0.0.1:5555')

    def test_get_device_properties(self):
        """Check that ``get_device_properties`` works correctly.

        """
        self.ftv.adb_shell_output = DEVICE_PROPERTIES_OUTPUT1
        device_properties = self.ftv.get_device_properties()
        self.assertDictEqual(DEVICE_PROPERTIES_DICT1, device_properties)

        self.ftv.adb_shell_output = DEVICE_PROPERTIES_OUTPUT2
        device_properties = self.ftv.get_device_properties()
        self.assertDictEqual(DEVICE_PROPERTIES_DICT2, device_properties)

    def test_audio_state(self):
        """Check that the ``audio_state`` property works correctly.

        """
        self.ftv.adb_shell_output = None
        audio_state = self.ftv.audio_state
        self.assertEqual(audio_state, None)

        self.ftv.adb_shell_output = '0'
        audio_state = self.ftv.audio_state
        self.assertEqual(audio_state, constants.STATE_IDLE)

        self.ftv.adb_shell_output = '1'
        audio_state = self.ftv.audio_state
        self.assertEqual(audio_state, constants.STATE_PAUSED)

        self.ftv.adb_shell_output = '2'
        audio_state = self.ftv.audio_state
        self.assertEqual(audio_state, constants.STATE_PLAYING)

    def test_current_app(self):
        """Check that the ``current_app`` property works correctly.

        """
        self.ftv.adb_shell_output = None
        current_app = self.ftv.current_app
        self.assertEqual(current_app, None)

        self.ftv.adb_shell_output = ''
        current_app = self.ftv.current_app
        self.assertEqual(current_app, None)

        self.ftv.adb_shell_output = CURRENT_APP_OUTPUT
        current_app = self.ftv.current_app
        self.assertEqual(current_app, "com.amazon.tv.launcher")

    def test_media_session_state(self):
        """Check that the ``media_session_state`` property works correctly.

        """
        self.ftv.adb_shell_output = None
        media_session_state = self.ftv.media_session_state
        self.assertEqual(media_session_state, None)

        self.ftv.adb_shell_output = ''
        media_session_state = self.ftv.media_session_state
        self.assertEqual(media_session_state, None)

        self.ftv.adb_shell_output = MEDIA_SESSION_STATE_OUTPUT
        media_session_state = self.ftv.media_session_state
        self.assertEqual(media_session_state, 2)

    def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly.

        """
        self.ftv.adb_shell_output = None
        running_apps = self.ftv.running_apps
        self.assertEqual(running_apps, None)

        self.ftv.adb_shell_output = ''
        running_apps = self.ftv.running_apps
        self.assertEqual(running_apps, None)

        self.ftv.adb_shell_output = RUNNING_APPS_OUTPUT
        running_apps = self.ftv.running_apps
        self.assertListEqual(running_apps, RUNNING_APPS_LIST)

    def test_get_properties(self):
        """Check that ``get_properties()`` works correctly.

        """
        self.ftv.adb_shell_output = None
        properties = self.ftv.get_properties_dict(lazy=True)
        self.assertDictEqual(properties, GET_PROPERTIES_DICT_NONE)

        self.ftv.adb_shell_output = GET_PROPERTIES_OUTPUT1
        properties = self.ftv.get_properties_dict(lazy=True)
        self.assertDictEqual(properties, GET_PROPERTIES_DICT1)

        self.ftv.adb_shell_output = GET_PROPERTIES_OUTPUT2
        properties = self.ftv.get_properties_dict(lazy=True)
        self.assertDictEqual(properties, GET_PROPERTIES_DICT2)

        self.ftv.adb_shell_output = GET_PROPERTIES_OUTPUT3
        properties = self.ftv.get_properties_dict(lazy=True)
        self.assertDictEqual(properties, GET_PROPERTIES_DICT3)

        self.ftv._state_detection_rules = STATE_DETECTION_RULES1
        state = self.ftv.update()
        self.assertEqual(state[0], constants.STATE_OFF)

        self.ftv._state_detection_rules = STATE_DETECTION_RULES2
        state = self.ftv.update()
        self.assertEqual(state[0], constants.STATE_OFF)

        self.ftv._state_detection_rules = STATE_DETECTION_RULES3
        state = self.ftv.update()
        self.assertEqual(state[0], constants.STATE_STANDBY)

        self.ftv._state_detection_rules = STATE_DETECTION_RULES4
        state = self.ftv.update()
        self.assertEqual(state[0], constants.STATE_PAUSED)

        self.ftv._state_detection_rules = STATE_DETECTION_RULES5
        state = self.ftv.update()
        self.assertEqual(state[0], constants.STATE_STANDBY)

    def test_update(self):
        """Check that the ``update`` method works correctly.

        """
        self.ftv.adb_shell_output = GET_PROPERTIES_OUTPUT1
        state = self.ftv.update()
        self.assertTupleEqual(state, STATE1)

        self.ftv.adb_shell_output = GET_PROPERTIES_OUTPUT2
        state = self.ftv.update()
        self.assertTupleEqual(state, STATE2)

        self.ftv.adb_shell_output = GET_PROPERTIES_OUTPUT3
        state = self.ftv.update()
        self.assertTupleEqual(state, STATE3)


@patch('androidtv.basetv.BaseTV.connect', connect_patched)
@patch('androidtv.basetv.BaseTV._adb_shell_python_adb', adb_shell_patched)
class TestFireTVStateDetectionRules(unittest.TestCase):
    def test_state_detection_rules_validator(self):
        """Check that ``state_detection_rules_validator()`` works correctly.

        """
        with self.assertRaises(KeyError):
            ftv = FireTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES_INVALID1)

        with self.assertRaises(KeyError):
            ftv = FireTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES_INVALID2)

        with self.assertRaises(KeyError):
            ftv = FireTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES_INVALID3)


if __name__ == "__main__":
    unittest.main()
