import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, '..')

from androidtv.adb_manager.adb_manager_async import ClientAsync

from .async_wrapper import awaiter
from . import patchers


class TestAsyncClientDevice(unittest.TestCase):
    """Test"""

    @awaiter
    async def test_stuff(self):
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
