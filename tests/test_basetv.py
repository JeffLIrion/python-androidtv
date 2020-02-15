import sys
import unittest


sys.path.insert(0, '..')

from androidtv import constants, ha_state_detection_rules_validator
from androidtv.basetv import BaseTV
from . import patchers


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

DEVICE_PROPERTIES_OUTPUT3 = """Not Amazon
AFTT
SERIALNO
5.1.1
Device "wlan0" does not exist.
    link/ether ab:cd:ef:gh:ij:kl brd ff:ff:ff:ff:ff:ff
"""

DEVICE_PROPERTIES_DICT3 = {'manufacturer': 'Not Amazon',
                           'model': 'AFTT',
                           'serialno': 'SERIALNO',
                           'sw_version': '5.1.1',
                           'wifimac': None,
                           'ethmac': 'ab:cd:ef:gh:ij:kl'}

MEDIA_SESSION_STATE_OUTPUT = "com.amazon.tv.launcher\nstate=PlaybackState {state=2, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}"

STATE_DETECTION_RULES1 = {'com.amazon.tv.launcher': ['off']}
STATE_DETECTION_RULES2 = {'com.amazon.tv.launcher': ['media_session_state', 'off']}
STATE_DETECTION_RULES3 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES4 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 1}}, 'paused']}
STATE_DETECTION_RULES5 = {'com.amazon.tv.launcher': ['audio_state']}

STATE_DETECTION_RULES_INVALID1 = {123: ['media_session_state']}
STATE_DETECTION_RULES_INVALID2 = {'com.amazon.tv.launcher': [123]}
STATE_DETECTION_RULES_INVALID3 = {'com.amazon.tv.launcher': ['INVALID']}
STATE_DETECTION_RULES_INVALID4 = {'com.amazon.tv.launcher': [{'INVALID': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES_INVALID5 = {'com.amazon.tv.launcher': [{'standby': 'INVALID'}]}
STATE_DETECTION_RULES_INVALID6 = {'com.amazon.tv.launcher': [{'standby': {'INVALID': 2}}]}
STATE_DETECTION_RULES_INVALID7 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 'INVALID'}}]}
STATE_DETECTION_RULES_INVALID8 = {'com.amazon.tv.launcher': [{'standby': {'media_session_state': 'INVALID'}}]}
STATE_DETECTION_RULES_INVALID9 = {'com.amazon.tv.launcher': [{'standby': {'audio_state': 123}}]}
STATE_DETECTION_RULES_INVALID10 = {'com.amazon.tv.launcher': [{'standby': {'media_session_state': 'INVALID'}}]}
STATE_DETECTION_RULES_INVALID11 = {'com.amazon.tv.launcher': [{'standby': {'audio_state': 123}}]}


class TestBaseTVPython(unittest.TestCase):
    PATCH_KEY = 'python'
    ADB_ATTR = '_adb'

    def setUp(self):
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.btv = BaseTV('HOST', 5555)

    def test_available(self):
        """Test that the available property works correctly.

        """
        self.assertTrue(self.btv.available)

    def test_adb_close(self):
        """Test that the ``adb_close`` method works correctly.

        """
        self.btv.adb_close()
        if self.PATCH_KEY == 'python':
            self.assertFalse(self.btv.available)
        else:
            self.assertTrue(self.btv.available)

    def test_adb_pull(self):
        """Test that the ``adb_pull`` method works correctly.

        """
        with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
            self.btv.adb_pull("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
            self.assertEqual(patch_pull.call_count, 1)

    def test_adb_push(self):
        """Test that the ``adb_push`` method works correctly.

        """
        with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
            self.btv.adb_push("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
            self.assertEqual(patch_push.call_count, 1)

    def test_keys(self):
        """Test that the key methods send the correct commands.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.btv.adb_shell("TEST")
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "TEST")

            self.btv.space()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_SPACE))

            self.btv.key_0()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_0))

            self.btv.key_1()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_1))

            self.btv.key_2()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_2))

            self.btv.key_3()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_3))

            self.btv.key_4()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_4))

            self.btv.key_5()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_5))

            self.btv.key_6()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_6))

            self.btv.key_7()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_7))

            self.btv.key_8()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_8))

            self.btv.key_9()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_9))

            self.btv.key_a()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_A))

            self.btv.key_b()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_B))

            self.btv.key_c()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_C))

            self.btv.key_d()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_D))

            self.btv.key_e()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_E))

            self.btv.key_f()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_F))

            self.btv.key_g()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_G))

            self.btv.key_h()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_H))

            self.btv.key_i()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_I))

            self.btv.key_j()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_J))

            self.btv.key_k()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_K))

            self.btv.key_l()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_L))

            self.btv.key_m()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_M))

            self.btv.key_n()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_N))

            self.btv.key_o()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_O))

            self.btv.key_p()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_P))

            self.btv.key_q()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Q))

            self.btv.key_r()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_R))

            self.btv.key_s()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_S))

            self.btv.key_t()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_T))

            self.btv.key_u()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_U))

            self.btv.key_v()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_V))

            self.btv.key_w()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_W))

            self.btv.key_x()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_X))

            self.btv.key_y()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Y))

            self.btv.key_z()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Z))

            self.btv.power()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_POWER))

            self.btv.sleep()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_SLEEP))

            self.btv.home()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_HOME))

            self.btv.up()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_UP))

            self.btv.down()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_DOWN))

            self.btv.left()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_LEFT))

            self.btv.right()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_RIGHT))

            self.btv.enter()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_ENTER))

            self.btv.back()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_BACK))

            self.btv.menu()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_MENU))

            self.btv.mute_volume()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_MUTE))

            self.btv.media_play()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PLAY))

            self.btv.media_pause()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PAUSE))

            self.btv.media_play_pause()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PLAY_PAUSE))

            self.btv.media_stop()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_STOP))

            self.btv.media_next_track()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_NEXT))

            self.btv.media_previous_track()
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PREVIOUS))

    def test_get_device_properties(self):
        """Check that ``get_device_properties`` works correctly.

        """
        with patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT1, device_properties)

        with patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT2, device_properties)

        with patchers.patch_shell(DEVICE_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual(DEVICE_PROPERTIES_DICT3, device_properties)

        with patchers.patch_shell('manufacturer')[self.PATCH_KEY]:
            device_properties = self.btv.get_device_properties()
            self.assertDictEqual({}, device_properties)

    def test_awake(self):
        """Check that the ``awake`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertFalse(self.btv.awake)

        with patchers.patch_shell('0')[self.PATCH_KEY]:
            self.assertFalse(self.btv.awake)

        with patchers.patch_shell('1')[self.PATCH_KEY]:
            self.assertTrue(self.btv.awake)

    def test_audio_state(self):
        """Check that the ``audio_state`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            audio_state = self.btv.audio_state
            self.assertIsNone(audio_state, None)

        with patchers.patch_shell('0')[self.PATCH_KEY]:
            audio_state = self.btv.audio_state
            self.assertEqual(audio_state, constants.STATE_IDLE)

        with patchers.patch_shell('1')[self.PATCH_KEY]:
            audio_state = self.btv.audio_state
            self.assertEqual(audio_state, constants.STATE_PAUSED)

        with patchers.patch_shell('2')[self.PATCH_KEY]:
            audio_state = self.btv.audio_state
            self.assertEqual(audio_state, constants.STATE_PLAYING)

    def test_current_app(self):
        """Check that the ``current_app`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            current_app = self.btv.current_app
            self.assertIsNone(current_app, None)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            current_app = self.btv.current_app
            self.assertIsNone(current_app, None)

        with patchers.patch_shell('com.amazon.tv.launcher')[self.PATCH_KEY]:
            current_app = self.btv.current_app
            self.assertEqual(current_app, "com.amazon.tv.launcher")

    def test_media_session_state(self):
        """Check that the ``media_session_state`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell('unknown.app\n ')[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell('2')[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state
            self.assertIsNone(media_session_state, None)

        with patchers.patch_shell(MEDIA_SESSION_STATE_OUTPUT)[self.PATCH_KEY]:
            media_session_state = self.btv.media_session_state
            self.assertEqual(media_session_state, 2)

    def test_screen_on(self):
        """Check that the ``screen_on`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertFalse(self.btv.screen_on)

        with patchers.patch_shell('0')[self.PATCH_KEY]:
            self.assertFalse(self.btv.screen_on)

        with patchers.patch_shell('1')[self.PATCH_KEY]:
            self.assertTrue(self.btv.screen_on)

    def test_state_detection_rules_validator(self):
        """Check that the ``state_detection_rules_validator`` function works correctly.

        """
        with patchers.patch_connect(True)['python'], patchers.patch_shell('')['python']:
            # Make sure that no error is raised when the state detection rules are valid
            BaseTV('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES1)
            BaseTV('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES2)
            BaseTV('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES3)
            BaseTV('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES4)
            BaseTV('HOST', 5555, state_detection_rules=STATE_DETECTION_RULES5)

            # Make sure that an error is raised when the state detection rules are invalid
            self.assertRaises(TypeError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID1)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID2)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID3)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID4)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID5)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID6)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID7)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID8)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID9)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID10)
            self.assertRaises(KeyError, BaseTV, 'HOST', 5555, '', '', 5037, state_detection_rules=STATE_DETECTION_RULES_INVALID11)

    def test_wake_lock_size(self):
        """Check that the ``wake_lock_size`` property works correctly.

        """
        with patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertIsNone(self.btv.wake_lock_size)

        with patchers.patch_shell('')[self.PATCH_KEY]:
            self.assertIsNone(self.btv.wake_lock_size)

        with patchers.patch_shell('Wake Locks: size=2')[self.PATCH_KEY]:
            self.assertEqual(self.btv.wake_lock_size, 2)

        with patchers.patch_shell('INVALID')[self.PATCH_KEY]:
            self.assertIsNone(self.btv.wake_lock_size)


class TestHAStateDetectionRulesValidator(unittest.TestCase):
    def test_ha_state_detection_rules_validator(self):
        """Check that ``ha_state_detection_rules_validator()`` works correctly.

        """
        with self.assertRaises(AssertionError):
            for app_id, rules in STATE_DETECTION_RULES_INVALID2.items():
                ha_state_detection_rules_validator(AssertionError)(rules)


if __name__ == "__main__":
    unittest.main()
