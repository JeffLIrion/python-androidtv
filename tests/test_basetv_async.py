import asyncio
import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, "..")

import androidtv
from androidtv import constants
from androidtv.basetv.basetv_async import BaseTVAsync

from . import async_patchers
from .async_wrapper import awaiter
from .patchers import patch_calls

PNG_IMAGE = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0fa\x00\x00\x0fa\x01\xa8?\xa7i\x00\x00\x00\x0eIDAT\x18\x95c`\x18\x05\x83\x13\x00\x00\x01\x9a\x00\x01\x16\xca\xd3i\x00\x00\x00\x00IEND\xaeB`\x82"


class TestBaseTVAsyncPython(unittest.TestCase):
    PATCH_KEY = "python"
    ADB_ATTR = "_adb"

    @awaiter
    async def setUp(self):
        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[
            self.PATCH_KEY
        ], async_patchers.patch_shell("")[self.PATCH_KEY]:
            self.btv = BaseTVAsync("HOST", 5555)
            await self.btv.adb_connect()

    def test_available(self):
        """Test that the available property works correctly."""
        self.assertTrue(self.btv.available)

    @awaiter
    async def test_adb_close(self):
        """Test that the ``adb_close`` method works correctly."""
        await self.btv.adb_close()
        if self.PATCH_KEY == "python":
            self.assertFalse(self.btv.available)
        else:
            self.assertTrue(self.btv.available)

    @awaiter
    async def test_adb_pull(self):
        """Test that the ``adb_pull`` method works correctly."""
        with async_patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
            await self.btv.adb_pull("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
            self.assertEqual(patch_pull.call_count, 1)

    @awaiter
    async def test_adb_push(self):
        """Test that the ``adb_push`` method works correctly."""
        with async_patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
            await self.btv.adb_push("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
            self.assertEqual(patch_push.call_count, 1)

    @awaiter
    async def test_adb_screencap(self):
        """Test that the ``adb_screencap`` method works correctly."""
        with patch.object(self.btv._adb, "screencap", return_value=PNG_IMAGE, new_callable=async_patchers.AsyncMock):
            self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)

    @awaiter
    async def test_keys(self):
        """Test that the key methods send the correct commands."""
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell("")[self.PATCH_KEY]:
            await self.btv.adb_shell("TEST")
            self.assertEqual(getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "TEST")

            await self.btv.space()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_SPACE)
            )

            await self.btv.key_0()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_0)
            )

            await self.btv.key_1()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_1)
            )

            await self.btv.key_2()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_2)
            )

            await self.btv.key_3()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_3)
            )

            await self.btv.key_4()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_4)
            )

            await self.btv.key_5()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_5)
            )

            await self.btv.key_6()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_6)
            )

            await self.btv.key_7()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_7)
            )

            await self.btv.key_8()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_8)
            )

            await self.btv.key_9()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_9)
            )

            await self.btv.key_a()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_A)
            )

            await self.btv.key_b()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_B)
            )

            await self.btv.key_c()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_C)
            )

            await self.btv.key_d()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_D)
            )

            await self.btv.key_e()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_E)
            )

            await self.btv.key_f()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_F)
            )

            await self.btv.key_g()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_G)
            )

            await self.btv.key_h()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_H)
            )

            await self.btv.key_i()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_I)
            )

            await self.btv.key_j()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_J)
            )

            await self.btv.key_k()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_K)
            )

            await self.btv.key_l()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_L)
            )

            await self.btv.key_m()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_M)
            )

            await self.btv.key_n()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_N)
            )

            await self.btv.key_o()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_O)
            )

            await self.btv.key_p()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_P)
            )

            await self.btv.key_q()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Q)
            )

            await self.btv.key_r()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_R)
            )

            await self.btv.key_s()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_S)
            )

            await self.btv.key_t()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_T)
            )

            await self.btv.key_u()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_U)
            )

            await self.btv.key_v()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_V)
            )

            await self.btv.key_w()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_W)
            )

            await self.btv.key_x()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_X)
            )

            await self.btv.key_y()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Y)
            )

            await self.btv.key_z()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_Z)
            )

            await self.btv.power()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_POWER)
            )

            await self.btv.sleep()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_SLEEP)
            )

            await self.btv.home()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_HOME)
            )

            await self.btv.up()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_UP)
            )

            await self.btv.down()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_DOWN)
            )

            await self.btv.left()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_LEFT)
            )

            await self.btv.right()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_RIGHT)
            )

            await self.btv.enter()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_ENTER)
            )

            await self.btv.back()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_BACK)
            )

            await self.btv.menu()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_MENU)
            )

            await self.btv.mute_volume()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_MUTE)
            )

            await self.btv.media_play()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PLAY)
            )

            await self.btv.media_pause()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PAUSE)
            )

            await self.btv.media_play_pause()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PLAY_PAUSE)
            )

            await self.btv.media_stop()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_STOP)
            )

            await self.btv.media_next_track()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_NEXT)
            )

            await self.btv.media_previous_track()
            self.assertEqual(
                getattr(self.btv._adb, self.ADB_ATTR).shell_cmd, "input keyevent {}".format(constants.KEY_PREVIOUS)
            )

    @awaiter
    async def test_get_device_properties(self):
        """Check that ``get_device_properties`` works correctly."""
        with async_patchers.patch_shell("")[self.PATCH_KEY]:
            with patch_calls(self.btv, self.btv._parse_device_properties) as patched:
                await self.btv.get_device_properties()
                assert patched.called

    @awaiter
    async def test_awake(self):
        """Check that the ``awake`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertFalse(await self.btv.awake())

        with async_patchers.patch_shell("0")[self.PATCH_KEY]:
            self.assertFalse(await self.btv.awake())

        with async_patchers.patch_shell("1")[self.PATCH_KEY]:
            self.assertTrue(await self.btv.awake())

    @awaiter
    async def test_audio_state(self):
        """Check that the ``audio_state`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.btv, self.btv._audio_state) as patched:
                await self.btv.audio_state()
                assert patched.called

    @awaiter
    async def test_current_app(self):
        """Check that the ``current_app`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.btv, self.btv._current_app) as patched:
                await self.btv.current_app()
                assert patched.called

    @awaiter
    async def test_get_installed_apps(self):
        """ "Check that `get_installed_apps` works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.btv, self.btv._get_installed_apps) as patched:
                await self.btv.get_installed_apps()
                assert patched.called

    @awaiter
    async def test_media_session_state(self):
        """Check that the ``media_session_state`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.btv, self.btv._current_app_media_session_state) as patched:
                await self.btv.media_session_state()
                assert patched.called

    @awaiter
    async def test_screen_on(self):
        """Check that the ``screen_on`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertFalse(await self.btv.screen_on())

        with async_patchers.patch_shell("0")[self.PATCH_KEY]:
            self.assertFalse(await self.btv.screen_on())

        with async_patchers.patch_shell("1")[self.PATCH_KEY]:
            self.assertTrue(await self.btv.screen_on())

    @awaiter
    async def test_screen_on_awake_wake_lock_size(self):
        """Check that the ``screen_on_awake_wake_lock_size`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertTupleEqual(await self.btv.screen_on_awake_wake_lock_size(), (None, None, None))

        with async_patchers.patch_shell("")[self.PATCH_KEY]:
            self.assertTupleEqual(await self.btv.screen_on_awake_wake_lock_size(), (False, False, None))

        with async_patchers.patch_shell("1")[self.PATCH_KEY]:
            self.assertTupleEqual(await self.btv.screen_on_awake_wake_lock_size(), (True, None, None))

        with async_patchers.patch_shell("11")[self.PATCH_KEY]:
            self.assertTupleEqual(await self.btv.screen_on_awake_wake_lock_size(), (True, True, None))

        with async_patchers.patch_shell("11Wake Locks: size=2")[self.PATCH_KEY]:
            self.assertTupleEqual(await self.btv.screen_on_awake_wake_lock_size(), (True, True, 2))

        with async_patchers.patch_shell(
            ["Failed to write while dumping serviceWake Locks: size=2", "11Wake Locks: size=2"]
        )[self.PATCH_KEY]:
            self.assertTupleEqual(await self.btv.screen_on_awake_wake_lock_size(), (True, True, 2))

    @awaiter
    async def test_wake_lock_size(self):
        """Check that the ``wake_lock_size`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.btv, self.btv._wake_lock_size) as patched:
                await self.btv.wake_lock_size()
                assert patched.called

    @awaiter
    async def test_get_hdmi_input(self):
        """Check that the ``get_hdmi_input`` function works correctly."""
        with async_patchers.patch_shell("HW2")[self.PATCH_KEY]:
            with patch_calls(self.btv, self.btv._get_hdmi_input) as patched:
                await self.btv.get_hdmi_input()
                assert patched.called

    @awaiter
    async def test_learn_sendevent(self):
        """Check that the ``learn_sendevent`` method works correctly."""
        with async_patchers.patch_shell(
            'add device 1: /dev/input/event4\r\n  name:     "Amazon Fire TV Remote"\r\nadd device 2: /dev/input/event3\r\n  name:     "kcmouse"\r\ncould not get driver version for /dev/input/mouse0, Not a typewriter\r\nadd device 3: /dev/input/event2\r\n  name:     "amazon_touch"\r\nadd device 4: /dev/input/event1\r\n  name:     "hdmipower"\r\nadd device 5: /dev/input/event0\r\n  name:     "mtk-kpd"\r\ncould not get driver version for /dev/input/mice, Not a typewriter\r\n/dev/input/event4: 0004 0004 00070051\r\n/dev/input/event4: 0001 006c 00000001\r\n/dev/input/event4: 0000 0000 00000000\r\n/dev/input/event4: 0004 0004 00070051\r\n/dev/input/event4: 0001 006c 00000000\r\n/dev/input/event4: 0000 0000 00000000\r\nyour command was interrupted'
        )[self.PATCH_KEY]:
            self.assertEqual(
                await self.btv.learn_sendevent(),
                "sendevent /dev/input/event4 4 4 458833 && sendevent /dev/input/event4 1 108 1 && sendevent /dev/input/event4 0 0 0 && sendevent /dev/input/event4 4 4 458833 && sendevent /dev/input/event4 1 108 0 && sendevent /dev/input/event4 0 0 0",
            )

        with async_patchers.patch_shell("This is not a valid response")[self.PATCH_KEY]:
            self.assertEqual(await self.btv.learn_sendevent(), "")


if __name__ == "__main__":
    unittest.main()
