"""Define patches used for androidtv tests."""

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


KEY_PYTHON = "python"
KEY_PYTHON_USB = "python_usb"
KEY_SERVER = "server"

ADB_DEVICE_TCP_FAKE = "AdbDeviceTcpFake"
CLIENT_FAKE_SUCCESS = "ClientFakeSuccess"
CLIENT_FAKE_FAIL = "ClientFakeFail"
DEVICE_FAKE = "DeviceFake"

class AdbDeviceTcpFake(object):
    """A fake of the `adb_shell.adb_device.AdbDeviceTcp` class."""

    def __init__(self, *args, **kwargs):
        """Initialize a fake `adb_shell.adb_device.AdbDeviceTcp` instance."""
        self.available = False

    def close(self):
        """Close the socket connection."""
        self.available = False

    def connect(self, *args, **kwargs):
        """Try to connect to a device."""
        raise NotImplementedError

    def push(self, *args, **kwargs):
        """Push a file to the device."""

    def pull(self, *args, **kwargs):
        """Pull a file from the device."""

    def shell(self, cmd, *args, **kwargs):
        """Send an ADB shell command."""
        return None


class ClientFakeSuccess(object):
    """A fake of the `ppadb.client.Client` class when the connection and shell commands succeed."""

    def __init__(self, host="127.0.0.1", port=5037):
        """Initialize a `ClientFakeSuccess` instance."""
        self._devices = []

    def device(self, serial):
        """Mock the `Client.device` method when the device is connected via ADB."""
        device = DeviceFake(serial)
        self._devices.append(device)
        return device


class ClientFakeFail(object):
    """A fake of the `ppadb.client.Client` class when the connection and shell commands fail."""

    def __init__(self, host="127.0.0.1", port=5037):
        """Initialize a `ClientFakeFail` instance."""
        self._devices = []

    def device(self, serial):
        """Mock the `Client.device` method when the device is not connected via ADB."""
        self._devices = []


class DeviceFake(object):
    """A fake of the `ppadb.device.Device` class."""

    def __init__(self, host):
        """Initialize a `DeviceFake` instance."""
        self.host = host

    def push(self, *args, **kwargs):
        """Push a file to the device."""

    def pull(self, *args, **kwargs):
        """Pull a file from the device."""

    def shell(self, cmd):
        """Send an ADB shell command."""
        raise NotImplementedError

    def screencap(self):
        """Take a screencap."""
        raise NotImplementedError


def patch_connect(success):
    """Mock the `adb_shell.adb_device.AdbDeviceTcp` and `ppadb.client.Client` classes."""

    def connect_success_python(self, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.connect` method when it succeeds."""
        self.available = True

    def connect_fail_python(self, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.connect` method when it fails."""
        raise OSError

    if success:
        return {KEY_PYTHON: patch("{}.{}.connect".format(__name__, ADB_DEVICE_TCP_FAKE), connect_success_python), KEY_SERVER: patch("androidtv.adb_manager.adb_manager_sync.Client", ClientFakeSuccess)}
    return {KEY_PYTHON: patch("{}.{}.connect".format(__name__, ADB_DEVICE_TCP_FAKE), connect_fail_python), KEY_SERVER: patch("androidtv.adb_manager.adb_manager_sync.Client", ClientFakeFail)}


def patch_shell(response=None, error=False):
    """Mock the `AdbDeviceTcpFake.shell` and `DeviceFake.shell` methods."""

    def shell_success(self, cmd, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.shell` and `DeviceFake.shell` methods when they are successful."""
        self.shell_cmd = cmd
        return response

    def shell_fail_python(self, cmd, *args, **kwargs):
        """Mock the `AdbDeviceTcpFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise AttributeError

    def shell_fail_server(self, cmd):
        """Mock the `DeviceFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise ConnectionResetError

    if not error:
        return {KEY_PYTHON: patch("{}.{}.shell".format(__name__, ADB_DEVICE_TCP_FAKE), shell_success), KEY_SERVER: patch("{}.{}.shell".format(__name__, DEVICE_FAKE), shell_success)}
    return {KEY_PYTHON: patch("{}.{}.shell".format(__name__, ADB_DEVICE_TCP_FAKE), shell_fail_python), KEY_SERVER: patch("{}.{}.shell".format(__name__, DEVICE_FAKE), shell_fail_server)}


PATCH_PUSH = {KEY_PYTHON: patch("{}.{}.push".format(__name__, ADB_DEVICE_TCP_FAKE)), KEY_SERVER: patch("{}.{}.push".format(__name__, DEVICE_FAKE))}

PATCH_PULL = {KEY_PYTHON: patch("{}.{}.pull".format(__name__, ADB_DEVICE_TCP_FAKE)), KEY_SERVER: patch("{}.{}.pull".format(__name__, DEVICE_FAKE))}

PATCH_ADB_DEVICE_TCP = patch("androidtv.adb_manager.adb_manager_sync.AdbDeviceTcp", AdbDeviceTcpFake)

PATCH_ADB_DEVICE_USB = patch("androidtv.adb_manager.adb_manager_sync.AdbDeviceUsb", AdbDeviceTcpFake)

PATCH_ADB_SERVER_RUNTIME_ERROR = patch("{}.{}.device".format(__name__, CLIENT_FAKE_SUCCESS), side_effect=RuntimeError)


class CustomException(Exception):
    """A custom exception type."""


PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION = {KEY_PYTHON: patch("{}.{}.connect".format(__name__, ADB_DEVICE_TCP_FAKE), side_effect=CustomException), KEY_SERVER: patch("{}.{}.device".format(__name__, CLIENT_FAKE_SUCCESS), side_effect=CustomException)}


def patch_calls(obj, wraps):
    """Patch a method call without changing its behavior.

    Parameters
    ----------
    obj
        The object whose method will be patched (i.e., `self`)
    wraps
        The method that is being patched (i.e., `self.method`)

    Returns
    -------
    The patched method

    """
    return patch.object(type(obj), wraps.__name__.split()[-1], wraps=wraps)
