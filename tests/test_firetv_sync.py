import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, "..")

from androidtv import constants, ha_state_detection_rules_validator
from androidtv.firetv.firetv_sync import FireTVSync
from . import patchers


HDMI_INPUT_EMPTY = "\n"

CURRENT_APP_OUTPUT = "com.amazon.tv.launcher"

RUNNING_APPS_OUTPUT = """u0_a18    316   197   1189204 115000 ffffffff 00000000 S com.netflix.ninja
u0_a2     15121 197   998628 24628 ffffffff 00000000 S com.amazon.device.controllermanager"""

RUNNING_APPS_LIST = ["com.netflix.ninja", "com.amazon.device.controllermanager"]

GET_PROPERTIES_OUTPUT1 = ""
GET_PROPERTIES_DICT1 = {
    "screen_on": False,
    "awake": False,
    "wake_lock_size": -1,
    "current_app": None,
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": None,
}
STATE1 = (constants.STATE_OFF, None, None, None)

GET_PROPERTIES_OUTPUT2 = "1"
GET_PROPERTIES_DICT2 = {
    "screen_on": True,
    "awake": False,
    "wake_lock_size": -1,
    "current_app": None,
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": None,
}
STATE2 = (constants.STATE_STANDBY, None, None, None)

GET_PROPERTIES_OUTPUT3 = """11Wake Locks: size=2
com.amazon.tv.launcher


u0_a2     17243 197   998628 24932 ffffffff 00000000 S com.amazon.device.controllermanager
u0_a2     17374 197   995368 20764 ffffffff 00000000 S com.amazon.device.controllermanager:BluetoothReceiver"""
GET_PROPERTIES_DICT3 = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": 2,
    "current_app": "com.amazon.tv.launcher",
    "media_session_state": None,
    "running_apps": ["com.amazon.device.controllermanager", "com.amazon.device.controllermanager:BluetoothReceiver"],
    "hdmi_input": None,
}
STATE3 = (
    constants.STATE_IDLE,
    "com.amazon.tv.launcher",
    ["com.amazon.device.controllermanager", "com.amazon.device.controllermanager:BluetoothReceiver"],
    None,
)

GET_PROPERTIES_OUTPUT3A = GET_PROPERTIES_OUTPUT3[0]
GET_PROPERTIES_OUTPUT3B = GET_PROPERTIES_OUTPUT3[:2]
GET_PROPERTIES_OUTPUT3C = GET_PROPERTIES_OUTPUT3.splitlines()[0]
GET_PROPERTIES_OUTPUT3D = "\n".join(GET_PROPERTIES_OUTPUT3.splitlines()[:2])
GET_PROPERTIES_OUTPUT3E = "\n".join(GET_PROPERTIES_OUTPUT3.splitlines()[:3])
GET_PROPERTIES_OUTPUT3F = "\n".join(GET_PROPERTIES_OUTPUT3.splitlines()[:4]) + "HW2"

GET_PROPERTIES_DICT3A = {
    "screen_on": True,
    "awake": False,
    "wake_lock_size": -1,
    "current_app": None,
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": None,
}
GET_PROPERTIES_DICT3B = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": -1,
    "current_app": None,
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": None,
}
GET_PROPERTIES_DICT3C = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": 2,
    "current_app": None,
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": None,
}
GET_PROPERTIES_DICT3D = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": 2,
    "current_app": "com.amazon.tv.launcher",
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": None,
}
GET_PROPERTIES_DICT3E = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": 2,
    "current_app": "com.amazon.tv.launcher",
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": None,
}
GET_PROPERTIES_DICT3F = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": 2,
    "current_app": "com.amazon.tv.launcher",
    "media_session_state": None,
    "running_apps": None,
    "hdmi_input": "HW2",
}

GET_PROPERTIES_OUTPUT4 = """11Wake Locks: size=2
com.amazon.tv.launcher
state=PlaybackState {state=2, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}"""
GET_PROPERTIES_DICT4 = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": 2,
    "current_app": "com.amazon.tv.launcher",
    "media_session_state": 2,
    "running_apps": None,
    "hdmi_input": None,
}

GET_PROPERTIES_OUTPUT5 = """11Wake Locks: size=2
com.amazon.tv.launcher
state=PlaybackState {state=2, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}

u0_a2     17243 197   998628 24932 ffffffff 00000000 S com.amazon.device.controllermanager
u0_a2     17374 197   995368 20764 ffffffff 00000000 S com.amazon.device.controllermanager:BluetoothReceiver"""
GET_PROPERTIES_DICT5 = {
    "screen_on": True,
    "awake": True,
    "wake_lock_size": 2,
    "current_app": "com.amazon.tv.launcher",
    "media_session_state": 2,
    "running_apps": ["com.amazon.device.controllermanager", "com.amazon.device.controllermanager:BluetoothReceiver"],
    "hdmi_input": None,
}

GET_PROPERTIES_DICT_NONE = {
    "screen_on": None,
    "awake": None,
    "wake_lock_size": None,
    "media_session_state": None,
    "current_app": None,
    "running_apps": None,
    "hdmi_input": None,
}
STATE_NONE = (None, None, None, None)

STATE_DETECTION_RULES1 = {"com.amazon.tv.launcher": ["off"]}
STATE_DETECTION_RULES2 = {"com.amazon.tv.launcher": ["media_session_state", "off"]}
STATE_DETECTION_RULES3 = {"com.amazon.tv.launcher": [{"standby": {"wake_lock_size": 2}}]}
STATE_DETECTION_RULES4 = {"com.amazon.tv.launcher": [{"standby": {"wake_lock_size": 1}}, "paused"]}
STATE_DETECTION_RULES5 = {"com.amazon.tv.launcher": ["audio_state"]}


class TestFireTVSyncPython(unittest.TestCase):
    ADB_ATTR = "_adb"
    PATCH_KEY = "python"

    def setUp(self):
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[
            self.PATCH_KEY
        ]:
            self.ftv = FireTVSync("HOST", 5555)
            self.ftv.adb_connect()

    def test_turn_on_off(self):
        """Test that the ``FireTVSync.turn_on`` and ``FireTVSync.turn_off`` methods work correctly."""
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[self.PATCH_KEY]:
            self.ftv.turn_on()
            self.assertEqual(
                getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd,
                constants.CMD_SCREEN_ON
                + " || (input keyevent {0} && input keyevent {1})".format(constants.KEY_POWER, constants.KEY_HOME),
            )

            self.ftv.turn_off()
            self.assertEqual(
                getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd,
                constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_SLEEP),
            )

    def test_send_intent(self):
        """Test that the ``_send_intent`` method works correctly."""
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("output\r\nretcode")[self.PATCH_KEY]:
            result = self.ftv._send_intent("TEST", constants.INTENT_LAUNCH)
            self.assertEqual(
                getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd,
                "monkey -p TEST -c android.intent.category.LAUNCHER 1; echo $?",
            )
            self.assertDictEqual(result, {"output": "output", "retcode": "retcode"})

        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(None)[self.PATCH_KEY]:
            result = self.ftv._send_intent("TEST", constants.INTENT_LAUNCH)
            self.assertEqual(
                getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd,
                "monkey -p TEST -c android.intent.category.LAUNCHER 1; echo $?",
            )
            self.assertDictEqual(result, {})

    def test_launch_app_stop_app(self):
        """Test that the ``FireTVSync.launch_app`` and ``FireTVSync.stop_app`` methods work correctly."""
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(None)[self.PATCH_KEY]:
            self.ftv.launch_app("TEST")
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_LAUNCH_APP.format("TEST"))

            self.ftv.stop_app("TEST")
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, "am force-stop TEST")

    def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            running_apps = self.ftv.running_apps()
            self.assertIsNone(running_apps, None)

        with patchers.patch_shell("")[self.PATCH_KEY]:
            running_apps = self.ftv.running_apps()
            self.assertIsNone(running_apps, None)

        with patchers.patch_shell(RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            running_apps = self.ftv.running_apps()
            self.assertListEqual(running_apps, RUNNING_APPS_LIST)

    def test_get_properties(self):
        """Check that ``get_properties()`` works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            with patchers.patch_calls(
                self.ftv, self.ftv.screen_on_awake_wake_lock_size
            ) as screen_on_awake_wake_lock_size, patchers.patch_calls(
                self.ftv, self.ftv.current_app_media_session_state
            ) as current_app_media_session_state, patchers.patch_calls(
                self.ftv, self.ftv.running_apps
            ) as running_apps, patchers.patch_calls(
                self.ftv, self.ftv.get_hdmi_input
            ) as get_hdmi_input:
                self.ftv.get_properties(lazy=True)
                assert screen_on_awake_wake_lock_size.called
                assert not current_app_media_session_state.called
                assert not running_apps.called
                assert not get_hdmi_input.called

            with patchers.patch_calls(
                self.ftv, self.ftv.screen_on_awake_wake_lock_size
            ) as screen_on_awake_wake_lock_size, patchers.patch_calls(
                self.ftv, self.ftv.current_app_media_session_state
            ) as current_app_media_session_state, patchers.patch_calls(
                self.ftv, self.ftv.running_apps
            ) as running_apps, patchers.patch_calls(
                self.ftv, self.ftv.get_hdmi_input
            ) as get_hdmi_input:
                self.ftv.get_properties(lazy=False, get_running_apps=True)
                assert screen_on_awake_wake_lock_size.called
                assert current_app_media_session_state.called
                assert running_apps.called
                assert get_hdmi_input.called

            with patchers.patch_calls(
                self.ftv, self.ftv.screen_on_awake_wake_lock_size
            ) as screen_on_awake_wake_lock_size, patchers.patch_calls(
                self.ftv, self.ftv.current_app_media_session_state
            ) as current_app_media_session_state, patchers.patch_calls(
                self.ftv, self.ftv.running_apps
            ) as running_apps, patchers.patch_calls(
                self.ftv, self.ftv.get_hdmi_input
            ) as get_hdmi_input:
                self.ftv.get_properties(lazy=False, get_running_apps=False)
                assert screen_on_awake_wake_lock_size.called
                assert current_app_media_session_state.called
                assert not running_apps.called
                assert get_hdmi_input.called

    def test_get_properties_dict(self):
        """Check that ``get_properties_dict()`` works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            with patchers.patch_calls(self.ftv, self.ftv.get_properties) as get_properties:
                self.ftv.get_properties_dict()
                assert get_properties.called

    def test_update(self):
        """Check that the ``update`` method works correctly."""
        with patchers.patch_connect(False)[self.PATCH_KEY]:
            self.ftv.adb_connect()

        self.assertTupleEqual(self.ftv.update(), STATE_NONE)

    def assertUpdate(self, get_properties, update):
        """Check that the results of the `update` method are as expected."""
        with patch("androidtv.firetv.firetv_sync.FireTVSync.get_properties", return_value=get_properties):
            self.assertTupleEqual(self.ftv.update(), update)

    def test_state_detection(self):
        """Check that the state detection works as expected."""
        self.assertUpdate([False, None, -1, None, None, None, None], (constants.STATE_OFF, None, None, None))

        self.assertUpdate([True, False, -1, None, None, None, None], (constants.STATE_STANDBY, None, None, None))

        self.assertUpdate(
            [True, True, 1, "com.amazon.tv.launcher", None, None, None],
            (constants.STATE_IDLE, "com.amazon.tv.launcher", ["com.amazon.tv.launcher"], None),
        )

        # Amazon Video
        self.assertUpdate(
            [True, True, 1, constants.APP_AMAZON_VIDEO, 3, [constants.APP_AMAZON_VIDEO], None],
            (constants.STATE_PLAYING, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_AMAZON_VIDEO, 2, [constants.APP_AMAZON_VIDEO], None],
            (constants.STATE_PAUSED, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_AMAZON_VIDEO, 1, [constants.APP_AMAZON_VIDEO], None],
            (constants.STATE_IDLE, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO], None),
        )

        # Amazon Video with custom state detection rules
        self.ftv._state_detection_rules = {constants.APP_AMAZON_VIDEO: ["media_session_state"]}

        self.assertUpdate(
            [True, True, 2, constants.APP_AMAZON_VIDEO, 2, [constants.APP_AMAZON_VIDEO], None],
            (constants.STATE_PAUSED, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO], None),
        )

        self.assertUpdate(
            [True, True, 5, constants.APP_AMAZON_VIDEO, 3, [constants.APP_AMAZON_VIDEO], None],
            (constants.STATE_PLAYING, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO], None),
        )

        self.assertUpdate(
            [True, True, 5, constants.APP_AMAZON_VIDEO, 1, [constants.APP_AMAZON_VIDEO], None],
            (constants.STATE_IDLE, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO], None),
        )

        self.ftv._state_detection_rules = {constants.APP_AMAZON_VIDEO: [{"standby": {"media_session_state": 2}}]}
        self.assertUpdate(
            [True, True, 2, constants.APP_AMAZON_VIDEO, None, [constants.APP_AMAZON_VIDEO], None],
            (constants.STATE_IDLE, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO], None),
        )

        # Firefox
        self.assertUpdate(
            [True, True, 3, constants.APP_FIREFOX, 3, [constants.APP_FIREFOX], None],
            (constants.STATE_PLAYING, constants.APP_FIREFOX, [constants.APP_FIREFOX], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_FIREFOX, 3, [constants.APP_FIREFOX], None],
            (constants.STATE_IDLE, constants.APP_FIREFOX, [constants.APP_FIREFOX], None),
        )

        # Hulu
        self.assertUpdate(
            [True, True, 4, constants.APP_HULU, 3, [constants.APP_HULU], None],
            (constants.STATE_PLAYING, constants.APP_HULU, [constants.APP_HULU], None),
        )

        self.assertUpdate(
            [True, True, 2, constants.APP_HULU, 3, [constants.APP_HULU], None],
            (constants.STATE_PAUSED, constants.APP_HULU, [constants.APP_HULU], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_HULU, 3, [constants.APP_HULU], None],
            (constants.STATE_IDLE, constants.APP_HULU, [constants.APP_HULU], None),
        )

        # Jellyfin
        self.assertUpdate(
            [True, True, 2, constants.APP_JELLYFIN_TV, 3, [constants.APP_JELLYFIN_TV], None],
            (constants.STATE_PLAYING, constants.APP_JELLYFIN_TV, [constants.APP_JELLYFIN_TV], None),
        )

        self.assertUpdate(
            [True, True, 4, constants.APP_JELLYFIN_TV, 3, [constants.APP_JELLYFIN_TV], None],
            (constants.STATE_PAUSED, constants.APP_JELLYFIN_TV, [constants.APP_JELLYFIN_TV], None),
        )

        # Netfilx
        self.assertUpdate(
            [True, True, 1, constants.APP_NETFLIX, 3, [constants.APP_NETFLIX], None],
            (constants.STATE_PLAYING, constants.APP_NETFLIX, [constants.APP_NETFLIX], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_NETFLIX, 2, [constants.APP_NETFLIX], None],
            (constants.STATE_PAUSED, constants.APP_NETFLIX, [constants.APP_NETFLIX], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_NETFLIX, 1, [constants.APP_NETFLIX], None],
            (constants.STATE_IDLE, constants.APP_NETFLIX, [constants.APP_NETFLIX], None),
        )

        # Plex
        self.assertUpdate(
            [True, True, 1, constants.APP_PLEX, 3, [constants.APP_PLEX], None],
            (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX], None),
        )

        self.assertUpdate(
            [True, True, 2, constants.APP_PLEX, 3, [constants.APP_PLEX], None],
            (constants.STATE_PAUSED, constants.APP_PLEX, [constants.APP_PLEX], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_PLEX, 1, [constants.APP_PLEX], None],
            (constants.STATE_IDLE, constants.APP_PLEX, [constants.APP_PLEX], None),
        )

        # Sport 1
        self.assertUpdate(
            [True, True, 3, constants.APP_SPORT1, 3, [constants.APP_SPORT1], None],
            (constants.STATE_PLAYING, constants.APP_SPORT1, [constants.APP_SPORT1], None),
        )

        self.assertUpdate(
            [True, True, 2, constants.APP_SPORT1, 3, [constants.APP_SPORT1], None],
            (constants.STATE_PAUSED, constants.APP_SPORT1, [constants.APP_SPORT1], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_SPORT1, 3, [constants.APP_SPORT1], None],
            (constants.STATE_IDLE, constants.APP_SPORT1, [constants.APP_SPORT1], None),
        )

        # Spotify
        self.assertUpdate(
            [True, True, 1, constants.APP_SPOTIFY, 3, [constants.APP_SPOTIFY], None],
            (constants.STATE_PLAYING, constants.APP_SPOTIFY, [constants.APP_SPOTIFY], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_SPOTIFY, 2, [constants.APP_SPOTIFY], None],
            (constants.STATE_PAUSED, constants.APP_SPOTIFY, [constants.APP_SPOTIFY], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_SPOTIFY, 1, [constants.APP_SPOTIFY], None],
            (constants.STATE_IDLE, constants.APP_SPOTIFY, [constants.APP_SPOTIFY], None),
        )

        # Twitch
        self.assertUpdate(
            [True, True, 2, constants.APP_TWITCH_FIRETV, 3, [constants.APP_TWITCH_FIRETV], None],
            (constants.STATE_PAUSED, constants.APP_TWITCH_FIRETV, [constants.APP_TWITCH_FIRETV], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_TWITCH_FIRETV, 3, [constants.APP_TWITCH_FIRETV], None],
            (constants.STATE_PLAYING, constants.APP_TWITCH_FIRETV, [constants.APP_TWITCH_FIRETV], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_TWITCH_FIRETV, 4, [constants.APP_TWITCH_FIRETV], None],
            (constants.STATE_PLAYING, constants.APP_TWITCH_FIRETV, [constants.APP_TWITCH_FIRETV], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_TWITCH_FIRETV, 1, [constants.APP_TWITCH_FIRETV], None],
            (constants.STATE_IDLE, constants.APP_TWITCH_FIRETV, [constants.APP_TWITCH_FIRETV], None),
        )

        # Waipu TV
        self.assertUpdate(
            [True, True, 3, constants.APP_WAIPU_TV, 1, [constants.APP_WAIPU_TV], None],
            (constants.STATE_PLAYING, constants.APP_WAIPU_TV, [constants.APP_WAIPU_TV], None),
        )

        self.assertUpdate(
            [True, True, 2, constants.APP_WAIPU_TV, 1, [constants.APP_WAIPU_TV], None],
            (constants.STATE_PAUSED, constants.APP_WAIPU_TV, [constants.APP_WAIPU_TV], None),
        )

        self.assertUpdate(
            [True, True, 1, constants.APP_WAIPU_TV, 1, [constants.APP_WAIPU_TV], None],
            (constants.STATE_IDLE, constants.APP_WAIPU_TV, [constants.APP_WAIPU_TV], None),
        )

        # Unknown app
        self.assertUpdate(
            [True, True, 1, "unknown", 3, ["unknown"], None], (constants.STATE_PLAYING, "unknown", ["unknown"], None)
        )

        self.assertUpdate(
            [True, True, 1, "unknown", 2, ["unknown"], None], (constants.STATE_PAUSED, "unknown", ["unknown"], None)
        )

        self.assertUpdate(
            [True, True, 1, "unknown", 1, ["unknown"], None], (constants.STATE_IDLE, "unknown", ["unknown"], None)
        )

        self.assertUpdate(
            [True, True, 1, "unknown", None, ["unknown"], None], (constants.STATE_PLAYING, "unknown", ["unknown"], None)
        )

        self.assertUpdate(
            [True, True, 2, "unknown", None, ["unknown"], None], (constants.STATE_PAUSED, "unknown", ["unknown"], None)
        )


class TestFireTVSyncServer(TestFireTVSyncPython):
    ADB_ATTR = "_adb_device"
    PATCH_KEY = "server"

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[self.PATCH_KEY]:
            self.ftv = FireTVSync("HOST", 5555, adb_server_ip="ADB_SERVER_PORT")
            self.ftv.adb_connect()


if __name__ == "__main__":
    unittest.main()
