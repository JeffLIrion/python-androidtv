import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, '..')

from androidtv import constants
from androidtv.androidtv import AndroidTV


# `adb shell dumpsys audio`
DUMPSYS_AUDIO_OFF = """MediaFocusControl dump time: 9:00:59 AM

Audio Focus stack entries (last is top of stack):
  source:android.os.BinderProxy@bd99735 -- pack: org.droidtv.playtv -- client: android.media.AudioManager@d4df3dforg.droidtv.playtv.PlayTvActivity@bfb901f -- gain: GAIN -- flags: DELAY_OK|PAUSES_ON_DUCKABLE_LOSS -- loss: none -- notified: true -- uid: 1000 -- attr: AudioAttributes: usage=1 content=3 flags=0x0 tags= bundle=null -- sdk:26


No external focus policy



 Notify on duck:  true

 In ring or call: false


Stream volumes (device: index)
- STREAM_VOICE_CALL:
   Muted: true
   Min: 1
   Max: 5
   Current: 2 (speaker): 2, 40000 (hmdi_arc): 2, 40000000 (default): 1
   Devices: speaker
- STREAM_SYSTEM:
   Muted: true
   Min: 0
   Max: 7
   Current: 2 (speaker): 2, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker
- STREAM_RING:
   Muted: true
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker
- STREAM_MUSIC:
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
   Devices: speaker
- STREAM_NOTIFICATION:
   Muted: true
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker
- STREAM_BLUETOOTH_SCO:
   Muted: true
   Min: 0
   Max: 15
   Current: 2 (speaker): 7, 40000 (hmdi_arc): 7, 40000000 (default): 4
   Devices: speaker
- STREAM_SYSTEM_ENFORCED:
   Muted: true
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker
- STREAM_DTMF:
   Muted: true
   Min: 0
   Max: 15
   Current: 2 (speaker): 5, 40000 (hmdi_arc): 7, 40000000 (default): 4
   Devices: speaker
- STREAM_TTS:
   Muted: true
   Min: 0
   Max: 15
   Current: 2 (speaker): 7, 40000 (hmdi_arc): 7, 40000000 (default): 4
   Devices: speaker
- STREAM_ACCESSIBILITY:
   Muted: true
   Min: 0
   Max: 15
   Current: 2 (speaker): 5, 40000 (hmdi_arc): 7, 40000000 (default): 4
   Devices: speaker

- mute affected streams = 0x2e

Ringer mode:
- mode (internal) = NORMAL
- mode (external) = NORMAL
- ringer mode affected streams = 0x80 (STREAM_SYSTEM_ENFORCED)
- ringer mode muted streams = 0x0
- delegate = ZenModeHelper

Audio routes:
  mMainType=0x0
  mBluetoothName=null

Other state:
  mVolumeController=VolumeController(android.os.BinderProxy@fb5b7ca,mVisible=false)
  mSafeMediaVolumeState=SAFE_MEDIA_VOLUME_ACTIVE
  mSafeMediaVolumeIndex=250
  sIndependentA11yVolume=false
  mPendingVolumeCommand=null
  mMusicActiveMs=0
  mMcc=0
  mCameraSoundForced=false
  mHasVibrator=false
  mVolumePolicy=VolumePolicy[volumeDownToEnterSilent=true,volumeUpToExitSilent=true,doNotDisturbWhenSilent=true,vibrateToSilentDebounce=400]
  mAvrcpAbsVolSupported=false

Audio policies:

PlaybackActivityMonitor dump time: 9:00:59 AM
  ID:23 -- type:android.media.SoundPool -- u/pid:10025/1934 -- state:idle -- attr:AudioAttributes: usage=13 content=4 flags=0x0 tags= bundle=null
  ID:55 -- type:android.media.MediaPlayer -- u/pid:1000/2283 -- state:idle -- attr:AudioAttributes: usage=0 content=0 flags=0x0 tags= bundle=null
  ID:15 -- type:android.media.SoundPool -- u/pid:1000/1723 -- state:idle -- attr:AudioAttributes: usage=13 content=4 flags=0x0 tags= bundle=null
  ID:31 -- type:android.media.MediaPlayer -- u/pid:1000/2010 -- state:idle -- attr:AudioAttributes: usage=0 content=0 flags=0x0 tags= bundle=null
  ID:143 -- type:android.media.SoundPool -- u/pid:10018/15178 -- state:idle -- attr:AudioAttributes: usage=13 content=4 flags=0x0 tags= bundle=null

  ducked players:

  muted player piids:"""


DUMPSYS_AUDIO_ON = """MediaFocusControl dump time: 9:03:06 AM

Audio Focus stack entries (last is top of stack):
  source:android.os.BinderProxy@bd99735 -- pack: org.droidtv.playtv -- client: android.media.AudioManager@d4df3dforg.droidtv.playtv.PlayTvActivity@bfb901f -- gain: GAIN -- flags: DELAY_OK|PAUSES_ON_DUCKABLE_LOSS -- loss: none -- notified: true -- uid: 1000 -- attr: AudioAttributes: usage=1 content=3 flags=0x0 tags= bundle=null -- sdk:26


No external focus policy



 Notify on duck:  true

 In ring or call: false


Stream volumes (device: index)
- STREAM_VOICE_CALL:
   Muted: false
   Min: 1
   Max: 5
   Current: 2 (speaker): 2, 40000 (hmdi_arc): 2, 40000000 (default): 1
   Devices: speaker
- STREAM_SYSTEM:
   Muted: false
   Min: 0
   Max: 7
   Current: 2 (speaker): 2, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: hmdi_arc
- STREAM_RING:
   Muted: false
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker
- STREAM_MUSIC:
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
   Devices: speaker
- STREAM_NOTIFICATION:
   Muted: false
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker
- STREAM_BLUETOOTH_SCO:
   Muted: false
   Min: 0
   Max: 15
   Current: 2 (speaker): 6, 40000 (hmdi_arc): 6, 40000000 (default): 4
   Devices: speaker
- STREAM_SYSTEM_ENFORCED:
   Muted: false
   Min: 0
   Max: 7
   Current: 2 (speaker): 3, 40000 (hmdi_arc): 3, 40000000 (default): 2
   Devices: speaker
- STREAM_DTMF:
   Muted: false
   Min: 0
   Max: 15
   Current: 2 (speaker): 5, 40000 (hmdi_arc): 6, 40000000 (default): 4
   Devices: hmdi_arc
- STREAM_TTS:
   Muted: false
   Min: 0
   Max: 15
   Current: 2 (speaker): 6, 40000 (hmdi_arc): 6, 40000000 (default): 4
   Devices: speaker
- STREAM_ACCESSIBILITY:
   Muted: false
   Min: 0
   Max: 15
   Current: 2 (speaker): 5, 40000 (hmdi_arc): 6, 40000000 (default): 4
   Devices: hmdi_arc

- mute affected streams = 0x2e

Ringer mode:
- mode (internal) = NORMAL
- mode (external) = NORMAL
- ringer mode affected streams = 0x80 (STREAM_SYSTEM_ENFORCED)
- ringer mode muted streams = 0x0
- delegate = ZenModeHelper

Audio routes:
  mMainType=0x8
  mBluetoothName=null

Other state:
  mVolumeController=VolumeController(android.os.BinderProxy@fb5b7ca,mVisible=false)
  mSafeMediaVolumeState=SAFE_MEDIA_VOLUME_ACTIVE
  mSafeMediaVolumeIndex=250
  sIndependentA11yVolume=false
  mPendingVolumeCommand=null
  mMusicActiveMs=0
  mMcc=0
  mCameraSoundForced=false
  mHasVibrator=false
  mVolumePolicy=VolumePolicy[volumeDownToEnterSilent=true,volumeUpToExitSilent=true,doNotDisturbWhenSilent=true,vibrateToSilentDebounce=400]
  mAvrcpAbsVolSupported=false

Audio policies:

PlaybackActivityMonitor dump time: 9:03:06 AM
  ID:23 -- type:android.media.SoundPool -- u/pid:10025/1934 -- state:idle -- attr:AudioAttributes: usage=13 content=4 flags=0x0 tags= bundle=null
  ID:55 -- type:android.media.MediaPlayer -- u/pid:1000/2283 -- state:idle -- attr:AudioAttributes: usage=0 content=0 flags=0x0 tags= bundle=null
  ID:15 -- type:android.media.SoundPool -- u/pid:1000/1723 -- state:idle -- attr:AudioAttributes: usage=13 content=4 flags=0x0 tags= bundle=null
  ID:31 -- type:android.media.MediaPlayer -- u/pid:1000/2010 -- state:idle -- attr:AudioAttributes: usage=0 content=0 flags=0x0 tags= bundle=null
  ID:143 -- type:android.media.SoundPool -- u/pid:10018/15178 -- state:idle -- attr:AudioAttributes: usage=13 content=4 flags=0x0 tags= bundle=null

  ducked players:

  muted player piids:"""

# `dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && dumpsys audio`
GET_PROPERTIES_OUTPUT1 = ""
GET_PROPERTIES_DICT1 = {'screen_on': False,
                        'awake': False,
                        'wake_lock_size': -1,
                        'media_session_state': None,
                        'current_app': None,
                        'audio_state': None,
                        'device': None,
                        'is_volume_muted': None,
                        'volume': None}
STATE1 = (constants.STATE_OFF, None, None, None, None)

# `dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && dumpsys audio`
GET_PROPERTIES_OUTPUT2 = "1"
GET_PROPERTIES_DICT2 = {'screen_on': True,
                        'awake': False,
                        'wake_lock_size': -1,
                        'media_session_state': None,
                        'current_app': None,
                        'audio_state': None,
                        'device': None,
                        'is_volume_muted': None,
                        'volume': None}
STATE2 = (constants.STATE_IDLE, None, None, None, None)

# `dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && dumpsys audio`
GET_PROPERTIES_OUTPUT3 = """11Wake Locks: size=2
com.amazon.tv.launcher

""" + DUMPSYS_AUDIO_ON
GET_PROPERTIES_DICT3 = {'screen_on': True,
                        'awake': True,
                        'wake_lock_size': 2,
                        'media_session_state': None,
                        'current_app': 'com.amazon.tv.launcher',
                        'audio_state': constants.STATE_IDLE,
                        'device': 'hmdi_arc',
                        'is_volume_muted': False,
                        'volume': 22}
STATE3 = (constants.STATE_PLAYING, 'com.amazon.tv.launcher', 'hmdi_arc', False, 22/60.)

GET_PROPERTIES_DICT_NONE = {'screen_on': None,
                            'awake': None,
                            'wake_lock_size': None,
                            'media_session_state': None,
                            'current_app': None,
                            'audio_state': None,
                            'device': None,
                            'is_volume_muted': None,
                            'volume': None}

# https://community.home-assistant.io/t/testers-needed-custom-state-detection-rules-for-android-tv-fire-tv/129493/6?u=jefflirion
STATE_DETECTION_RULES_PLEX = {'com.plexapp.android': [{'playing': {'media_session_state': 3,
                                                                   'wake_lock_size': 3}},
                                                      {'paused': {'media_session_state': 3,
                                                                  'wake_lock_size': 1}},
                                                      'standby']}

# Plex: standby
GET_PROPERTIES_OUTPUT_PLEX_STANDBY = """11Wake Locks: size=1
com.plexapp.android

""" + DUMPSYS_AUDIO_ON

GET_PROPERTIES_DICT_PLEX_STANDBY = {'screen_on': True,
                                    'awake': True,
                                    'wake_lock_size': 1,
                                    'media_session_state': None,
                                    'current_app': 'com.plexapp.android',
                                    'audio_state': constants.STATE_IDLE,
                                    'device': 'hmdi_arc',
                                    'is_volume_muted': False,
                                    'volume': 22}

STATE_PLEX_STANDBY = (constants.STATE_PLAYING, 'com.plexapp.android', 'hmdi_arc', False, 22/60.)

# Plex: playing
GET_PROPERTIES_OUTPUT_PLEX_PLAYING = """11Wake Locks: size=3
com.plexapp.android
state=3
""" + DUMPSYS_AUDIO_ON

GET_PROPERTIES_DICT_PLEX_PLAYING = {'screen_on': True,
                                    'awake': True,
                                    'wake_lock_size': 3,
                                    'media_session_state': 3,
                                    'current_app': 'com.plexapp.android',
                                    'audio_state': constants.STATE_IDLE,
                                    'device': 'hmdi_arc',
                                    'is_volume_muted': False,
                                    'volume': 22}

STATE_PLEX_PLAYING = (constants.STATE_PLAYING, 'com.plexapp.android', 'hmdi_arc', False, 22/60.)

# Plex: paused
GET_PROPERTIES_OUTPUT_PLEX_PAUSED = """11Wake Locks: size=1
com.plexapp.android
state=3
""" + DUMPSYS_AUDIO_ON

GET_PROPERTIES_DICT_PLEX_PAUSED = {'screen_on': True,
                                   'awake': True,
                                   'wake_lock_size': 1,
                                   'media_session_state': 3,
                                   'current_app': 'com.plexapp.android',
                                   'audio_state': constants.STATE_IDLE,
                                   'device': 'hmdi_arc',
                                   'is_volume_muted': False,
                                   'volume': 22}

STATE_PLEX_PAUSED = (constants.STATE_PAUSED, 'com.plexapp.android', 'hmdi_arc', False, 22/60.)

STATE_DETECTION_RULES1 = {'com.amazon.tv.launcher': ['off']}
STATE_DETECTION_RULES2 = {'com.amazon.tv.launcher': ['media_session_state', 'off']}
STATE_DETECTION_RULES3 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES4 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 1}}, 'paused']}
STATE_DETECTION_RULES5 = {'com.amazon.tv.launcher': ['audio_state']}

STATE_DETECTION_RULES_INVALID1 = {'com.amazon.tv.launcher': [123]}
STATE_DETECTION_RULES_INVALID2 = {'com.amazon.tv.launcher': ['INVALID']}
STATE_DETECTION_RULES_INVALID3 = {'com.amazon.tv.launcher': [{'INVALID': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES_INVALID4 = {'com.amazon.tv.launcher': [{'standby': 'INVALID'}]}
STATE_DETECTION_RULES_INVALID5 = {'com.amazon.tv.launcher': [{'standby': {'INVALID': 2}}]}
STATE_DETECTION_RULES_INVALID6 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 'INVALID'}}]}
STATE_DETECTION_RULES_INVALID7 = {'com.amazon.tv.launcher': [{'standby': {'media_session_state': 'INVALID'}}]}
STATE_DETECTION_RULES_INVALID8 = {'com.amazon.tv.launcher': [{'standby': {'audio_state': 123}}]}


def adb_shell_patched(self, cmd):
    self.adb_shell_cmd = cmd
    if not hasattr(self, 'adb_shell_output') or not self._available:
        self.adb_shell_output = None
    return self.adb_shell_output


def connect_patched(self, always_log_errors=True):
    self._adb = True
    self._available = True
    return self._available


class TestAndroidTV(unittest.TestCase):
    def setUp(self):
        with patch('androidtv.basetv.BaseTV.connect', connect_patched), patch('androidtv.basetv.BaseTV._adb_shell_python_adb', adb_shell_patched):
            self.atv = AndroidTV('127.0.0.1:5555')

    def test_device(self):
        """Check that the ``device`` property works correctly.

        """
        self.atv.adb_shell_output = None
        device = self.atv.device
        self.assertIsNone(device)

        self.atv.adb_shell_output = ''
        device = self.atv.device
        self.assertIsNone(device)

        self.atv.adb_shell_output = DUMPSYS_AUDIO_OFF
        device = self.atv.device
        self.assertEqual('speaker', device)

        self.atv.adb_shell_output = DUMPSYS_AUDIO_ON
        device = self.atv.device
        self.assertEqual('hmdi_arc', device)

    def test_volume(self):
        """Check that the ``volume`` property works correctly.

        """
        self.atv.adb_shell_output = None
        volume = self.atv.volume
        self.assertIsNone(volume)

        self.atv.adb_shell_output = ''
        volume = self.atv.volume
        self.assertIsNone(volume)

        self.atv.adb_shell_output = DUMPSYS_AUDIO_OFF
        volume = self.atv.volume
        self.assertEqual(volume, 20)
        self.assertEqual(self.atv.max_volume, 60.)

        self.atv.adb_shell_output = DUMPSYS_AUDIO_ON
        volume = self.atv.volume
        self.assertEqual(volume, 22)
        self.assertEqual(self.atv.max_volume, 60.)

    def test_is_volume_muted(self):
        """Check that the ``is_volume_muted`` property works correctly.

        """
        self.atv.adb_shell_output = None
        is_volume_muted = self.atv.is_volume_muted
        self.assertIsNone(is_volume_muted)

        self.atv.adb_shell_output = ''
        is_volume_muted = self.atv.is_volume_muted
        self.assertIsNone(is_volume_muted)

        self.atv.adb_shell_output = DUMPSYS_AUDIO_OFF
        is_volume_muted = self.atv.is_volume_muted
        self.assertFalse(is_volume_muted)

    def test_get_properties(self):
        """Check that ``get_properties()`` works correctly.

        """
        self.atv.adb_shell_output = None
        properties = self.atv.get_properties_dict(lazy=True)
        self.assertEqual(properties, GET_PROPERTIES_DICT_NONE)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT1
        properties = self.atv.get_properties_dict(lazy=True)
        self.assertEqual(properties, GET_PROPERTIES_DICT1)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT2
        properties = self.atv.get_properties_dict(lazy=True)
        self.assertEqual(properties, GET_PROPERTIES_DICT2)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT3
        properties = self.atv.get_properties_dict(lazy=True)
        self.assertEqual(properties, GET_PROPERTIES_DICT3)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT_PLEX_STANDBY
        properties = self.atv.get_properties_dict(lazy=True)
        self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_STANDBY)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT_PLEX_PLAYING
        properties = self.atv.get_properties_dict(lazy=True)
        self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PLAYING)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT_PLEX_PAUSED
        properties = self.atv.get_properties_dict(lazy=True)
        self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PAUSED)

    def test_update(self):
        """Check that the ``update`` method works correctly.

        """
        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT1
        state = self.atv.update()
        self.assertTupleEqual(state, STATE1)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT2
        state = self.atv.update()
        self.assertTupleEqual(state, STATE2)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT3
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
        self.assertEqual(state[0], constants.STATE_STANDBY)

        self.atv._state_detection_rules = STATE_DETECTION_RULES4
        state = self.atv.update()
        self.assertEqual(state[0], constants.STATE_PAUSED)

        self.atv._state_detection_rules = STATE_DETECTION_RULES5
        state = self.atv.update()
        self.assertEqual(state[0], constants.STATE_IDLE)

    def test_set_volume_level(self):
        """Check that the ``set_volume_level`` method works correctly.

        """
        self.atv.adb_shell_output = None
        new_volume_level = self.atv.set_volume_level(0.5)
        self.assertIsNone(new_volume_level)

        self.atv.adb_shell_output = ''
        new_volume_level = self.atv.set_volume_level(0.5)
        self.assertIsNone(new_volume_level)

        self.atv.adb_shell_output = DUMPSYS_AUDIO_ON
        new_volume_level = self.atv.set_volume_level(0.5)
        self.assertEqual(new_volume_level, 0.5)
        self.assertEqual(self.atv.adb_shell_cmd, "(input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24) &")

        self.atv.adb_shell_output = ''
        new_volume_level = self.atv.set_volume_level(0.5, 22./60)
        self.assertEqual(new_volume_level, 0.5)
        self.assertEqual(self.atv.adb_shell_cmd, "(input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24) &")

    def test_volume_up(self):
        """Check that the ``volume_up`` method works correctly.

        """
        self.atv.adb_shell_output = None
        new_volume_level = self.atv.volume_up()
        self.assertIsNone(new_volume_level)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 24")

        self.atv.adb_shell_output = ''
        new_volume_level = self.atv.volume_up()
        self.assertIsNone(new_volume_level)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 24")

        self.atv.adb_shell_output = DUMPSYS_AUDIO_ON
        new_volume_level = self.atv.volume_up()
        self.assertEqual(new_volume_level, 23./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 24")
        new_volume_level = self.atv.volume_up(23./60)
        self.assertEqual(new_volume_level, 24./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 24")

        self.atv.adb_shell_output = DUMPSYS_AUDIO_OFF
        new_volume_level = self.atv.volume_up()
        self.assertEqual(new_volume_level, 21./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 24")
        new_volume_level = self.atv.volume_up(21./60)
        self.assertEqual(new_volume_level, 22./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 24")

    def test_volume_down(self):
        """Check that the ``volume_down`` method works correctly.

        """
        self.atv.adb_shell_output = None
        new_volume_level = self.atv.volume_down()
        self.assertIsNone(new_volume_level)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 25")

        self.atv.adb_shell_output = ''
        new_volume_level = self.atv.volume_down()
        self.assertIsNone(new_volume_level)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 25")

        self.atv.adb_shell_output = DUMPSYS_AUDIO_ON
        new_volume_level = self.atv.volume_down()
        self.assertEqual(new_volume_level, 21./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 25")
        new_volume_level = self.atv.volume_down(21./60)
        self.assertEqual(new_volume_level, 20./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 25")

        self.atv.adb_shell_output = DUMPSYS_AUDIO_OFF
        new_volume_level = self.atv.volume_down()
        self.assertEqual(new_volume_level, 19./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 25")
        new_volume_level = self.atv.volume_down(19./60)
        self.assertEqual(new_volume_level, 18./60)
        self.assertEqual(self.atv.adb_shell_cmd, "input keyevent 25")


@patch('androidtv.basetv.BaseTV.connect', connect_patched)
@patch('androidtv.basetv.BaseTV._adb_shell_python_adb', adb_shell_patched)
class TestStateDetectionRulesValidator(unittest.TestCase):
    def test_state_detection_rules_validator(self):
        """Check that the ``state_detection_rules_validator`` function works correctly.

        """
        # Make sure that no error is raised when the state detection rules are valid
        atv1 = AndroidTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES1)
        atv2 = AndroidTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES2)
        atv3 = AndroidTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES3)
        atv4 = AndroidTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES4)
        atv5 = AndroidTV('127.0.0.1:5555', state_detection_rules=STATE_DETECTION_RULES5)

        # Make sure that an error is raised when the state detection rules are invalid
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID1)
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID2)
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID3)
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID4)
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID5)
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID6)
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID7)
        self.assertRaises(KeyError, AndroidTV, '127.0.0.1:5555', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID8)


if __name__ == "__main__":
    unittest.main()
