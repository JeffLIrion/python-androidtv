"""Tests for the ClientAsync and AdbDeviceUsbAsync classes."""

import unittest
from unittest.mock import patch

try:
    from adb_shell.transport.usb_transport import UsbTransport
except (ImportError, OSError):
    UsbTransport = None

from androidtv.adb_manager.adb_manager_async import AdbDeviceUsbAsync, ClientAsync

from .async_wrapper import awaiter
from . import patchers


class TestAsyncClientDevice(unittest.TestCase):
    """Test the ``ClientAsync`` and ``DeviceAsync`` classes defined in ``adb_manager_async.py``.

    These tests can be removed once true async support for using an ADB server is available.

    """

    @awaiter
    async def test_async_client_device(self):
        """Test the ClientAsync class."""
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
        """Test the ClientAsync class when it fails."""
        with patch("androidtv.adb_manager.adb_manager_async.Client", patchers.ClientFakeFail):
            client = ClientAsync("host", "port")

            device = await client.device("serial")

            self.assertFalse(device)


@unittest.skipIf(UsbTransport is None, "UsbTransport cannot be imported")
class TestAsyncUsb(unittest.TestCase):
    """Test the ``AdbDeviceUsbAsync`` class defined in ``adb_manager_async.py``.

    These tests can be removed once true async support for using a USB connection is available.

    """

    @awaiter
    async def test_async_usb(self):
        """Test the AdbDeviceUsbAsync class."""
        with patch("adb_shell.adb_device.UsbTransport.find_adb", return_value=UsbTransport("device", "setting")):
            device = AdbDeviceUsbAsync()

            self.assertFalse(device.available)

            with patch("androidtv.adb_manager.adb_manager_async.AdbDeviceUsb.connect") as connect:
                await device.connect()
                assert connect.called

            with patch("androidtv.adb_manager.adb_manager_async.AdbDeviceUsb.shell") as shell:
                await device.shell("test")
                assert shell.called

            with patch("androidtv.adb_manager.adb_manager_async.AdbDeviceUsb.push") as push:
                await device.push("local_path", "device_path")
                assert push.called

            with patch("androidtv.adb_manager.adb_manager_async.AdbDeviceUsb.pull") as pull:
                await device.pull("device_path", "local_path")
                assert pull.called

            with patch("androidtv.adb_manager.adb_manager_async.AdbDeviceUsb.close") as close:
                await device.close()
                assert close.called
