import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, "..")

from androidtv import constants
from androidtv.androidtv.androidtv_sync import AndroidTVSync
from . import patchers


UNKNOWN_APP = "unknown"

HDMI_INPUT_EMPTY = "\n"

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

RUNNING_APPS_LIST = ["com.netflix.ninja", "com.amazon.device.controllermanager"]


GET_PROPERTIES_OUTPUT = (
    True,
    True,
    constants.STATE_IDLE,
    2,
    "com.amazon.tv.launcher",
    None,
    "hmdi_arc",
    False,
    22,
    None,
    None,
)
STATE_NONE = (None, None, None, None, None, None, None)

STATE_DETECTION_RULES1 = {"com.amazon.tv.launcher": ["off"]}
STATE_DETECTION_RULES2 = {"com.amazon.tv.launcher": ["media_session_state", "off"]}
STATE_DETECTION_RULES3 = {"com.amazon.tv.launcher": [{"idle": {"wake_lock_size": 2}}]}
STATE_DETECTION_RULES4 = {"com.amazon.tv.launcher": [{"idle": {"wake_lock_size": 1}}, "paused"]}
STATE_DETECTION_RULES5 = {"com.amazon.tv.launcher": ["audio_state"]}


class TestAndroidTVSyncPython(unittest.TestCase):
    PATCH_KEY = "python"
    ADB_ATTR = "_adb"

    def setUp(self):
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[
            self.PATCH_KEY
        ]:
            self.atv = AndroidTVSync("HOST", 5555)
            self.atv.adb_connect()

    def test_turn_on_off(self):
        """Test that the ``AndroidTVSync.turn_on`` and ``AndroidTVSync.turn_off`` methods work correctly."""
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[self.PATCH_KEY]:
            self.atv.turn_on()
            self.assertEqual(
                getattr(self.atv._adb, self.ADB_ATTR).shell_cmd,
                constants.CMD_SCREEN_ON + " || input keyevent {0}".format(constants.KEY_POWER),
            )

            self.atv.turn_off()
            self.assertEqual(
                getattr(self.atv._adb, self.ADB_ATTR).shell_cmd,
                constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_POWER),
            )

    def test_start_intent(self):
        """Test that the ``start_intent`` method works correctly."""
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[self.PATCH_KEY]:
            self.atv.start_intent("TEST")
            self.assertEqual(
                getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "am start -a android.intent.action.VIEW -d TEST"
            )

    def test_launch_app_stop_app(self):
        """Test that the ``AndroidTVSync.launch_app`` and ``AndroidTVSync.stop_app`` methods work correctly."""
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(None)[self.PATCH_KEY]:
            self.atv.launch_app("TEST")
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_LAUNCH_APP.format("TEST"))

            self.atv.stop_app("TEST")
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "am force-stop TEST")

    def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            running_apps = self.atv.running_apps()
            self.assertIsNone(running_apps, None)

        with patchers.patch_shell("")[self.PATCH_KEY]:
            running_apps = self.atv.running_apps()
            self.assertIsNone(running_apps, None)

        with patchers.patch_shell(RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            running_apps = self.atv.running_apps()
            self.assertListEqual(running_apps, RUNNING_APPS_LIST)

    def test_stream_music_properties(self):
        """Check that the ``stream_music_properties`` method works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertTupleEqual(self.atv.stream_music_properties(), (None, None, None, None))
            self.assertIsNone(self.atv.audio_output_device())
            self.assertIsNone(self.atv.is_volume_muted())
            self.assertIsNone(self.atv.volume())
            self.assertIsNone(self.atv.volume_level())

        with patchers.patch_shell("")[self.PATCH_KEY]:
            self.assertTupleEqual(self.atv.stream_music_properties(), (None, None, None, None))
            self.assertIsNone(self.atv.audio_output_device())
            self.assertIsNone(self.atv.is_volume_muted())
            self.assertIsNone(self.atv.volume())
            self.assertIsNone(self.atv.volume_level())

        with patchers.patch_shell(" ")[self.PATCH_KEY]:
            self.assertTupleEqual(self.atv.stream_music_properties(), (None, None, None, None))
            self.assertIsNone(self.atv.audio_output_device())
            self.assertIsNone(self.atv.is_volume_muted())
            self.assertIsNone(self.atv.volume())
            self.assertIsNone(self.atv.volume_level())

        with patchers.patch_shell(STREAM_MUSIC_EMPTY)[self.PATCH_KEY]:
            self.assertTupleEqual(self.atv.stream_music_properties(), (None, None, None, None))
            self.assertIsNone(self.atv.audio_output_device())
            self.assertIsNone(self.atv.is_volume_muted())
            self.assertIsNone(self.atv.volume())
            self.assertIsNone(self.atv.volume_level())

        with patchers.patch_shell(STREAM_MUSIC_NO_VOLUME)[self.PATCH_KEY]:
            self.assertTupleEqual(self.atv.stream_music_properties(), ("speaker", False, None, None))
            self.assertEqual("speaker", self.atv.audio_output_device())
            self.assertFalse(self.atv.is_volume_muted())
            self.assertIsNone(self.atv.volume())
            self.assertIsNone(self.atv.volume_level())

        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            self.assertTupleEqual(self.atv.stream_music_properties(), ("speaker", False, 20, 20 / 60.0))
            self.assertEqual("speaker", self.atv.audio_output_device())
            self.assertFalse(self.atv.is_volume_muted())
            self.assertEqual(self.atv.volume(), 20)
            self.assertEqual(self.atv.max_volume, 60.0)

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            self.assertTupleEqual(self.atv.stream_music_properties(), ("hmdi_arc", False, 22, 22 / 60.0))
            self.assertEqual("hmdi_arc", self.atv.audio_output_device())
            self.assertFalse(self.atv.is_volume_muted())
            self.assertEqual(self.atv.volume(), 22)
            self.assertEqual(self.atv.max_volume, 60.0)

    def test_set_volume_level(self):
        """Check that the ``set_volume_level`` method works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5)
            self.assertIsNone(new_volume_level)

        with patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5)
            self.assertIsNone(new_volume_level)

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(0.5)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 30")

        with patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(30.0 / 60)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 30")

        with patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = self.atv.set_volume_level(22.0 / 60)
            self.assertEqual(new_volume_level, 22.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 22")

    def test_volume_up(self):
        """Check that the ``volume_up`` method works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertEqual(new_volume_level, 23.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = self.atv.volume_up(23.0 / 60)
            self.assertEqual(new_volume_level, 24.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_up()
            self.assertEqual(new_volume_level, 21.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = self.atv.volume_up(21.0 / 60)
            self.assertEqual(new_volume_level, 22.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

    def test_volume_down(self):
        """Check that the ``volume_down`` method works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertEqual(new_volume_level, 21.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = self.atv.volume_down(21.0 / 60)
            self.assertEqual(new_volume_level, 20.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            new_volume_level = self.atv.volume_down()
            self.assertEqual(new_volume_level, 19.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = self.atv.volume_down(19.0 / 60)
            self.assertEqual(new_volume_level, 18.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

    def test_get_properties(self):
        """Check that ``get_properties()`` works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            with patchers.patch_calls(
                self.atv, self.atv.screen_on_awake_wake_lock_size
            ) as screen_on_awake_wake_lock_size, patchers.patch_calls(
                self.atv, self.atv.current_app_media_session_state
            ) as current_app_media_session_state, patchers.patch_calls(
                self.atv, self.atv.stream_music_properties
            ) as stream_music_properties, patchers.patch_calls(
                self.atv, self.atv.running_apps
            ) as running_apps, patchers.patch_calls(
                self.atv, self.atv.get_hdmi_input
            ) as get_hdmi_input:
                self.atv.get_properties(lazy=True)
                assert screen_on_awake_wake_lock_size.called
                assert not current_app_media_session_state.called
                assert not running_apps.called
                assert not get_hdmi_input.called

            with patchers.patch_calls(
                self.atv, self.atv.screen_on_awake_wake_lock_size
            ) as screen_on_awake_wake_lock_size, patchers.patch_calls(
                self.atv, self.atv.current_app_media_session_state
            ) as current_app_media_session_state, patchers.patch_calls(
                self.atv, self.atv.stream_music_properties
            ) as stream_music_properties, patchers.patch_calls(
                self.atv, self.atv.running_apps
            ) as running_apps, patchers.patch_calls(
                self.atv, self.atv.get_hdmi_input
            ) as get_hdmi_input:
                self.atv.get_properties(lazy=False, get_running_apps=True)
                assert screen_on_awake_wake_lock_size.called
                assert current_app_media_session_state.called
                assert running_apps.called
                assert get_hdmi_input.called

            with patchers.patch_calls(
                self.atv, self.atv.screen_on_awake_wake_lock_size
            ) as screen_on_awake_wake_lock_size, patchers.patch_calls(
                self.atv, self.atv.current_app_media_session_state
            ) as current_app_media_session_state, patchers.patch_calls(
                self.atv, self.atv.stream_music_properties
            ) as stream_music_properties, patchers.patch_calls(
                self.atv, self.atv.running_apps
            ) as running_apps, patchers.patch_calls(
                self.atv, self.atv.get_hdmi_input
            ) as get_hdmi_input:
                self.atv.get_properties(lazy=False, get_running_apps=False)
                assert screen_on_awake_wake_lock_size.called
                assert current_app_media_session_state.called
                assert not running_apps.called
                assert get_hdmi_input.called

    def test_get_properties_dict(self):
        """Check that ``get_properties_dict()`` works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            with patchers.patch_calls(self.atv, self.atv.get_properties) as get_properties:
                self.atv.get_properties_dict()
                assert get_properties.called

    def test_update(self):
        """Check that the ``update`` method works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            with patchers.patch_calls(self.atv, self.atv._update) as patched:
                self.atv.update()
                assert patched.called

    def test_update2(self):
        """Check that the ``update`` method works correctly."""
        with patchers.patch_connect(False)[self.PATCH_KEY]:
            self.atv.adb_connect()
        state = self.atv.update()
        self.assertTupleEqual(state, STATE_NONE)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.atv.adb_connect()

        with patchers.patch_shell(None)[self.PATCH_KEY]:
            state = self.atv.update()
            self.assertTupleEqual(state, STATE_NONE)

        with patch(
            "androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties", return_value=GET_PROPERTIES_OUTPUT
        ):
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

    def assertUpdate(self, get_properties, update):
        """Check that the results of the `update` method are as expected."""
        with patch("androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties", return_value=get_properties):
            self.assertTupleEqual(self.atv.update(), update)

    def test_state_detection(self):
        """Check that the state detection works as expected."""
        self.atv.max_volume = 60.0
        self.assertUpdate(
            [False, False, None, -1, None, None, None, None, None, None, None],
            (constants.STATE_OFF, None, None, None, None, None, None),
        )

        self.assertUpdate(
            [True, False, None, -1, None, None, None, None, None, None, None],
            (constants.STATE_STANDBY, None, None, None, None, None, None),
        )

        # ATV Launcher
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_ATV_LAUNCHER, 3, "hmdi_arc", False, 30, None, None],
            (
                constants.STATE_IDLE,
                constants.APP_ATV_LAUNCHER,
                [constants.APP_ATV_LAUNCHER],
                "hmdi_arc",
                False,
                0.5,
                None,
            ),
        )

        # ATV Launcher with custom state detection
        self.atv._state_detection_rules = {constants.APP_ATV_LAUNCHER: [{"idle": {"audio_state": "idle"}}]}
        self.assertUpdate(
            [True, True, constants.STATE_PAUSED, 2, constants.APP_ATV_LAUNCHER, 3, "hmdi_arc", False, 30, None, None],
            (
                constants.STATE_IDLE,
                constants.APP_ATV_LAUNCHER,
                [constants.APP_ATV_LAUNCHER],
                "hmdi_arc",
                False,
                0.5,
                None,
            ),
        )

        self.atv._state_detection_rules = {constants.APP_ATV_LAUNCHER: [{"idle": {"INVALID": "idle"}}]}
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_ATV_LAUNCHER, 3, "hmdi_arc", False, 30, None, None],
            (
                constants.STATE_IDLE,
                constants.APP_ATV_LAUNCHER,
                [constants.APP_ATV_LAUNCHER],
                "hmdi_arc",
                False,
                0.5,
                None,
            ),
        )

        self.atv._state_detection_rules = None

        # Bell Fibe
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_BELL_FIBE, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, constants.APP_BELL_FIBE, [constants.APP_BELL_FIBE], "hmdi_arc", False, 0.5, None),
        )

        # Netflix
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_NETFLIX, 2, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, constants.APP_NETFLIX, [constants.APP_NETFLIX], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_NETFLIX, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_NETFLIX, [constants.APP_NETFLIX], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_NETFLIX, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, constants.APP_NETFLIX, [constants.APP_NETFLIX], "hmdi_arc", False, 0.5, None),
        )

        # NLZIET
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 1, constants.APP_NLZIET, 2, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, constants.APP_NLZIET, [constants.APP_NLZIET], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_NLZIET, 2, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_NLZIET, [constants.APP_NLZIET], "hmdi_arc", False, 0.5, None),
        )

        # Plex
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_PLEX, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, constants.APP_PLEX, [constants.APP_PLEX], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 3, constants.APP_PLEX, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 4, constants.APP_PLEX, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 5, constants.APP_PLEX, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 7, constants.APP_PLEX, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 1, constants.APP_PLEX, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, constants.APP_PLEX, [constants.APP_PLEX], "hmdi_arc", False, 0.5, None),
        )

        # TVheadend
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 5, constants.APP_TVHEADEND, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, constants.APP_TVHEADEND, [constants.APP_TVHEADEND], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 6, constants.APP_TVHEADEND, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_TVHEADEND, [constants.APP_TVHEADEND], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 1, constants.APP_TVHEADEND, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, constants.APP_TVHEADEND, [constants.APP_TVHEADEND], "hmdi_arc", False, 0.5, None),
        )

        # VLC
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 6, constants.APP_VLC, 2, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, constants.APP_VLC, [constants.APP_VLC], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 6, constants.APP_VLC, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_VLC, [constants.APP_VLC], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 6, constants.APP_VLC, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, constants.APP_VLC, [constants.APP_VLC], "hmdi_arc", False, 0.5, None),
        )

        # VRV
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_VRV, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, constants.APP_VRV, [constants.APP_VRV], "hmdi_arc", False, 0.5, None),
        )

        # YouTube
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_YOUTUBE, 2, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, constants.APP_YOUTUBE, [constants.APP_YOUTUBE], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_YOUTUBE, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, constants.APP_YOUTUBE, [constants.APP_YOUTUBE], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, constants.APP_YOUTUBE, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, constants.APP_YOUTUBE, [constants.APP_YOUTUBE], "hmdi_arc", False, 0.5, None),
        )

        # Unknown app
        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, UNKNOWN_APP, 2, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, UNKNOWN_APP, [UNKNOWN_APP], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, UNKNOWN_APP, 3, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, UNKNOWN_APP, [UNKNOWN_APP], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, UNKNOWN_APP, 4, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, UNKNOWN_APP, [UNKNOWN_APP], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_PLAYING, 2, UNKNOWN_APP, None, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, UNKNOWN_APP, [UNKNOWN_APP], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 1, UNKNOWN_APP, None, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PAUSED, UNKNOWN_APP, [UNKNOWN_APP], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 2, UNKNOWN_APP, None, "hmdi_arc", False, 30, None, None],
            (constants.STATE_PLAYING, UNKNOWN_APP, [UNKNOWN_APP], "hmdi_arc", False, 0.5, None),
        )

        self.assertUpdate(
            [True, True, constants.STATE_IDLE, 3, UNKNOWN_APP, None, "hmdi_arc", False, 30, None, None],
            (constants.STATE_IDLE, UNKNOWN_APP, [UNKNOWN_APP], "hmdi_arc", False, 0.5, None),
        )

    def test_customize_command(self):
        self.atv.customize_command(constants.CUSTOM_CURRENT_APP, "1")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.current_app()
            patched.assert_called_with("1")

        self.atv.customize_command(constants.CUSTOM_CURRENT_APP_MEDIA_SESSION_STATE, "2")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.current_app_media_session_state()
            patched.assert_called_with("2")

        self.atv.customize_command(constants.CUSTOM_LAUNCH_APP, "this is a {}")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.launch_app("test")
            patched.assert_called_with("this is a test")

        self.atv.customize_command(constants.CUSTOM_RUNNING_APPS, "3")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.running_apps()
            patched.assert_called_with("3")

        self.atv.customize_command(constants.CUSTOM_TURN_OFF, "4")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.turn_off()
            patched.assert_called_with("4")

        self.atv.customize_command(constants.CUSTOM_TURN_ON, "5")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.turn_on()
            patched.assert_called_with("5")

        self.atv.customize_command(constants.CUSTOM_AUDIO_STATE, "6")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.audio_state()
            patched.assert_called_with("6")

        self.atv.customize_command(constants.CUSTOM_HDMI_INPUT, "7")
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.get_hdmi_input()
            patched.assert_called_with("7")

        # Delete a custom command
        self.atv.customize_command(constants.CUSTOM_TURN_ON, None)
        with patch.object(self.atv._adb, "shell") as patched:
            self.atv.turn_on()
            patched.assert_called_with(constants.CMD_TURN_ON_ANDROIDTV)


class TestAndroidTVSyncServer(TestAndroidTVSyncPython):
    PATCH_KEY = "server"
    ADB_ATTR = "_adb_device"

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[self.PATCH_KEY]:
            self.atv = AndroidTVSync("HOST", 5555, adb_server_ip="ADB_SERVER_IP")
            self.atv.adb_connect()


class TestStateDetectionRulesValidator(unittest.TestCase):
    def test_state_detection_rules_validator(self):
        """Check that the ``state_detection_rules_validator`` function works correctly."""
        with patchers.patch_connect(True)["python"], patchers.patch_shell("")["python"]:
            # Make sure that no error is raised when the state detection rules are valid
            AndroidTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES1)
            AndroidTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES2)
            AndroidTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES3)
            AndroidTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES4)
            AndroidTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES5)


if __name__ == "__main__":
    unittest.main()
