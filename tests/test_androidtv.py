import sys
import unittest


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

# `dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && (dumpsys media_session | grep -m 1 'state=PlaybackState {' || echo) && dumpsys window windows | grep mCurrentFocus && dumpsys audio`
GET_PROPERTIES_OUTPUT1 = "1"
GET_PROPERTIES_DICT1 = {'screen_on': True,
                        'awake': False,
                        'wake_lock_size': -1,
                        'media_session_state': None,
                        'current_app': None,
                        'audio_state': None,
                        'device': None,
                        'is_volume_muted': None,
                        'volume': None}
STATE1 = (constants.STATE_IDLE, None, None, None, None)

# `dumpsys power | grep 'Display Power' | grep -q 'state=ON' && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && (dumpsys media_session | grep -m 1 'state=PlaybackState {' || echo) && dumpsys window windows | grep mCurrentFocus && dumpsys audio`
GET_PROPERTIES_OUTPUT2 = """11Wake Locks: size=2

  mCurrentFocus=Window{c82ee5e u0 com.amazon.tv.launcher/com.amazon.tv.launcher.ui.HomeActivity_vNext}
""" + DUMPSYS_AUDIO_ON
GET_PROPERTIES_DICT2 = {'screen_on': True,
                        'awake': True,
                        'wake_lock_size': 2,
                        'media_session_state': None,
                        'current_app': 'com.amazon.tv.launcher',
                        'audio_state': constants.STATE_IDLE,
                        'device': 'hmdi_arc',
                        'is_volume_muted': False,
                        'volume': 22}
STATE2 = (constants.STATE_PLAYING, 'com.amazon.tv.launcher', 'hmdi_arc', False, 22/60.)

GET_PROPERTIES_DICT_NONE = {'screen_on': None,
                            'awake': None,
                            'wake_lock_size': None,
                            'media_session_state': None,
                            'current_app': None,
                            'audio_state': None,
                            'device': None,
                            'is_volume_muted': None,
                            'volume': None}


def _adb_shell_patched(self):
    def _adb_shell_method(cmd):
        return self.adb_shell_output

    return _adb_shell_method


class TestAndroidTV(unittest.TestCase):
    def setUp(self):
        self.atv = AndroidTV('127.0.0.1:5555')

        # patch ADB-related methods
        self.atv.adb_shell = _adb_shell_patched(self.atv)
        self.atv._adb = True
        self.atv._available = True
        self.atv.adb_shell_output = None

    def test_device(self):
        """Check that the ``device`` property works correctly.

        """
        self.atv.adb_shell_output = None
        device = self.atv.device
        self.assertEqual(None, device)

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
        self.assertEqual(volume, None)

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
        self.assertEqual(is_volume_muted, None)

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

    def test_update(self):
        """Check that the ``update`` method works correctly.

        """
        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT1
        state = self.atv.update()
        self.assertTupleEqual(state, STATE1)

        self.atv.adb_shell_output = GET_PROPERTIES_OUTPUT2
        state = self.atv.update()
        self.assertTupleEqual(state, STATE2)


if __name__ == "__main__":
    unittest.main()
