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


class AdbDeviceTcpFake(object):
    """A fake of the `aio_adb_shell.adb_device.AdbDeviceTcp` class."""

    def __init__(self, *args, **kwargs):
        """Initialize a fake `adb_shell.adb_device.AdbDeviceTcp` instance."""
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


def patch_connect(success):
    """Mock the `adb_shell.adb_device.AdbDeviceTcp` class."""

    async def connect_success_python(self, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.connect` method when it succeeds."""
        self.available = True

    async def connect_fail_python(self, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.connect` method when it fails."""
        raise OSError

    if success:
        return {KEY_PYTHON: patch("{}.AdbDeviceTcpFake.connect".format(__name__), connect_success_python)}
    return {KEY_PYTHON: patch("{}.AdbDeviceTcpFake.connect".format(__name__), connect_fail_python)}


def patch_shell(response=None, error=False):
    """Mock the `AdbDeviceTcpFake.shell` and `DeviceFake.shell` methods."""

    async def shell_success(self, cmd, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.shell` and `DeviceFake.shell` methods when they are successful."""
        self.shell_cmd = cmd
        return response

    async def shell_fail_python(self, cmd, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise AttributeError

    if not error:
        return {KEY_PYTHON: patch("{}.AdbDeviceTcpFake.shell".format(__name__), shell_success)}
    return {KEY_PYTHON: patch("{}.AdbDeviceTcpFake.shell".format(__name__), shell_fail_python)}


PATCH_PUSH = {KEY_PYTHON: patch("{}.AdbDeviceTcpFake.push".format(__name__), new_callable=AsyncMock)}

PATCH_PULL = {KEY_PYTHON: patch("{}.AdbDeviceTcpFake.pull".format(__name__), new_callable=AsyncMock)}

PATCH_ADB_DEVICE_TCP = patch("aio_androidtv.adb_manager.AdbDeviceTcp", AdbDeviceTcpFake)


class CustomException(Exception):
    """A custom exception type."""


PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION = {KEY_PYTHON: patch("{}.AdbDeviceTcpFake.connect".format(__name__), side_effect=CustomException)}
