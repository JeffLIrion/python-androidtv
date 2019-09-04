import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, '..')

from androidtv import constants, ha_state_detection_rules_validator
from androidtv.firetv import FireTV
from . import patchers


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
STATE_NONE = (None, None, None)

STATE_DETECTION_RULES1 = {'com.amazon.tv.launcher': ['off']}
STATE_DETECTION_RULES2 = {'com.amazon.tv.launcher': ['media_session_state', 'off']}
STATE_DETECTION_RULES3 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES4 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 1}}, 'paused']}
STATE_DETECTION_RULES5 = {'com.amazon.tv.launcher': ['audio_state']}

STATE_DETECTION_RULES_INVALID1 = {'com.amazon.tv.launcher': 'off'}
STATE_DETECTION_RULES_INVALID2 = {'com.amazon.tv.launcher': ['stopped']}
STATE_DETECTION_RULES_INVALID3 = {'com.amazon.tv.launcher': [{'off': {'invalid': 1}}]}


class TestFireTVPython(unittest.TestCase):
    PATCH_KEY = 'python'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            self.ftv = FireTV('IP:PORT')

    def test_get_device_properties(self):
        """Check that ``get_device_properties`` works correctly.

        """
        with patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            device_properties = self.ftv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT1, device_properties)

        with patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            device_properties = self.ftv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT2, device_properties)

    def test_audio_state(self):
        """Check that the ``audio_state`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            audio_state = self.ftv.audio_state
            self.assertEqual(audio_state, None)

        with patchers.patch_shell('0')[self.PATCH_KEY]:
            audio_state = self.ftv.audio_state
            self.assertEqual(audio_state, constants.STATE_IDLE)

        with patchers.patch_shell('1')[self.PATCH_KEY]:
            audio_state = self.ftv.audio_state
            self.assertEqual(audio_state, constants.STATE_PAUSED)

        with patchers.patch_shell('2')[self.PATCH_KEY]:
            audio_state = self.ftv.audio_state
            self.assertEqual(audio_state, constants.STATE_PLAYING)

    def test_current_app(self):
        """Check that the ``current_app`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            current_app = self.ftv.current_app
            self.assertEqual(current_app, None)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            current_app = self.ftv.current_app
            self.assertEqual(current_app, None)

        with patchers.patch_shell(CURRENT_APP_OUTPUT)[self.PATCH_KEY]:
            current_app = self.ftv.current_app
            self.assertEqual(current_app, "com.amazon.tv.launcher")

    def test_media_session_state(self):
        """Check that the ``media_session_state`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            media_session_state = self.ftv.media_session_state
            self.assertEqual(media_session_state, None)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            media_session_state = self.ftv.media_session_state
            self.assertEqual(media_session_state, None)

        with patchers.patch_shell(MEDIA_SESSION_STATE_OUTPUT)[self.PATCH_KEY]:
            media_session_state = self.ftv.media_session_state
            self.assertEqual(media_session_state, 2)

    def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            running_apps = self.ftv.running_apps
            self.assertEqual(running_apps, None)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            running_apps = self.ftv.running_apps
            self.assertEqual(running_apps, None)

        with patchers.patch_shell(RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            running_apps = self.ftv.running_apps
            self.assertListEqual(running_apps, RUNNING_APPS_LIST)

    def test_get_properties(self):
        """Check that ``get_properties()`` works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            properties = self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT_NONE)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            properties = self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT1)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            properties = self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT2)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
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
        with patchers.patch_connect(False)[self.PATCH_KEY]:
            self.ftv.connect()
        state = self.ftv.update()
        self.assertTupleEqual(state, STATE_NONE)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(self.ftv.connect())

        with patchers.patch_shell(None)[self.PATCH_KEY]:
            state = self.ftv.update()
            self.assertTupleEqual(state, STATE_NONE)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            state = self.ftv.update()
            self.assertTupleEqual(state, STATE1)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            state = self.ftv.update()
            self.assertTupleEqual(state, STATE2)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
            state = self.ftv.update()
            self.assertTupleEqual(state, STATE3)

    def assertUpdate(self, get_properties, update):
        """Check that the results of the `update` method are as expected.

        """
        with patch('androidtv.firetv.FireTV.get_properties', return_value=get_properties):
            self.assertTupleEqual(self.ftv.update(), update)

    def test_state_detection(self):
        """Check that the state detection works as expected.

        """
        self.assertUpdate([True, True, 1, constants.APP_NETFLIX, 3, [constants.APP_NETFLIX]],
                          (constants.STATE_PLAYING, constants.APP_NETFLIX, [constants.APP_NETFLIX]))


class TestFireTVServer(TestFireTVPython):
    PATCH_KEY = 'server'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            self.ftv = FireTV('IP:PORT', adb_server_ip='ADB_SERVER_PORT')


class TestFireTVStateDetectionRules(unittest.TestCase):
    def test_state_detection_rules_validator(self):
        """Check that ``state_detection_rules_validator()`` works correctly.

        """
        with self.assertRaises(KeyError):
            ftv = FireTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES_INVALID1)

        with self.assertRaises(KeyError):
            ftv = FireTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES_INVALID2)

        with self.assertRaises(KeyError):
            ftv = FireTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES_INVALID3)

    def test_ha_state_detection_rules_validator(self):
        """Check that ``ha_state_detection_rules_validator()`` works correctly.

        """
        with self.assertRaises(AssertionError):
            for app_id, rules in STATE_DETECTION_RULES_INVALID1.items():
                ha_state_detection_rules_validator(AssertionError)(rules)


if __name__ == "__main__":
    unittest.main()
