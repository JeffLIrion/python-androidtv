import asyncio
import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, "..")

from androidtv import constants
from androidtv.androidtv.androidtv_async import AndroidTVAsync

from . import async_patchers
from .async_wrapper import awaiter
from .patchers import patch_calls


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


class TestAndroidTVAsyncPython(unittest.TestCase):
    PATCH_KEY = "python"
    ADB_ATTR = "_adb"

    @awaiter
    async def setUp(self):
        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[
            self.PATCH_KEY
        ], async_patchers.patch_shell("")[self.PATCH_KEY]:
            self.atv = AndroidTVAsync("HOST", 5555)
            await self.atv.adb_connect()
            self.assertEqual(
                self.atv._cmd_get_properties_lazy_no_running_apps,
                constants.CMD_ANDROIDTV_PROPERTIES_LAZY_NO_RUNNING_APPS,
            )

    @awaiter
    async def test_turn_on_off(self):
        """Test that the ``AndroidTVAsync.turn_on`` and ``AndroidTVAsync.turn_off`` methods work correctly."""
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell("")[self.PATCH_KEY]:
            await self.atv.turn_on()
            self.assertEqual(
                getattr(self.atv._adb, self.ADB_ATTR).shell_cmd,
                constants.CMD_SCREEN_ON + " || input keyevent {0}".format(constants.KEY_POWER),
            )

            await self.atv.turn_off()
            self.assertEqual(
                getattr(self.atv._adb, self.ADB_ATTR).shell_cmd,
                constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_POWER),
            )

    @awaiter
    async def test_start_intent(self):
        """Test that the ``start_intent`` method works correctly."""
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell("")[self.PATCH_KEY]:
            await self.atv.start_intent("TEST")
            self.assertEqual(
                getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "am start -a android.intent.action.VIEW -d TEST"
            )

    @awaiter
    async def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.atv, self.atv._running_apps) as patched:
                await self.atv.running_apps()
                assert patched.called

    @awaiter
    async def test_audio_output_device(self):
        """Check that the ``device`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.atv, self.atv._audio_output_device) as patched:
                await self.atv.audio_output_device()
                assert patched.called

    @awaiter
    async def test_volume(self):
        """Check that the ``volume`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.atv, self.atv._volume) as patched:
                await self.atv.volume()
                assert patched.called

    @awaiter
    async def test_volume_level(self):
        """Check that the ``volume_level`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.atv, self.atv._volume_level) as patched:
                await self.atv.volume_level()
                assert patched.called

    @awaiter
    async def test_is_volume_muted(self):
        """Check that the ``is_volume_muted`` property works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.atv, self.atv._is_volume_muted) as patched:
                await self.atv.is_volume_muted()
                assert patched.called

    @awaiter
    async def test_set_volume_level(self):
        """Check that the ``set_volume_level`` method works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = await self.atv.set_volume_level(0.5)
            self.assertIsNone(new_volume_level)

        with async_patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = await self.atv.set_volume_level(0.5)
            self.assertIsNone(new_volume_level)

        with async_patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = await self.atv.set_volume_level(0.5)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 30")

        with async_patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = await self.atv.set_volume_level(30.0 / 60)
            self.assertEqual(new_volume_level, 0.5)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 30")

        with async_patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = await self.atv.set_volume_level(22.0 / 60)
            self.assertEqual(new_volume_level, 22.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "media volume --show --stream 3 --set 22")

    @awaiter
    async def test_volume_up(self):
        """Check that the ``volume_up`` method works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with async_patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_up()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with async_patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_up()
            self.assertEqual(new_volume_level, 23.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = await self.atv.volume_up(23.0 / 60)
            self.assertEqual(new_volume_level, 24.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

        with async_patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_up()
            self.assertEqual(new_volume_level, 21.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")
            new_volume_level = await self.atv.volume_up(21.0 / 60)
            self.assertEqual(new_volume_level, 22.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 24")

    @awaiter
    async def test_volume_down(self):
        """Check that the ``volume_down`` method works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with async_patchers.patch_shell("")[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_down()
            self.assertIsNone(new_volume_level)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with async_patchers.patch_shell(STREAM_MUSIC_ON)[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_down()
            self.assertEqual(new_volume_level, 21.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = await self.atv.volume_down(21.0 / 60)
            self.assertEqual(new_volume_level, 20.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

        with async_patchers.patch_shell(STREAM_MUSIC_OFF)[self.PATCH_KEY]:
            new_volume_level = await self.atv.volume_down()
            self.assertEqual(new_volume_level, 19.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")
            new_volume_level = await self.atv.volume_down(19.0 / 60)
            self.assertEqual(new_volume_level, 18.0 / 60)
            self.assertEqual(getattr(self.atv._adb, self.ADB_ATTR).shell_cmd, "input keyevent 25")

    @awaiter
    async def test_get_properties(self):
        """Check that the ``get_properties`` method works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            for get_running_apps in [True, False]:
                for lazy in [True, False]:
                    with patch_calls(self.atv, self.atv._get_properties) as patched:
                        await self.atv.get_properties_dict(get_running_apps, lazy)
                        assert patched.called

    @awaiter
    async def test_update(self):
        """Check that the ``update`` method works correctly."""
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.atv, self.atv._update) as patched:
                await self.atv.update()
                assert patched.called


class TestAndroidTVAsyncServer(TestAndroidTVAsyncPython):
    PATCH_KEY = "server"
    ADB_ATTR = "_adb_device"

    @awaiter
    async def setUp(self):
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell("")[self.PATCH_KEY]:
            self.atv = AndroidTVAsync("HOST", 5555, adb_server_ip="ADB_SERVER_IP")
            await self.atv.adb_connect()


if __name__ == "__main__":
    unittest.main()
