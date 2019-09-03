import sys
import unittest


sys.path.insert(0, '..')

from androidtv import constants
from androidtv.androidtv import AndroidTV
from androidtv.firetv import FireTV
from . import patchers


class TestAndroidTVSimplePython(unittest.TestCase):
    PATCH_KEY = 'python'
    ADB_ATTR = '_adb'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv = AndroidTV('IP:PORT')

    def test_keys(self):
        """Test that the key methods send the correct commands.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.atv.space()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_SPACE))

            self.atv.key_0()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_0))

            self.atv.key_1()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_1))

            self.atv.key_2()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_2))

            self.atv.key_3()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_3))

            self.atv.key_4()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_4))

            self.atv.key_5()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_5))

            self.atv.key_6()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_6))

            self.atv.key_7()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_7))

            self.atv.key_8()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_8))

            self.atv.key_9()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_9))

            self.atv.key_a()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_A))

            self.atv.key_b()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_B))

            self.atv.key_c()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_C))

            self.atv.key_d()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_D))

            self.atv.key_e()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_E))

            self.atv.key_f()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_F))

            self.atv.key_g()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_G))

            self.atv.key_h()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_H))

            self.atv.key_i()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_I))

            self.atv.key_j()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_J))

            self.atv.key_k()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_K))

            self.atv.key_l()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_L))

            self.atv.key_m()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_M))

            self.atv.key_n()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_N))

            self.atv.key_o()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_O))

            self.atv.key_p()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_P))

            self.atv.key_q()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Q))

            self.atv.key_r()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_R))

            self.atv.key_s()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_S))

            self.atv.key_t()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_T))

            self.atv.key_u()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_U))

            self.atv.key_v()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_V))

            self.atv.key_w()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_W))

            self.atv.key_x()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_X))

            self.atv.key_y()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Y))

            self.atv.key_z()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Z))

            self.atv.power()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_POWER))

            self.atv.sleep()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_SLEEP))

            self.atv.home()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_HOME))

            self.atv.up()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_UP))

            self.atv.down()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_DOWN))

            self.atv.left()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_LEFT))

            self.atv.right()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_RIGHT))

            self.atv.enter()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_ENTER))

            self.atv.back()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_BACK))

            self.atv.menu()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_MENU))

            self.atv.mute_volume()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_MUTE))

            self.atv.media_play()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PLAY))

            self.atv.media_pause()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PAUSE))

            self.atv.media_play_pause()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PLAY_PAUSE))

            self.atv.media_stop()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_STOP))

            self.atv.media_next_track()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_NEXT))

            self.atv.media_previous_track()
            self.assertEqual(getattr(self.atv.adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PREVIOUS))

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


class TestFireTVSimplePython(unittest.TestCase):
    PATCH_KEY = 'python'
    ADB_ATTR = '_adb'

    def setUp(self):
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.ftv = FireTV('IP:PORT')

    def test_turn_on_off(self):
        """Test that the ``FireTV.turn_on`` and ``FireTV.turn_off`` methods work correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.ftv.turn_on()
            self.assertEqual(getattr(self.ftv.adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " || (input keyevent {0} && input keyevent {1})".format(constants.KEY_POWER, constants.KEY_HOME))

            self.ftv.turn_off()
            self.assertEqual(getattr(self.ftv.adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_SLEEP))

    def test_launch_app_stop_app(self):
        """Test that the ``FireTV.launch_app`` and ``FireTV.stop_app`` methods work correctly.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell('')[self.PATCH_KEY]:
            self.ftv.launch_app("TEST")
            self.assertEqual(getattr(self.ftv.adb, self.ADB_ATTR).shell_cmd, "monkey -p TEST -c android.intent.category.LAUNCHER 1; echo $?")

            self.ftv.stop_app("TEST")
            self.assertEqual(getattr(self.ftv.adb, self.ADB_ATTR).shell_cmd, "am force-stop TEST")


if __name__ == "__main__":
    unittest.main()
