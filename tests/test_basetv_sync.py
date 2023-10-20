import sys
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


sys.path.insert(0, "..")

from androidtv import constants, ha_state_detection_rules_validator
from androidtv.androidtv.androidtv_sync import AndroidTVSync
from androidtv.basetv.basetv_sync import BaseTVSync
from . import patchers


DEVICE_PROPERTIES_OUTPUT1 = """Amazon
AFTT
SERIALNO
5.1.1
"""

WIFIMAC_OUTPUT1 = "    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff"
ETHMAC_OUTPUT1 = 'Device "eth0" does not exist.'

DEVICE_PROPERTIES_DICT1 = {
    "manufacturer": "Amazon",
    "model": "AFTT",
    "serialno": "SERIALNO",
    "sw_version": "5.1.1",
    "wifimac": "ab:cd:ef:gh:ij:kl",
    "ethmac": None,
}

DEVICE_PROPERTIES_OUTPUT2 = """Amazon
AFTT

5.1.1
"""

DEVICE_PROPERTIES_DICT2 = {
    "manufacturer": "Amazon",
    "model": "AFTT",
    "serialno": None,
    "sw_version": "5.1.1",
    "wifimac": "ab:cd:ef:gh:ij:kl",
    "ethmac": None,
}

DEVICE_PROPERTIES_OUTPUT3 = """Not Amazon
AFTT
SERIALNO
5.1.1
"""

WIFIMAC_OUTPUT3 = 'Device "wlan0" does not exist.'
ETHMAC_OUTPUT3 = "    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff"

DEVICE_PROPERTIES_DICT3 = {
    "manufacturer": "Not Amazon",
    "model": "AFTT",
    "serialno": "SERIALNO",
    "sw_version": "5.1.1",
    "wifimac": None,
    "ethmac": "ab:cd:ef:gh:ij:kl",
}


# Source: https://community.home-assistant.io/t/new-chromecast-w-android-tv-integration-only-showing-as-off-or-idle/234424/15
DEVICE_PROPERTIES_GOOGLE_TV = """Google
Chromecast
SERIALNO
10
"""

WIFIMAC_GOOGLE = "    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff"
ETHMAC_GOOGLE = 'Device "eth0" does not exist.'

DEVICE_PROPERTIES_OUTPUT_SONY_TV = """Sony
BRAVIA 4K GB
SERIALNO
8.0.0
"""

WIFIMAC_SONY = "    link/ether 11:22:33:44:55:66 brd ff:ff:ff:ff:ff:ff"
ETHMAC_SONY = "    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff"

DEVICE_PROPERTIES_DICT_SONY_TV = {
    "manufacturer": "Sony",
    "model": "BRAVIA 4K GB",
    "serialno": "SERIALNO",
    "sw_version": "8.0.0",
    "wifimac": "11:22:33:44:55:66",
    "ethmac": "ab:cd:ef:gh:ij:kl",
}

DEVICE_PROPERTIES_OUTPUT_SHIELD_TV_11 = """NVIDIA
SHIELD Android TV
0123456789012
11
"""

WIFIMAC_SHIELD_TV_11 = "    link/ether 11:22:33:44:55:66 brd ff:ff:ff:ff:ff:ff"
ETHMAC_SHIELD_TV_11 = "    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff"

DEVICE_PROPERTIES_OUTPUT_SHIELD_TV_12 = """NVIDIA
SHIELD Android TV
0123456789012
12
"""

WIFIMAC_SHIELD_TV_12 = "    link/ether 11:22:33:44:55:66 brd ff:ff:ff:ff:ff:ff"
ETHMAC_SHIELD_TV_12 = "    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff"

DEVICE_PROPERTIES_OUTPUT_SHIELD_TV_13 = """NVIDIA
SHIELD Android TV
0123456789012
13
"""

WIFIMAC_SHIELD_TV_13 = "    link/ether 11:22:33:44:55:66 brd ff:ff:ff:ff:ff:ff"
ETHMAC_SHIELD_TV_13 = "    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff"

DEVICE_PROPERTIES_DICT_SHIELD_TV_11 = {
    "manufacturer": "NVIDIA",
    "model": "SHIELD Android TV",
    "serialno": "0123456789012",
    "sw_version": "11",
    "wifimac": "11:22:33:44:55:66",
    "ethmac": "ab:cd:ef:gh:ij:kl",
}

DEVICE_PROPERTIES_DICT_SHIELD_TV_12 = {
    "manufacturer": "NVIDIA",
    "model": "SHIELD Android TV",
    "serialno": "0123456789012",
    "sw_version": "12",
    "wifimac": "11:22:33:44:55:66",
    "ethmac": "ab:cd:ef:gh:ij:kl",
}

DEVICE_PROPERTIES_DICT_SHIELD_TV_13 = {
    "manufacturer": "NVIDIA",
    "model": "SHIELD Android TV",
    "serialno": "0123456789012",
    "sw_version": "13",
    "wifimac": "11:22:33:44:55:66",
    "ethmac": "ab:cd:ef:gh:ij:kl",
}

INSTALLED_APPS_OUTPUT_1 = """package:org.example.app
package:org.example.launcher
"""

INSTALLED_APPS_LIST = ["org.example.app", "org.example.launcher"]

MEDIA_SESSION_STATE_OUTPUT = "com.amazon.tv.launcher\nstate=PlaybackState {state=2, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}"

STATE_DETECTION_RULES1 = {"com.amazon.tv.launcher": ["off"]}
STATE_DETECTION_RULES2 = {"com.amazon.tv.launcher": ["media_session_state", "off"]}
STATE_DETECTION_RULES3 = {"com.amazon.tv.launcher": [{"standby": {"wake_lock_size": 2}}]}
STATE_DETECTION_RULES4 = {"com.amazon.tv.launcher": [{"standby": {"wake_lock_size": 1}}, "paused"]}
STATE_DETECTION_RULES5 = {"com.amazon.tv.launcher": ["audio_state"]}

STATE_DETECTION_RULES_INVALID1 = {123: ["media_session_state"]}
STATE_DETECTION_RULES_INVALID2 = {"com.amazon.tv.launcher": [123]}
STATE_DETECTION_RULES_INVALID3 = {"com.amazon.tv.launcher": ["INVALID"]}
STATE_DETECTION_RULES_INVALID4 = {"com.amazon.tv.launcher": [{"INVALID": {"wake_lock_size": 2}}]}
STATE_DETECTION_RULES_INVALID5 = {"com.amazon.tv.launcher": [{"standby": "INVALID"}]}
STATE_DETECTION_RULES_INVALID6 = {"com.amazon.tv.launcher": [{"standby": {"INVALID": 2}}]}
STATE_DETECTION_RULES_INVALID7 = {"com.amazon.tv.launcher": [{"standby": {"wake_lock_size": "INVALID"}}]}
STATE_DETECTION_RULES_INVALID8 = {"com.amazon.tv.launcher": [{"standby": {"media_session_state": "INVALID"}}]}
STATE_DETECTION_RULES_INVALID9 = {"com.amazon.tv.launcher": [{"standby": {"audio_state": 123}}]}
STATE_DETECTION_RULES_INVALID10 = {"com.amazon.tv.launcher": [{"standby": {"media_session_state": "INVALID"}}]}
STATE_DETECTION_RULES_INVALID11 = {"com.amazon.tv.launcher": [{"standby": {"audio_state": 123}}]}

PNG_IMAGE = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0fa\x00\x00\x0fa\x01\xa8?\xa7i\x00\x00\x00\x0eIDAT\x18\x95c`\x18\x05\x83\x13\x00\x00\x01\x9a\x00\x01\x16\xca\xd3i\x00\x00\x00\x00IEND\xaeB`\x82"


class TestBaseTVSyncPython(unittest.TestCase):
    PATCH_KEY = "python"
    ADB_ATTR = "_adb"

    def setUp(self):
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[
            self.PATCH_KEY
        ]:
            self.btv = BaseTVSync("HOST", 5555)
            self.btv.adb_connect()

    def test_available(self):
        """Test that the available property works correctly."""
        self.assertTrue(self.btv.available)

    def test_adb_close(self):
        """Test that the ``adb_close`` method works correctly."""
        self.btv.adb_close()
        if self.PATCH_KEY == "python":
            self.assertFalse(self.btv.available)
        else:
            self.assertTrue(self.btv.available)

    def test_adb_pull(self):
        """Test that the ``adb_pull`` method works correctly."""
        with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
            self.btv.adb_pull("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
            self.assertEqual(patch_pull.call_count, 1)

    def test_adb_push(self):
        """Test that the ``adb_push`` method works correctly."""
        with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
            self.btv.adb_push("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
            self.assertEqual(patch_push.call_count, 1)

    def test_adb_screencap(self):
        """Test that the ``adb_screencap`` method works correctly."""
        with patch.object(self.btv._adb, "screencap", return_value=PNG_IMAGE):
            self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)

    def test_keys(self):
        """Test that the key methods send the correct commands."""
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("")[self.PATCH_KEY]:
            self.btv.adb_shell("TEST")
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "TEST")

            self.btv.space()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_SPACE),
            )

            self.btv.key_0()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_0),
            )

            self.btv.key_1()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_1),
            )

            self.btv.key_2()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_2),
            )

            self.btv.key_3()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_3),
            )

            self.btv.key_4()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_4),
            )

            self.btv.key_5()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_5),
            )

            self.btv.key_6()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_6),
            )

            self.btv.key_7()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_7),
            )

            self.btv.key_8()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_8),
            )

            self.btv.key_9()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_9),
            )

            self.btv.key_a()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_A),
            )

            self.btv.key_b()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_B),
            )

            self.btv.key_c()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_C),
            )

            self.btv.key_d()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_D),
            )

            self.btv.key_e()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_E),
            )

            self.btv.key_f()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_F),
            )

            self.btv.key_g()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_G),
            )

            self.btv.key_h()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_H),
            )

            self.btv.key_i()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_I),
            )

            self.btv.key_j()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_J),
            )

            self.btv.key_k()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_K),
            )

            self.btv.key_l()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_L),
            )

            self.btv.key_m()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_M),
            )

            self.btv.key_n()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_N),
            )

            self.btv.key_o()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_O),
            )

            self.btv.key_p()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_P),
            )

            self.btv.key_q()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_Q),
            )

            self.btv.key_r()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_R),
            )

            self.btv.key_s()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_S),
            )

            self.btv.key_t()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_T),
            )

            self.btv.key_u()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_U),
            )

            self.btv.key_v()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_V),
            )

            self.btv.key_w()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_W),
            )

            self.btv.key_x()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_X),
            )

            self.btv.key_y()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_Y),
            )

            self.btv.key_z()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_Z),
            )

            self.btv.power()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_POWER),
            )

            self.btv.sleep()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_SLEEP),
            )

            self.btv.home()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_HOME),
            )

            self.btv.up()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_UP),
            )

            self.btv.down()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_DOWN),
            )

            self.btv.left()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_LEFT),
            )

            self.btv.right()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_RIGHT),
            )

            self.btv.enter()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_ENTER),
            )

            self.btv.back()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_BACK),
            )

            self.btv.menu()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_MENU),
            )

            self.btv.mute_volume()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_MUTE),
            )

            self.btv.media_play()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_PLAY),
            )

            self.btv.media_pause()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_PAUSE),
            )

            self.btv.media_play_pause()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_PLAY_PAUSE),
            )

            self.btv.media_stop()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_STOP),
            )

            self.btv.media_next_track()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_NEXT),
            )

            self.btv.media_previous_track()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd,
                "input keyevent {}".format(constants.KEY_PREVIOUS),
            )

    def test_get_device_properties(self):
        """Check that ``get_device_properties`` works correctly."""
        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(DEVICE_PROPERTIES_OUTPUT1, ETHMAC_OUTPUT1, WIFIMAC_OUTPUT1),
        ):
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT1, device_properties)

        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(DEVICE_PROPERTIES_OUTPUT2, ETHMAC_OUTPUT1, WIFIMAC_OUTPUT1),
        ):
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT2, device_properties)

        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(DEVICE_PROPERTIES_OUTPUT3, ETHMAC_OUTPUT3, WIFIMAC_OUTPUT3),
        ):
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT3, device_properties)

        with patch.object(self.btv._adb, "shell", side_effect=("manufacturer", None, "No match")):
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual({"ethmac": None, "wifimac": None}, device_properties)

        with patch.object(self.btv._adb, "shell", side_effect=("", None, "No match")):
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual({"ethmac": None, "wifimac": None}, device_properties)

        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(DEVICE_PROPERTIES_GOOGLE_TV, ETHMAC_GOOGLE, WIFIMAC_GOOGLE),
        ):
            self.btv = AndroidTVSync.from_base(self.btv)
            device_properties = self.btv.get_device_properties()
            assert "Chromecast" in self.btv.device_properties.get("model", "")
            assert self.btv.DEVICE_ENUM == AndroidTVSync.DEVICE_ENUM
            self.assertEqual(self.btv.device_properties["manufacturer"], "Google")
            self.assertEqual(self.btv._cmd_current_app(), constants.CMD_CURRENT_APP_GOOGLE_TV)
            self.assertEqual(
                self.btv._cmd_current_app_media_session_state(),
                constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE_GOOGLE_TV,
            )
            self.assertEqual(
                self.btv._cmd_launch_app("TEST"),
                constants.CMD_LAUNCH_APP_GOOGLE_TV.format("TEST"),
            )

        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(DEVICE_PROPERTIES_OUTPUT_SONY_TV, ETHMAC_SONY, WIFIMAC_SONY),
        ):
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT_SONY_TV, device_properties)

        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(
                DEVICE_PROPERTIES_OUTPUT_SHIELD_TV_11,
                ETHMAC_SHIELD_TV_11,
                WIFIMAC_SHIELD_TV_11,
            ),
        ):
            self.btv = AndroidTVSync.from_base(self.btv)
            device_properties = self.btv.get_device_properties()
            assert self.btv.device_properties.get("sw_version", "") == "11"
            assert self.btv.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV
            self.assertDictEqual(DEVICE_PROPERTIES_DICT_SHIELD_TV_11, device_properties)
            # _cmd_audio_state
            self.assertEqual(self.btv._cmd_audio_state(), constants.CMD_AUDIO_STATE11)
            # _cmd_volume_set
            self.assertEqual(self.btv._cmd_volume_set(5), constants.CMD_VOLUME_SET_COMMAND11.format(5))
            # _cmd_current_app
            self.assertEqual(self.btv._cmd_current_app(), constants.CMD_CURRENT_APP11)
            # _cmd_current_app_media_session_state
            self.assertEqual(
                self.btv._cmd_current_app_media_session_state(),
                constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE11,
            )
            # _cmd_hdmi_input
            self.assertEqual(self.btv._cmd_hdmi_input(), constants.CMD_HDMI_INPUT11)
            # _cmd_launch_app
            self.assertEqual(
                self.btv._cmd_launch_app("TEST"),
                constants.CMD_LAUNCH_APP11.format("TEST"),
            )

        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(
                DEVICE_PROPERTIES_OUTPUT_SHIELD_TV_12,
                ETHMAC_SHIELD_TV_12,
                WIFIMAC_SHIELD_TV_12,
            ),
        ):
            self.btv = AndroidTVSync.from_base(self.btv)
            device_properties = self.btv.get_device_properties()
            assert self.btv.device_properties.get("sw_version", "") == "12"
            assert self.btv.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV
            self.assertDictEqual(DEVICE_PROPERTIES_DICT_SHIELD_TV_12, device_properties)
            # _cmd_audio_state
            self.assertEqual(self.btv._cmd_audio_state(), constants.CMD_AUDIO_STATE11)
            # _cmd_volume_set
            self.assertEqual(self.btv._cmd_volume_set(5), constants.CMD_VOLUME_SET_COMMAND11.format(5))
            # _cmd_current_app
            self.assertEqual(self.btv._cmd_current_app(), constants.CMD_CURRENT_APP12)
            # _cmd_current_app_media_session_state
            self.assertEqual(
                self.btv._cmd_current_app_media_session_state(),
                constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE12,
            )
            # _cmd_hdmi_input
            self.assertEqual(self.btv._cmd_hdmi_input(), constants.CMD_HDMI_INPUT11)
            # _cmd_launch_app
            self.assertEqual(
                self.btv._cmd_launch_app("TEST"),
                constants.CMD_LAUNCH_APP12.format("TEST"),
            )

        with patch.object(
            self.btv._adb,
            "shell",
            side_effect=(
                DEVICE_PROPERTIES_OUTPUT_SHIELD_TV_13,
                ETHMAC_SHIELD_TV_13,
                WIFIMAC_SHIELD_TV_13,
            ),
        ):
            self.btv = AndroidTVSync.from_base(self.btv)
            device_properties = self.btv.get_device_properties()
            assert self.btv.device_properties.get("sw_version", "") == "13"
            assert self.btv.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV
            self.assertDictEqual(DEVICE_PROPERTIES_DICT_SHIELD_TV_13, device_properties)
            # _cmd_audio_state
            self.assertEqual(self.btv._cmd_audio_state(), constants.CMD_AUDIO_STATE11)
            # _cmd_volume_set
            self.assertEqual(self.btv._cmd_volume_set(5), constants.CMD_VOLUME_SET_COMMAND11.format(5))
            # _cmd_current_app
            self.assertEqual(self.btv._cmd_current_app(), constants.CMD_CURRENT_APP13)
            # _cmd_current_app_media_session_state
            self.assertEqual(
                self.btv._cmd_current_app_media_session_state(),
                constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE13,
            )
            # _cmd_hdmi_input
            self.assertEqual(self.btv._cmd_hdmi_input(), constants.CMD_HDMI_INPUT11)
            # _cmd_launch_app
            self.assertEqual(
                self.btv._cmd_launch_app("TEST"),
                constants.CMD_LAUNCH_APP13.format("TEST"),
            )

    def test_get_installed_apps(self):
        """ "Check that `get_installed_apps` works correctly."""
        with patchers.patch_shell(INSTALLED_APPS_OUTPUT_1)[self.PATCH_KEY]:
            installed_apps = self.btv.get_installed_apps()
            self.assertListEqual(INSTALLED_APPS_LIST, installed_apps)

        with patchers.patch_shell(None)[self.PATCH_KEY]:
            installed_apps = self.btv.get_installed_apps()
            self.assertEqual(None, installed_apps)

    def test_awake(self):
        """Check that the ``awake`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertFalse(self.btv.awake())

        with patchers.patch_shell("0")[self.PATCH_KEY]:
            self.assertFalse(self.btv.awake())

        with patchers.patch_shell("1")[self.PATCH_KEY]:
            self.assertTrue(self.btv.awake())

    def test_audio_state(self):
        """Check that the ``audio_state`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            audio_state = self.btv.audio_state()
            self.assertIsNone(audio_state, None)

        with patchers.patch_shell("0")[self.PATCH_KEY]:
            audio_state = self.btv.audio_state()
            self.assertEqual(audio_state, constants.STATE_IDLE)

        with patchers.patch_shell("1")[self.PATCH_KEY]:
            audio_state = self.btv.audio_state()
            self.assertEqual(audio_state, constants.STATE_PAUSED)

        with patchers.patch_shell("2")[self.PATCH_KEY]:
            audio_state = self.btv.audio_state()
            self.assertEqual(audio_state, constants.STATE_PLAYING)

    def test_current_app(self):
        """Check that the ``current_app`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            current_app = self.btv.current_app()
            self.assertIsNone(current_app, None)

        with patchers.patch_shell("")[self.PATCH_KEY]:
            current_app = self.btv.current_app()
            self.assertIsNone(current_app, None)

        with patchers.patch_shell("com.amazon.tv.launcher")[self.PATCH_KEY]:
            current_app = self.btv.current_app()
            self.assertEqual(current_app, "com.amazon.tv.launcher")

    def test_media_session_state(self):
        """Check that the ``media_session_state`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state()
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell("")[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state()
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell("unknown.app\n ")[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state()
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell("2")[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state()
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell(MEDIA_SESSION_STATE_OUTPUT)[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state()
            self.assertEqual(media_session_state, 2)

    def test_screen_on(self):
        """Check that the ``screen_on`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertFalse(self.btv.screen_on())

        with patchers.patch_shell("0")[self.PATCH_KEY]:
            self.assertFalse(self.btv.screen_on())

        with patchers.patch_shell("1")[self.PATCH_KEY]:
            self.assertTrue(self.btv.screen_on())

    def test_screen_on_awake_wake_lock_size(self):
        """Check that the ``screen_on_awake_wake_lock_size`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertTupleEqual(self.btv.screen_on_awake_wake_lock_size(), (None, None, None))

        with patchers.patch_shell("")[self.PATCH_KEY]:
            self.assertTupleEqual(self.btv.screen_on_awake_wake_lock_size(), (False, False, None))

        with patchers.patch_shell("1")[self.PATCH_KEY]:
            self.assertTupleEqual(self.btv.screen_on_awake_wake_lock_size(), (True, None, None))

        with patchers.patch_shell("11")[self.PATCH_KEY]:
            self.assertTupleEqual(self.btv.screen_on_awake_wake_lock_size(), (True, True, None))

        with patchers.patch_shell("11Wake Locks: size=2")[self.PATCH_KEY]:
            self.assertTupleEqual(self.btv.screen_on_awake_wake_lock_size(), (True, True, 2))

        with patchers.patch_shell(
            [
                "Failed to write while dumping serviceWake Locks: size=2",
                "11Wake Locks: size=2",
            ]
        )[self.PATCH_KEY]:
            self.assertTupleEqual(self.btv.screen_on_awake_wake_lock_size(), (True, True, 2))

    def test_state_detection_rules_validator(self):
        """Check that the ``state_detection_rules_validator`` function works correctly."""
        with patchers.patch_connect(True)["python"], patchers.patch_shell("")["python"]:
            # Make sure that no error is raised when the state detection rules are valid
            BaseTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES1)
            BaseTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES2)
            BaseTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES3)
            BaseTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES4)
            BaseTVSync("HOST", 5555, state_detection_rules=STATE_DETECTION_RULES5)

            # Make sure that an error is raised when the state detection rules are invalid
            self.assertRaises(
                TypeError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID1,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID2,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID3,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID4,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID5,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID6,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID7,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID8,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID9,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID10,
            )
            self.assertRaises(
                KeyError,
                BaseTVSync,
                "HOST",
                5555,
                "",
                "",
                5037,
                state_detection_rules=STATE_DETECTION_RULES_INVALID11,
            )

    def test_wake_lock_size(self):
        """Check that the ``wake_lock_size`` property works correctly."""
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertIsNone(self.btv.wake_lock_size())

        with patchers.patch_shell("")[self.PATCH_KEY]:
            self.assertIsNone(self.btv.wake_lock_size())

        with patchers.patch_shell("Wake Locks: size=2")[self.PATCH_KEY]:
            self.assertEqual(self.btv.wake_lock_size(), 2)

        with patchers.patch_shell("INVALID")[self.PATCH_KEY]:
            self.assertIsNone(self.btv.wake_lock_size())

    def test_get_hdmi_input(self):
        """Check that the ``get_hdmi_input`` function works correctly."""
        with patchers.patch_shell("HW2")[self.PATCH_KEY]:
            self.assertEqual(self.btv.get_hdmi_input(), "HW2")

        with patchers.patch_shell("HW2\n")[self.PATCH_KEY]:
            self.assertEqual(self.btv.get_hdmi_input(), "HW2")

        with patchers.patch_shell("HW2\r\n")[self.PATCH_KEY]:
            self.assertEqual(self.btv.get_hdmi_input(), "HW2")

        with patchers.patch_shell("")[self.PATCH_KEY]:
            self.assertIsNone(self.btv.get_hdmi_input())

        with patchers.patch_shell("\r\n")[self.PATCH_KEY]:
            self.assertIsNone(self.btv.get_hdmi_input())

        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertIsNone(self.btv.get_hdmi_input())

    def test_learn_sendevent(self):
        """Check that the ``learn_sendevent`` method works correctly."""
        with patchers.patch_shell(
            'add device 1: /dev/input/event4\r\n  name:     "Amazon Fire TV Remote"\r\nadd device 2: /dev/input/event3\r\n  name:     "kcmouse"\r\ncould not get driver version for /dev/input/mouse0, Not a typewriter\r\nadd device 3: /dev/input/event2\r\n  name:     "amazon_touch"\r\nadd device 4: /dev/input/event1\r\n  name:     "hdmipower"\r\nadd device 5: /dev/input/event0\r\n  name:     "mtk-kpd"\r\ncould not get driver version for /dev/input/mice, Not a typewriter\r\n/dev/input/event4: 0004 0004 00070051\r\n/dev/input/event4: 0001 006c 00000001\r\n/dev/input/event4: 0000 0000 00000000\r\n/dev/input/event4: 0004 0004 00070051\r\n/dev/input/event4: 0001 006c 00000000\r\n/dev/input/event4: 0000 0000 00000000\r\nyour command was interrupted'
        )[self.PATCH_KEY]:
            self.assertEqual(
                self.btv.learn_sendevent(),
                "sendevent /dev/input/event4 4 4 458833 && sendevent /dev/input/event4 1 108 1 && sendevent /dev/input/event4 0 0 0 && sendevent /dev/input/event4 4 4 458833 && sendevent /dev/input/event4 1 108 0 && sendevent /dev/input/event4 0 0 0",
            )

        with patchers.patch_shell("This is not a valid response")[self.PATCH_KEY]:
            self.assertEqual(self.btv.learn_sendevent(), "")


class TestHAStateDetectionRulesValidator(unittest.TestCase):
    def test_ha_state_detection_rules_validator(self):
        """Check that ``ha_state_detection_rules_validator()`` works correctly."""
        with self.assertRaises(AssertionError):
            for app_id, rules in STATE_DETECTION_RULES_INVALID2.items():
                ha_state_detection_rules_validator(AssertionError)(rules)


if __name__ == "__main__":
    unittest.main()
