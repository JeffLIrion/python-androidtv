import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, '..')

from androidtv.adb_manager.adb_manager_async import ClientAsync

from .async_wrapper import awaiter
from . import patchers


class TestAsyncClientDevice(unittest.TestCase):
    """Test the ``ClientAsync`` and ``DeviceAsync`` classes defined in ``adb_manager_async.py``.

    This file can be removed once true async support for using an ADB server is available.

    """

    @awaiter
    async def test_async_client_device(self):
        with patch("androidtv.adb_manager.adb_manager_async.Client", patchers.ClientFakeSuccess):
            client = ClientAsync("host", "port")

            device = await client.device("serial")

            with patch("{}.DeviceFake.shell".format(patchers.__name__)):
                await device.shell("test")

            with patch("{}.DeviceFake.push".format(patchers.__name__)):
                await device.push("local_path", "device_path")

            with patch("{}.DeviceFake.pull".format(patchers.__name__)):
                await device.pull("device_path", "local_path")

            with patch("{}.DeviceFake.screencap".format(patchers.__name__)):
                await device.screencap()

    @awaiter
    async def test_async_client_device_fail(self):
        with patch("androidtv.adb_manager.adb_manager_async.Client", patchers.ClientFakeFail):
            client = ClientAsync("host", "port")

            device = await client.device("serial")

            self.assertFalse(device)
