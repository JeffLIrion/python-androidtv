"""Define patches used for androidtv tests."""

from unittest.mock import patch

try:
    from unittest.mock import AsyncMock
except ImportError:
    from unittest.mock import MagicMock

    class AsyncMock(MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)


KEY_PYTHON = "python"
KEY_SERVER = "server"

ADB_DEVICE_TCP_ASYNC_FAKE = "AdbDeviceTcpAsyncFake"
CLIENT_ASYNC_FAKE_SUCCESS = "ClientAsyncFakeSuccess"
CLIENT_ASYNC_FAKE_FAIL = "ClientAsyncFakeFail"
DEVICE_ASYNC_FAKE = "DeviceAsyncFake"


def async_patch(*args, **kwargs):
    return patch(*args, new_callable=AsyncMock, **kwargs)


class AdbDeviceTcpAsyncFake(object):
    """A fake of the `adb_shell.adb_device_async.AdbDeviceTcpAsync` class."""

    def __init__(self, *args, **kwargs):
        """Initialize a fake `adb_shell.adb_device_async.AdbDeviceTcpAsync` instance."""
        self.available = False

    async def close(self):
        """Close the socket connection."""
        self.available = False

    async def connect(self, *args, **kwargs):
        """Try to connect to a device."""
        raise NotImplementedError

    async def push(self, *args, **kwargs):
        """Push a file to the device."""

    async def pull(self, *args, **kwargs):
        """Pull a file from the device."""

    async def shell(self, cmd, *args, **kwargs):
        """Send an ADB shell command."""
        return None


class ClientAsyncFakeSuccess(object):
    """A fake of the `ppadb.client.Client` class when the connection and shell commands succeed."""

    def __init__(self, host="127.0.0.1", port=5037):
        """Initialize a `ClientAsyncFakeSuccess` instance."""
        self._devices = []

    async def device(self, serial):
        """Mock the `ClientAsync.device` method when the device is connected via ADB."""
        device = DeviceAsyncFake(serial)
        self._devices.append(device)
        return device


class ClientAsyncFakeFail(object):
    """A fake of the `ppadb.client.Client` class when the connection and shell commands fail."""

    def __init__(self, host="127.0.0.1", port=5037):
        """Initialize a `ClientAsyncFakeFail` instance."""
        self._devices = []

    async def device(self, serial):
        """Mock the `ClientAsync.device` method when the device is not connected via ADB."""
        self._devices = []


class DeviceAsyncFake(object):
    """A fake of the `ppadb.device.Device` class."""

    def __init__(self, host):
        """Initialize a `DeviceAsyncFake` instance."""
        self.host = host

    async def push(self, *args, **kwargs):
        """Push a file to the device."""

    async def pull(self, *args, **kwargs):
        """Pull a file from the device."""

    async def shell(self, cmd):
        """Send an ADB shell command."""
        raise NotImplementedError

    async def screencap(self):
        """Take a screencap."""
        raise NotImplementedError


def patch_connect(success):
    """Mock the `adb_shell.adb_device_async.AdbDeviceTcpAsync` and `ppadb.client.Client` classes."""

    async def connect_success_python(self, *args, **kwargs):
        """Mock the `AdbDeviceTcpAsyncFake.connect` method when it succeeds."""
        self.available = True

    async def connect_fail_python(self, *args, **kwargs):
        """Mock the `AdbDeviceTcpAsyncFake.connect` method when it fails."""
        raise OSError

    if success:
        return {KEY_PYTHON: patch("{}.{}.connect".format(__name__, ADB_DEVICE_TCP_ASYNC_FAKE), connect_success_python), KEY_SERVER: patch("androidtv.adb_manager.adb_manager_async.ClientAsync", ClientAsyncFakeSuccess)}
    return {KEY_PYTHON: patch("{}.{}.connect".format(__name__, ADB_DEVICE_TCP_ASYNC_FAKE), connect_fail_python), KEY_SERVER: patch("androidtv.adb_manager.adb_manager_async.ClientAsync", ClientAsyncFakeFail)}


def patch_shell(response=None, error=False):
    """Mock the `AdbDeviceTcpAsyncFake.shell` and `DeviceAsyncFake.shell` methods."""

    async def shell_success(self, cmd, *args, **kwargs):
        """Mock the `AdbDeviceTcpAsyncFake.shell` and `DeviceAsyncFake.shell` methods when they are successful."""
        self.shell_cmd = cmd
        return response

    async def shell_fail_python(self, cmd, *args, **kwargs):
        """Mock the `AdbDeviceTcpAsyncFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise AttributeError

    async def shell_fail_server(self, cmd):
        """Mock the `DeviceAsyncFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise ConnectionResetError

    if not error:
        return {KEY_PYTHON: patch("{}.{}.shell".format(__name__, ADB_DEVICE_TCP_ASYNC_FAKE), shell_success), KEY_SERVER: patch("{}.{}.shell".format(__name__, DEVICE_ASYNC_FAKE), shell_success)}
    return {KEY_PYTHON: patch("{}.{}.shell".format(__name__, ADB_DEVICE_TCP_ASYNC_FAKE), shell_fail_python), KEY_SERVER: patch("{}.{}.shell".format(__name__, DEVICE_ASYNC_FAKE), shell_fail_server)}


PATCH_PUSH = {KEY_PYTHON: async_patch("{}.{}.push".format(__name__, ADB_DEVICE_TCP_ASYNC_FAKE)), KEY_SERVER: async_patch("{}.{}.push".format(__name__, DEVICE_ASYNC_FAKE))}

PATCH_PULL = {KEY_PYTHON: async_patch("{}.{}.pull".format(__name__, ADB_DEVICE_TCP_ASYNC_FAKE)), KEY_SERVER: async_patch("{}.{}.pull".format(__name__, DEVICE_ASYNC_FAKE))}

PATCH_ADB_DEVICE_TCP = patch("androidtv.adb_manager.adb_manager_async.AdbDeviceTcpAsync", AdbDeviceTcpAsyncFake)


class CustomException(Exception):
    """A custom exception type."""


PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION = {KEY_PYTHON: async_patch("{}.{}.connect".format(__name__, ADB_DEVICE_TCP_ASYNC_FAKE), side_effect=CustomException), KEY_SERVER: async_patch("{}.{}.device".format(__name__, CLIENT_ASYNC_FAKE_SUCCESS), side_effect=CustomException)}
