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
from androidtv.androidtv import AndroidTV
from . import patchers


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
                        'current_app': 'com.amazon.tv.launcher',
                        'media_session_state': None,
                        'audio_state': constants.STATE_IDLE,
                        'device': 'hmdi_arc',
                        'is_volume_muted': False,
                        'volume': 22}
STATE3 = (constants.STATE_PLAYING, 'com.amazon.tv.launcher', 'hmdi_arc', False, 22/60.)

GET_PROPERTIES_OUTPUT3A = GET_PROPERTIES_OUTPUT3[:1]
GET_PROPERTIES_OUTPUT3B = GET_PROPERTIES_OUTPUT3[:2]
GET_PROPERTIES_OUTPUT3C = GET_PROPERTIES_OUTPUT3.splitlines()[0]
GET_PROPERTIES_OUTPUT3D = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:2])
GET_PROPERTIES_OUTPUT3E = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:3])
GET_PROPERTIES_OUTPUT3F = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:4])

GET_PROPERTIES_DICT3A = {'screen_on': True,
                         'awake': False,
                         'wake_lock_size': -1,
                         'current_app': None,
                         'media_session_state': None,
                         'audio_state': None,
                         'device': None,
                         'is_volume_muted': None,
                         'volume': None}
GET_PROPERTIES_DICT3B = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': -1,
                         'current_app': None,
                         'media_session_state': None,
                         'audio_state': None,
                         'device': None,
                         'is_volume_muted': None,
                         'volume': None}
GET_PROPERTIES_DICT3C = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': 2,
                         'current_app': None,
                         'media_session_state': None,
                         'audio_state': None,
                         'device': None,
                         'is_volume_muted': None,
                         'volume': None}
GET_PROPERTIES_DICT3D = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': 2,
                         'current_app': 'com.amazon.tv.launcher',
                         'media_session_state': None,
                         'audio_state': None,
                         'device': None,
                         'is_volume_muted': None,
                         'volume': None}
GET_PROPERTIES_DICT3E = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': 2,
                         'current_app': 'com.amazon.tv.launcher',
                         'media_session_state': None,
                         'audio_state': None,
                         'device': None,
                         'is_volume_muted': None,
                         'volume': None}

GET_PROPERTIES_OUTPUT4 = """11Wake Locks: size=2
com.amazon.tv.launcher
state=1
"""
GET_PROPERTIES_DICT4 = {'screen_on': True,
                        'awake': True,
                        'wake_lock_size': 2,
                        'current_app': 'com.amazon.tv.launcher',
                        'media_session_state': 1,
                        'audio_state': None,
                        'device': None,
                        'is_volume_muted': None,
                        'volume': None}

GET_PROPERTIES_DICT_NONE = {'screen_on': None,
                            'awake': None,
                            'wake_lock_size': None,
                            'media_session_state': None,
                            'current_app': None,
                            'audio_state': None,
                            'device': None,
                            'is_volume_muted': None,
                            'volume': None}
STATE_NONE = (None, None, None, None, None)

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


class TestAndroidTVPython(unittest.TestCase):
    PATCH_KEY = 'python'
    ADB_ATTR = '_adb'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv = AndroidTV('IP:PORT')

    def test_device(self):
        """Check that the ``device`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            device = self.atv.device
            self.assertIsNone(device)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            device = self.atv.device
            self.assertIsNone(device)

        with patchers.patch_shell(DUMPSYS_AUDIO_OFF)[self.PATCH_KEY]:
            device = self.atv.device
            self.assertEqual('speaker', device)

        with patchers.patch_shell(DUMPSYS_AUDIO_ON)[self.PATCH_KEY]:
            device = self.atv.device
            self.assertEqual('hmdi_arc', device)

    def test_turn_on_off(self):
        """Test that the ``AndroidTV.turn_on`` and ``AndroidTV.turn_off`` methods work correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv.turn_on()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " || input keyevent {0}".format(constants.KEY_POWER))

            self.atv.turn_off()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_POWER))

    def test_start_intent(self):
        """Test that the ``AndroidTV.start_intent`` method works correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv.start_intent("TEST")
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "am start -a android.intent.action.VIEW -d TEST")

    def test_volume(self):
        """Check that the ``volume`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            volume = self.atv.volume
            self.assertIsNone(volume)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            volume = self.atv.volume
            self.assertIsNone(volume)

        with patchers.patch_shell(DUMPSYS_AUDIO_OFF)[self.PATCH_KEY]:
            volume = self.atv.volume
            self.assertEqual(volume, 20)
            self.assertEqual(self.atv.max_volume, 60.)

        with patchers.patch_shell(DUMPSYS_AUDIO_ON)[self.PATCH_KEY]:
            volume = self.atv.volume
            self.assertEqual(volume, 22)
            self.assertEqual(self.atv.max_volume, 60.)

    def test_is_volume_muted(self):
        """Check that the ``is_volume_muted`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted
            self.assertIsNone(is_volume_muted)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted
            self.assertIsNone(is_volume_muted)

        with patchers.patch_shell(DUMPSYS_AUDIO_OFF)[self.PATCH_KEY]:
            is_volume_muted = self.atv.is_volume_muted
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

        with patchers.patch_shell(DUMPSYS_AUDIO_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "(input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24) &")

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5, 22./60)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "(input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24 && sleep 1 && input keyevent 24) &")

    def test_volume_up(self):
        """Check that the ``volume_up`` method works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell(DUMPSYS_AUDIO_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertEqual(new_volume_level, 23./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = self.atv.volume_up(23./60)
            self.assertEqual(new_volume_level, 24./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell(DUMPSYS_AUDIO_OFF)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertEqual(new_volume_level, 21./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = self.atv.volume_up(21./60)
            self.assertEqual(new_volume_level, 22./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

    def test_volume_down(self):
        """Check that the ``volume_down`` method works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell('')[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell(DUMPSYS_AUDIO_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertEqual(new_volume_level, 21./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = self.atv.volume_down(21./60)
            self.assertEqual(new_volume_level, 20./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell(DUMPSYS_AUDIO_OFF)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertEqual(new_volume_level, 19./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = self.atv.volume_down(19./60)
            self.assertEqual(new_volume_level, 18./60)
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

    def test_get_properties(self):
        """Check that ``get_properties()`` works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_NONE)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT1)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT2)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3A)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3A)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3B)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3B)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3C)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3C)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3D)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3D)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT3E)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT3E)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT4)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT4)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_STANDBY)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_STANDBY)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PLAYING)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PLAYING)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PAUSED)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PAUSED)

        with patchers.patch_shell(GET_PROPERTIES_OUTPUT_PLEX_PAUSED)[self.PATCH_KEY]:
            properties = self.atv.get_properties_dict(lazy=True)
            self.assertEqual(properties, GET_PROPERTIES_DICT_PLEX_PAUSED)

    def test_update(self):
        """Check that the ``update`` method works correctly.

        """
        with patchers.patch_connect(False)[self.PATCH_KEY]:
            self.atv.connect()
        state = self.atv.update()
        self.assertTupleEqual(state, STATE_NONE)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.atv.connect()

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
            self.assertEqual(state[0], constants.STATE_STANDBY)

            self.atv._state_detection_rules = STATE_DETECTION_RULES4
            state = self.atv.update()
            self.assertEqual(state[0], constants.STATE_PAUSED)

            self.atv._state_detection_rules = STATE_DETECTION_RULES5
            state = self.atv.update()
            self.assertEqual(state[0], constants.STATE_IDLE)

    def assertUpdate(self, get_properties, update):
        """Check that the results of the `update` method are as expected.

        """
        with patch('androidtv.androidtv.AndroidTV.get_properties', return_value=get_properties):
            self.assertTupleEqual(self.atv.update(), update)

    def test_state_detection(self):
        """Check that the state detection works as expected.

        """
        self.atv.max_volume = 60.
        self.assertUpdate([False, False, -1, None, None, None, None, None, None],
                          (constants.STATE_OFF, None, None, None, None))

        self.assertUpdate([True, False, -1, None, None, None, None, None, None],
                          (constants.STATE_IDLE, None, None, None, None))

        # ATV Launcher
        self.assertUpdate([True, True, 2, constants.APP_ATV_LAUNCHER, 3, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, constants.APP_ATV_LAUNCHER, 'hmdi_arc', False, 0.5))

        # ATV Launcher with custom state detection
        self.atv._state_detection_rules = {constants.APP_ATV_LAUNCHER: [{'idle': {'audio_state': 'idle'}}]}
        self.assertUpdate([True, True, 2, constants.APP_ATV_LAUNCHER, 3, None, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, constants.APP_ATV_LAUNCHER, 'hmdi_arc', False, 0.5))

        self.atv._state_detection_rules = {constants.APP_ATV_LAUNCHER: [{'idle': {'INVALID': 'idle'}}]}
        self.assertUpdate([True, True, 2, constants.APP_ATV_LAUNCHER, 3, None, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, constants.APP_ATV_LAUNCHER, 'hmdi_arc', False, 0.5))

        self.atv._state_detection_rules = None

        # Bell Fibe
        self.assertUpdate([True, True, 2, constants.APP_BELL_FIBE, 3, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_IDLE, constants.APP_BELL_FIBE, 'hmdi_arc', False, 0.5))

        # Netflix
        self.assertUpdate([True, True, 2, constants.APP_NETFLIX, 2, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PAUSED, constants.APP_NETFLIX, 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, constants.APP_NETFLIX, 3, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PLAYING, constants.APP_NETFLIX, 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, constants.APP_NETFLIX, 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, constants.APP_NETFLIX, 'hmdi_arc', False, 0.5))

        # Plex
        self.assertUpdate([True, True, 2, constants.APP_PLEX, 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_IDLE, constants.APP_PLEX, 'hmdi_arc', False, 0.5))

        # TVheadend
        self.assertUpdate([True, True, 5, constants.APP_TVHEADEND, 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PAUSED, constants.APP_TVHEADEND, 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 6, constants.APP_TVHEADEND, 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PLAYING, constants.APP_TVHEADEND, 'hmdi_arc', False, 0.5))
        
        self.assertUpdate([True, True, 1, constants.APP_TVHEADEND, 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, constants.APP_TVHEADEND, 'hmdi_arc', False, 0.5))

        # VLC
        self.assertUpdate([True, True, 6, constants.APP_VLC, 2, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PAUSED, constants.APP_VLC, 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 6, constants.APP_VLC, 3, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PLAYING, constants.APP_VLC, 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 6, constants.APP_VLC, 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, constants.APP_VLC, 'hmdi_arc', False, 0.5))

        # VRV
        self.assertUpdate([True, True, 2, constants.APP_VRV, 3, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_IDLE, constants.APP_VRV, 'hmdi_arc', False, 0.5))

        # YouTube
        self.assertUpdate([True, True, 2, constants.APP_YOUTUBE, 2, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PAUSED, constants.APP_YOUTUBE, 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, constants.APP_YOUTUBE, 3, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PLAYING, constants.APP_YOUTUBE, 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, constants.APP_YOUTUBE, 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, constants.APP_YOUTUBE, 'hmdi_arc', False, 0.5))

        # Unknown app
        self.assertUpdate([True, True, 2, 'unknown', 2, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PAUSED, 'unknown', 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, 'unknown', 3, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PLAYING, 'unknown', 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, 'unknown', 4, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, 'unknown', 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, 'unknown', None, constants.STATE_PLAYING, 'hmdi_arc', False, 30],
                          (constants.STATE_PLAYING, 'unknown', 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 1, 'unknown', None, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PAUSED, 'unknown', 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 2, 'unknown', None, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_PLAYING, 'unknown', 'hmdi_arc', False, 0.5))

        self.assertUpdate([True, True, 3, 'unknown', None, constants.STATE_IDLE, 'hmdi_arc', False, 30],
                          (constants.STATE_STANDBY, 'unknown', 'hmdi_arc', False, 0.5))


class TestAndroidTVServer(TestAndroidTVPython):
    PATCH_KEY = 'server'
    ADB_ATTR = '_adb_device'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv = AndroidTV('IP:PORT', adb_server_ip='ADB_SERVER_IP')


class TestStateDetectionRulesValidator(unittest.TestCase):
    def test_state_detection_rules_validator(self):
        """Check that the ``state_detection_rules_validator`` function works correctly.

        """
        with patchers.patch_connect(True)['python'], patchers.patch_shell('')['python']:
            # Make sure that no error is raised when the state detection rules are valid
            atv1 = AndroidTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES1)
            atv2 = AndroidTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES2)
            atv3 = AndroidTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES3)
            atv4 = AndroidTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES4)
            atv5 = AndroidTV('IP:PORT', state_detection_rules=STATE_DETECTION_RULES5)

            # Make sure that an error is raised when the state detection rules are invalid
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID1)
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID2)
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID3)
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID4)
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID5)
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID6)
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID7)
            self.assertRaises(KeyError, AndroidTV, 'IP:PORT', '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID8)


if __name__ == "__main__":
    unittest.main()
