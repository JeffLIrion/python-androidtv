import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, '..')

from androidtv import constants
from androidtv.firetv.firetv_async import FireTVAsync

from . import async_patchers
from .async_wrapper import awaiter
from .patchers import patch_calls


class TestFireTVAsyncPython(unittest.TestCase):
    ADB_ATTR = '_adb'
    PATCH_KEY = 'python'

    @awaiter
    async def setUp(self):
        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('')[self.PATCH_KEY]:
            self.ftv = FireTVAsync('HOST', 5555)
            await self.ftv.adb_connect()

    @awaiter
    async def test_turn_on_off(self):
        """Test that the ``FireTVAsync.turn_on`` and ``FireTVAsync.turn_off`` methods work correctly.

        """
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('')[self.PATCH_KEY]:
            await self.ftv.turn_on()
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " || (input keyevent {0} && input keyevent {1})".format(constants.KEY_POWER, constants.KEY_HOME))

            await self.ftv.turn_off()
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_SLEEP))

    @awaiter
    async def test_send_intent(self):
        """Test that the ``_send_intent`` method works correctly.

        """
        with async_patchers.patch_shell('output\r\nretcode')[self.PATCH_KEY]:
            result = await self.ftv._send_intent("TEST", constants.INTENT_LAUNCH)
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, "monkey -p TEST -c android.intent.category.LAUNCHER 1; echo $?")
            self.assertDictEqual(result, {'output': 'output', 'retcode': 'retcode'})

        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell(None)[self.PATCH_KEY]:
            result = await self.ftv._send_intent("TEST", constants.INTENT_LAUNCH)
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, "monkey -p TEST -c android.intent.category.LAUNCHER 1; echo $?")
            self.assertDictEqual(result, {})

    @awaiter
    async def test_launch_app_stop_app(self):
        """Test that the ``FireTVAsync.launch_app`` and ``FireTVAsync.stop_app`` methods work correctly.

        """
        with async_patchers.patch_shell('')[self.PATCH_KEY]:
            await self.ftv.launch_app("TEST")
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_LAUNCH_APP.format("TEST"))

            await self.ftv.stop_app("TEST")
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, "am force-stop TEST")

    @awaiter
    async def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly.

        """
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.ftv, self.ftv._running_apps) as patched:
                await self.ftv.running_apps()
                assert patched.called

    @awaiter
    async def test_get_properties(self):
        """Check that ``get_properties()`` works correctly.

        """
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            for get_running_apps in [True, False]:
                for lazy in [True, False]:
                    with patch_calls(self.ftv, self.ftv._get_properties) as patched:
                        await self.ftv.get_properties_dict(get_running_apps, lazy)
                        assert patched.called

    @awaiter
    async def test_update(self):
        """Check that the ``update`` method works correctly.

        """
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            with patch_calls(self.ftv, self.ftv._get_properties) as patched:
                await self.ftv.update()
                assert patched.called


class TestFireTVAsyncServer(TestFireTVAsyncPython):
    ADB_ATTR = '_adb_device'
    PATCH_KEY = 'server'

    @awaiter
    async def setUp(self):
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('')[self.PATCH_KEY]:
            self.ftv = FireTVAsync('HOST', 5555, adb_server_ip='ADB_SERVER_IP')
            await self.ftv.adb_connect()


if __name__ == "__main__":
    unittest.main()
