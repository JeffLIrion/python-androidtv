import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, '..')

from androidtv import constants
from androidtv.androidtv.androidtv_sync import AndroidTVSync
from . import patchers


STREAM_MUSIC_EMPTY = "- STREAM_MUSIC:\n \n- STREAM"

STREAM_MUSIC_OFF = """- STREAM_MUSIC:
   Muted: false
   Min: 0
   Max: 60
   Current: 2 (speaker): 20, 40000 (hmdi_arc): 27, 40000000 (default): 15
   Devices: speaker
- STREAM_ALARM:
   Muted: true
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker"""

STREAM_MUSIC_NO_VOLUME = """- STREAM_MUSIC:
   Muted: false
   Min: 0
   Max: 60
   Devices: speaker
- STREAM_ALARM:
   Muted: true
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker"""


STREAM_MUSIC_ON = """- STREAM_MUSIC:
   Muted: false
   Min: 0
   Max: 60
   Current: 2 (speaker): 20, 40000 (hmdi_arc): 22, 40000000 (default): 15
   Devices: hmdi_arc
- STREAM_ALARM:
   Muted: false
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker"""


RUNNING_APPS_OUTPUT = """
u0_a18    316   197   1189204 115000 ffffffff 00000000 S com.netflix.ninja
u0_a2     15121 197   998628 24628 ffffffff 00000000 S com.amazon.device.controllermanager"""

RUNNING_APPS_LIST = ['com.netflix.ninja', 'com.amazon.device.controllermanager']


GET_PROPERTIES_OUTPUT1 = ""
GET_PROPERTIES_DICT1 = {'screen_on': False,
                        'awake': False,
                        'audio_state': None,
                        'wake_lock_size': -1,
                        'media_session_state': None,
                        'current_app': None,
                        'audio_output_device': None,
                        'is_volume_muted': None,
                        'volume': None,
                        'running_apps': None}
STATE1 = (constants.STATE_OFF, None, None, None, None, None)

GET_PROPERTIES_OUTPUT2 = "1"
GET_PROPERTIES_DICT2 = {'screen_on': True,
                        'awake': False,
                        'audio_state': None,
                        'wake_lock_size': -1,
                        'media_session_state': None,
                        'current_app': None,
                        'audio_output_device': None,
                        'is_volume_muted': None,
                        'volume': None,
                        'running_apps': None}
STATE2 = (constants.STATE_STANDBY, None, None, None, None, None)

GET_PROPERTIES_OUTPUT3 = """110Wake Locks: size=2
com.amazon.tv.launcher

""" + STREAM_MUSIC_ON
GET_PROPERTIES_DICT3 = {'screen_on': True,
                        'awake': True,
                        'audio_state': constants.STATE_IDLE,
                        'wake_lock_size': 2,
                        'current_app': 'com.amazon.tv.launcher',
                        'media_session_state': None,
                        'audio_output_device': 'hmdi_arc',
                        'is_volume_muted': False,
                        'volume': 22,
                        'running_apps': None}
STATE3 = (constants.STATE_PLAYING, 'com.amazon.tv.launcher', ['com.amazon.tv.launcher'], 'hmdi_arc', False, (22 / 60.))

GET_PROPERTIES_OUTPUT3A = GET_PROPERTIES_OUTPUT3[:1]
GET_PROPERTIES_OUTPUT3B = GET_PROPERTIES_OUTPUT3[:2]
GET_PROPERTIES_OUTPUT3C = GET_PROPERTIES_OUTPUT3[:3]
GET_PROPERTIES_OUTPUT3D = GET_PROPERTIES_OUTPUT3.splitlines()[0]
GET_PROPERTIES_OUTPUT3E = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:2])
GET_PROPERTIES_OUTPUT3F = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:3])
GET_PROPERTIES_OUTPUT3G = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:4])

GET_PROPERTIES_DICT3A = {'screen_on': True,
                         'awake': False,
                         'audio_state': None,
                         'wake_lock_size': -1,
                         'current_app': None,
                         'media_session_state': None,
                         'audio_output_device': None,
                         'is_volume_muted': None,
                         'volume': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3B = {'screen_on': True,
                         'awake': True,
                         'audio_state': None,
                         'wake_lock_size': -1,
                         'current_app': None,
                         'media_session_state': None,
                         'audio_output_device': None,
                         'is_volume_muted': None,
                         'volume': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3C = {'screen_on': True,
                         'awake': True,
                         'audio_state': constants.STATE_IDLE,
                         'wake_lock_size': -1,
                         'current_app': None,
                         'media_session_state': None,
                         'audio_output_device': None,
                         'is_volume_muted': None,
                         'volume': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3D = {'screen_on': True,
                         'awake': True,
                         'audio_state': constants.STATE_IDLE,
                         'wake_lock_size': 2,
                         'current_app': None,
                         'media_session_state': None,
                         'audio_output_device': None,
                         'is_volume_muted': None,
                         'volume': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3E = {'screen_on': True,
                         'awake': True,
                         'audio_state': constants.STATE_IDLE,
                         'wake_lock_size': 2,
                         'current_app': 'com.amazon.tv.launcher',
                         'media_session_state': None,
                         'audio_output_device': None,
                         'is_volume_muted': None,
                         'volume': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3F = {'screen_on': True,
                         'awake': True,
                         'audio_state': constants.STATE_IDLE,
                         'wake_lock_size': 2,
                         'current_app': 'com.amazon.tv.launcher',
                         'media_session_state': None,
                         'audio_output_device': None,
                         'is_volume_muted': None,
                         'volume': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3G = {'screen_on': True,
                         'awake': True,
                         'audio_state': constants.STATE_IDLE,
                         'wake_lock_size': 2,
                         'current_app': 'com.amazon.tv.launcher',
                         'media_session_state': None,
                         'audio_output_device': None,
                         'is_volume_muted': None,
                         'volume': None,
                         'running_apps': None}

GET_PROPERTIES_OUTPUT4 = """111Wake Locks: size=2
com.amazon.tv.launcher
state=PlaybackState {state=1, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}
"""
GET_PROPERTIES_DICT4 = {'screen_on': True,
                        'awake': True,
                        'audio_state': constants.STATE_PAUSED,
                        'wake_lock_size': 2,
                        'current_app': 'com.amazon.tv.launcher',
                        'media_session_state': 1,
                        'audio_output_device': None,
                        'is_volume_muted': None,
                        'volume': None,
                        'running_apps': None}

GET_PROPERTIES_DICT_NONE = {'screen_on': None,
                            'awake': None,
                            'audio_state': None,
                            'wake_lock_size': None,
                            'media_session_state': None,
                            'current_app': None,
                            'audio_output_device': None,
                            'is_volume_muted': None,
                            'volume': None,
                            'running_apps': None}
STATE_NONE = (None, None, None, None, None, None)

# https://community.home-assistant.io/t/testers-needed-custom-state-detection-rules-for-android-tv-fire-tv/129493/6?u=jefflirion
STATE_DETECTION_RULES_PLEX = {'com.plexapp.android': [{'playing': {'media_session_state': 3,
                                                                   'wake_lock_size': 3}},
                                                      {'paused': {'media_session_state': 3,
                                                                  'wake_lock_size': 1}},
                                                      'idle']}

# Plex: idle
GET_PROPERTIES_OUTPUT_PLEX_IDLE = """110Wake Locks: size=1
com.plexapp.android

""" + STREAM_MUSIC_ON

GET_PROPERTIES_DICT_PLEX_IDLE = {'screen_on': True,
                                    'awake': True,
                                    'audio_state': constants.STATE_IDLE,
                                    'wake_lock_size': 1,
                                    'media_session_state': None,
                                    'current_app': 'com.plexapp.android',
                                    'audio_output_device': 'hmdi_arc',
                                    'is_volume_muted': False,
                                    'volume': 22,
                                    'running_apps': None}

STATE_PLEX_IDLE = (constants.STATE_PLAYING, 'com.plexapp.android', ['com.plexapp.android'], 'hmdi_arc', False, 22/60.)

# Plex: playing
GET_PROPERTIES_OUTPUT_PLEX_PLAYING = """110Wake Locks: size=3
com.plexapp.android
state=3
""" + STREAM_MUSIC_ON

GET_PROPERTIES_DICT_PLEX_PLAYING = {'screen_on': True,
                                    'awake': True,
                                    'audio_state': constants.STATE_IDLE,
                                    'wake_lock_size': 3,
                                    'media_session_state': 3,
                                    'current_app': 'com.plexapp.android',
                                    'audio_output_device': 'hmdi_arc',
                                    'is_volume_muted': False,
                                    'volume': 22,
                                    'running_apps': None}

STATE_PLEX_PLAYING = (constants.STATE_PLAYING, 'com.plexapp.android', ['com.plexapp.android'], 'hmdi_arc', False, 22/60.)

# Plex: paused
GET_PROPERTIES_OUTPUT_PLEX_PAUSED = """110Wake Locks: size=1
com.plexapp.android
state=3
""" + STREAM_MUSIC_ON

GET_PROPERTIES_DICT_PLEX_PAUSED = {'screen_on': True,
                                   'awake': True,
                                   'audio_state': constants.STATE_IDLE,
                                   'wake_lock_size': 1,
                                   'media_session_state': 3,
                                   'current_app': 'com.plexapp.android',
                                   'audio_output_device': 'hmdi_arc',
                                   'is_volume_muted': False,
                                   'volume': 22,
                                   'running_apps': None}

STATE_PLEX_PAUSED = (constants.STATE_PAUSED, 'com.plexapp.android', ['com.plexapp.android'], 'hmdi_arc', False, 22/60.)

STATE_DETECTION_RULES1 = {'com.amazon.tv.launcher': ['off']}
STATE_DETECTION_RULES2 = {'com.amazon.tv.launcher': ['media_session_state', 'off']}
STATE_DETECTION_RULES3 = {'com.amazon.tv.launcher': [{'idle': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES4 = {'com.amazon.tv.launcher': [{'idle': {'wake_lock_size': 1}}, 'paused']}
STATE_DETECTION_RULES5 = {'com.amazon.tv.launcher': ['audio_state']}


class TestAndroidTVSyncPython(unittest.TestCase):
    PATCH_KEY = 'python'
    ADB_ATTR = '_adb'

    def setUp(self):
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv = AndroidTVSync('HOST', 5555)
            self.atv.adb_connect()

    def test_turn_on_off(self):
        """Test that the ``AndroidTVSync.turn_on`` and ``AndroidTVSync.turn_off`` methods work correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv.turn_on()
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " || input keyevent {0}".format(constants.KEY_POWER))

            self.atv.turn_off()
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_POWER))

    def test_start_intent(self):
        """Test that the ``start_intent`` method works correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv.start_intent("TEST")
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "am start -a android.intent.action.VIEW -d TEST")

    def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            running_apps = self.atv.running_apps()
            self.assertIsNone(running_apps, None)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            running_apps = self.atv.running_apps()
            self.assertIsNone(running_apps, None)

        with patchers.patch_shell(RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            running_apps = self.atv.running_apps()
            self.assertListEqual(running_apps, RUNNING_APPS_LIST)

    def test_audio_output_device(self):
        """Check that the ``device`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            audio_output_device = self.atv.audio_output_device()
            self.assertIsNone(audio_output_device)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            audio_output_device = self.atv.audio_output_device()
            self.assertIsNone(audio_output_device)

        with patchers.patch_shell(' ')[self.PATCH_KEY]:
            audio_output_device = self.atv.audio_output_device()
            self.assertIsNone(audio_output_device)

        with patchers.patch_shell(STREAM_MUSIC_EMPTY)[self.PATCH_KEY]:
            audio_output_device = self.atv.audio_output_device()
            self.assertIsNone(audio_output_device)

        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            audio_output_device = self.atv.audio_output_device()
            self.assertEqual('speaker', audio_output_device)

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            audio_output_device = self.atv.audio_output_device()
            self.assertEqual('hmdi_arc', audio_output_device)

    def test_volume(self):
        """Check that the ``volume`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            volume = self.atv.volume()
            self.assertIsNone(volume)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            volume = self.atv.volume()
            self.assertIsNone(volume)

        with patchers.patch_shell(' ')[self.PATCH_KEY]:
            volume = self.atv.volume()
            self.assertIsNone(volume)

        with patchers.patch_shell(STREAM_MUSIC_EMPTY)[self.PATCH_KEY]:
            volume = self.atv.volume()
            self.assertIsNone(volume)

        with patchers.patch_shell(STREAM_MUSIC_NO_VOLUME)[self.PATCH_KEY]:
            volume = self.atv.volume()
            self.assertIsNone(volume)

        self.atv.max_volume = None
        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            volume = self.atv.volume()
            self.assertEqual(volume, 20)
            self.assertEqual(self.atv.max_volume, 60.)

        self.atv.max_volume = None
        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            volume = self.atv.volume()
            self.assertEqual(volume, 22)
            self.assertEqual(self.atv.max_volume, 60.)

    def test_volume_level(self):
        """Check that the ``volume_level`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            volume_level = self.atv.volume_level()
            self.assertIsNone(volume_level)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            volume_level = self.atv.volume_level()
            self.assertIsNone(volume_level)

        with patchers.patch_shell(' ')[self.PATCH_KEY]:
            volume_level = self.atv.volume_level()
            self.assertIsNone(volume_level)

        with patchers.patch_shell(STREAM_MUSIC_EMPTY)[self.PATCH_KEY]:
            volume_level = self.atv.volume_level()
            self.assertIsNone(volume_level)

        with patchers.patch_shell(STREAM_MUSIC_NO_VOLUME)[self.PATCH_KEY]:
            volume_level = self.atv.volume_level()
            self.assertIsNone(volume_level)

        self.atv.max_volume = None
        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            volume_level = self.atv.volume_level()
            self.assertEqual(volume_level, 20./60)
            self.assertEqual(self.atv.max_volume, 60.)

        self.atv.max_volume = None
        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            volume_level = self.atv.volume_level()
            self.assertEqual(volume_level, 22./60)
            self.assertEqual(self.atv.max_volume, 60.)

    def test_is_volume_muted(self):
        """Check that the ``is_volume_muted`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted()
            self.assertIsNone(is_volume_muted)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted()
            self.assertIsNone(is_volume_muted)

        with patchers.patch_shell(' ')[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted()
            self.assertIsNone(is_volume_muted)

        with patchers.patch_shell(STREAM_MUSIC_EMPTY)[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted()
            self.assertIsNone(is_volume_muted)

        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted()
            self.assertFalse(is_volume_muted)

    def test_set_volume_level(self):
        """Check that the ``set_volume_level`` method works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5)
            self.assertIsNone(new_volume_level)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5)
            self.assertIsNone(new_volume_level)

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 30")

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(30./60)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 30")

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(22./60)
            self.assertEqual(new_volume_level, 22./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 22")

    def test_volume_up(self):
        """Check that the ``volume_up`` method works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertEqual(new_volume_level, 23./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = self.atv.volume_up(23./60)
            self.assertEqual(new_volume_level, 24./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertEqual(new_volume_level, 21./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = self.atv.volume_up(21./60)
            self.assertEqual(new_volume_level, 22./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

    def test_volume_down(self):
        """Check that the ``volume_down`` method works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertEqual(new_volume_level, 21./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = self.atv.volume_down(21./60)
            self.assertEqual(new_volume_level, 20./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertEqual(new_volume_level, 19./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = self.atv.volume_down(19./60)
            self.assertEqual(new_volume_level, 18./60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

    def test_get_properties(self):
        """Check that the ``get_properties`` method works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_NONE)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT1)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT2)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3A)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3A)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3B)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3B)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3C)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3C)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3D)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3D)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3E)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3E)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3F)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3F)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT4)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT4)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT4)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=False)
            self.assertEqual(properties, GET_PROPERTIES_DICT4)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT4)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=False, lazy=False)
            self.assertEqual(properties, GET_PROPERTIES_DICT4)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_IDLE)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_IDLE)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PLAYING)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PLAYING)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PAUSED)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PAUSED)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PAUSED)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PAUSED)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PAUSED)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(get_running_apps=False, lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PAUSED)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PAUSED + RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            true_properties = GET_PROPERTIES_DICT_PLEX_PAUSED.copy()
            true_properties['running_apps'] = RUNNING_APPS_LIST
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=True)
            self.assertEqual(properties, true_properties)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PAUSED + RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            true_properties = GET_PROPERTIES_DICT_PLEX_PAUSED.copy()
            true_properties['running_apps'] = RUNNING_APPS_LIST
            properties = self.atv.get_properties_dict(get_running_apps=True, lazy=False)
            self.assertEqual(properties, true_properties)

    def test_update(self):
        """Check that the ``update`` method works correctly.

        """
        with patchers.patch_connect(False)[self.PATCH_KEY]:
            self.atv.adb_connect()
        state = self.atv.update()
        self.assertTupleEqual(state, STATE_NONE)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.atv.adb_connect()

        with patchers.patch_shell(None)[self.PATCH_KEY]:
            state = self.atv.update()
            self.assertTupleEqual(state, STATE_NONE)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            state = self.atv.update()
            self.assertTupleEqual(state, STATE1)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            state = self.atv.update()
            self.assertTupleEqual(state, STATE2)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
            state = self.atv.update()
            self.assertTupleEqual(state, STATE3)

            self.atv._state_detection_rules = STATE_DETECTION_RULES1
            state = self.atv.update()
            self.assertEqual(state[0], constants.STATE_OFF)

            self.atv._state_detection_rules = STATE_DETECTION_RULES2
            state = self.atv.update()
            self.assertEqual(state[0], constants.STATE_OFF)

            self.atv._state_detection_rules = STATE_DETECTION_RULES3
            state = self.atv.update()
            self.assertEqual(state[0], constants.STATE_IDLE)

            self.atv._state_detection_rules = STATE_DETECTION_RULES4
            state = self.atv.update()
            self.assertEqual(state[0], constants.STATE_PAUSED)

            self.atv._state_detection_rules = STATE_DETECTION_RULES5
            state = self.atv.update()
            self.assertEqual(state[0], constants.STATE_IDLE)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3 + RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            self.atv._state_detection_rules = None
            state = self.atv.update(get_running_apps=True)
            true_state = STATE3[:2] + (RUNNING_APPS_LIST,) + STATE3[3:]
            self.assertTupleEqual(state, true_state)

    def assertUpdate(self, get_properties, update):
        """Check that the results of the `update` method are as expected.

        """
        with patch('androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties', return_value=get_properties):
            self.assertTupleEqual(self.atv.update(), update)

    def test_state_detection(self):
        """Check that the state detection works as expected.

        """
        self.atv.max_volume = 60.
        self.assertUpdate([False, False, None, -1, None, None, None, None, None, None],
                          (constants.STATE_OFF, None, None, None, None, None))

        self.assertUpdate([True, False, None, -1, None, None, None, None, None, None],
                          (constants.STATE_STANDBY, None, None, None, None, None))

        # ATV Launcher
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_ATV_LAUNCHER, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_ATV_LAUNCHER, [constants.APP_ATV_LAUNCHER], 'hmdi_arc', False, 0.5))

        # ATV Launcher with custom state detection
        self.atv._state_detection_rules = {constants.APP_ATV_LAUNCHER: [{'idle': {'audio_state': 'idle'}}]}
        self.assertUpdate([True, True, constants.STATE_PAUSED, 2, constants.APP_ATV_LAUNCHER, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_ATV_LAUNCHER, [constants.APP_ATV_LAUNCHER], 'hmdi_arc', False, 0.5))

        self.atv._state_detection_rules = {constants.APP_ATV_LAUNCHER: [{'idle': {'INVALID': 'idle'}}]}
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_ATV_LAUNCHER, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_ATV_LAUNCHER, [constants.APP_ATV_LAUNCHER], 'hmdi_arc', False, 0.5))

        self.atv._state_detection_rules = None

        # Bell Fibe
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_BELL_FIBE, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_BELL_FIBE, [constants.APP_BELL_FIBE], 'hmdi_arc', False, 0.5))

        # Netflix
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_NETFLIX, 2, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PAUSED, constants.APP_NETFLIX, [constants.APP_NETFLIX], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_NETFLIX, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_NETFLIX, [constants.APP_NETFLIX], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_NETFLIX, 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_NETFLIX, [constants.APP_NETFLIX], 'hmdi_arc', False, 0.5))

        # Plex
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_PLEX, 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_PLEX, [constants.APP_PLEX], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 3, constants.APP_PLEX, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 4, constants.APP_PLEX, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 5, constants.APP_PLEX, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 7, constants.APP_PLEX, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 1, constants.APP_PLEX, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PAUSED, constants.APP_PLEX, [constants.APP_PLEX], 'hmdi_arc', False, 0.5))

        # TVheadend
        self.assertUpdate([True, True, constants.STATE_IDLE, 5, constants.APP_TVHEADEND, 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PAUSED, constants.APP_TVHEADEND, [constants.APP_TVHEADEND], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 6, constants.APP_TVHEADEND, 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_TVHEADEND, [constants.APP_TVHEADEND], 'hmdi_arc', False, 0.5))
        
        self.assertUpdate([True, True, constants.STATE_IDLE, 1, constants.APP_TVHEADEND, 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_TVHEADEND, [constants.APP_TVHEADEND], 'hmdi_arc', False, 0.5))

        # VLC
        self.assertUpdate([True, True, constants.STATE_IDLE, 6, constants.APP_VLC, 2, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PAUSED, constants.APP_VLC, [constants.APP_VLC], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 6, constants.APP_VLC, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_VLC, [constants.APP_VLC], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 6, constants.APP_VLC, 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_VLC, [constants.APP_VLC], 'hmdi_arc', False, 0.5))

        # VRV
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_VRV, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_VRV, [constants.APP_VRV], 'hmdi_arc', False, 0.5))

        # YouTube
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_YOUTUBE, 2, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PAUSED, constants.APP_YOUTUBE, [constants.APP_YOUTUBE], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_YOUTUBE, 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, constants.APP_YOUTUBE, [constants.APP_YOUTUBE], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 2, constants.APP_YOUTUBE, 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, constants.APP_YOUTUBE, [constants.APP_YOUTUBE], 'hmdi_arc', False, 0.5))

        # Unknown app
        self.assertUpdate([True, True, constants.STATE_IDLE, 2, 'unknown', 2, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PAUSED, 'unknown', ['unknown'], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 2, 'unknown', 3, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, 'unknown', ['unknown'], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 2, 'unknown', 4, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, 'unknown', ['unknown'], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_PLAYING, 2, 'unknown', None, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, 'unknown', ['unknown'], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 1, 'unknown', None, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PAUSED, 'unknown', ['unknown'], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 2, 'unknown', None, 'hmdi_arc', False, 30, None],
                          (constants.STATE_PLAYING, 'unknown', ['unknown'], 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, constants.STATE_IDLE, 3, 'unknown', None, 'hmdi_arc', False, 30, None],
                          (constants.STATE_IDLE, 'unknown', ['unknown'], 'hmdi_arc', False, 0.5))


class TestAndroidTVSyncServer(TestAndroidTVSyncPython):
    PATCH_KEY = 'server'
    ADB_ATTR = '_adb_device'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv = AndroidTVSync('HOST', 5555, adb_server_ip='ADB_SERVER_IP')
            self.atv.adb_connect()


class TestStateDetectionRulesValidator(unittest.TestCase):
    def test_state_detection_rules_validator(self):
        """Check that the ``state_detection_rules_validator`` function works correctly.

        """
        with patchers.patch_connect(True)['python'], patchers.patch_shell('')['python']:
            # Make sure that no error is raised when the state detection rules are valid
            AndroidTVSync('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES1)
            AndroidTVSync('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES2)
            AndroidTVSync('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES3)
            AndroidTVSync('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES4)
            AndroidTVSync('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES5)


if __name__ == "__main__":
    unittest.main()
