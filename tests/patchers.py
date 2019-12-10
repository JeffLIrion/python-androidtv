"""Define patches used for androidtv tests."""

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


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

    def shell(self, cmd):
        """Send an ADB shell command."""
        return None


class ClientFakeSuccess(object):
    """A fake of the `ppadb.client.Client` class when the connection and shell commands succeed."""

    def __init__(self, host="127.0.0.1", port=5037):
        """Initialize a `ClientFakeSuccess` instance."""
        self._devices = []

    def devices(self):
        """Get a list of the connected devices."""
        return self._devices

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

    def devices(self):
        """Get a list of the connected devices."""
        return self._devices

    def device(self, serial):
        """Mock the `Client.device` method when the device is not connected via ADB."""
        self._devices = []


class DeviceFake(object):
    """A fake of the `ppadb.device.Device` class."""

    def __init__(self, host):
        """Initialize a `DeviceFake` instance."""
        self.host = host

    def get_serial_no(self):
        """Get the serial number for the device (IP:PORT)."""
        return self.host

    def push(self, *args, **kwargs):
        """Push a file to the device."""

    def pull(self, *args, **kwargs):
        """Pull a file from the device."""

    def shell(self, cmd):
        """Send an ADB shell command."""
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
        return {"python": patch("{}.AdbDeviceTcpFake.connect".format(__name__), connect_success_python), "server": patch("androidtv.adb_manager.Client", ClientFakeSuccess)}
    return {"python": patch("{}.AdbDeviceTcpFake.connect".format(__name__), connect_fail_python), "server": patch("androidtv.adb_manager.Client", ClientFakeFail)}


def patch_shell(response=None, error=False):
    """Mock the `AdbDeviceTcpFake.shell` and `DeviceFake.shell` methods."""

    def shell_success(self, cmd):
        """Mock the `AdbDeviceTcpFake.shell` and `DeviceFake.shell` methods when they are successful."""
        self.shell_cmd = cmd
        return response

    def shell_fail_python(self, cmd):
        """Mock the `AdbDeviceTcpFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise AttributeError

    def shell_fail_server(self, cmd):
        """Mock the `DeviceFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise ConnectionResetError

    if not error:
        return {"python": patch("{}.AdbDeviceTcpFake.shell".format(__name__), shell_success), "server": patch("{}.DeviceFake.shell".format(__name__), shell_success)}
    return {"python": patch("{}.AdbDeviceTcpFake.shell".format(__name__), shell_fail_python), "server": patch("{}.DeviceFake.shell".format(__name__), shell_fail_server)}


PATCH_PUSH = {"python": patch("{}.AdbDeviceTcpFake.push".format(__name__)), "server": patch("{}.DeviceFake.push".format(__name__))}

PATCH_PULL = {"python": patch("{}.AdbDeviceTcpFake.pull".format(__name__)), "server": patch("{}.DeviceFake.pull".format(__name__))}

PATCH_ADB_DEVICE_TCP = patch("androidtv.adb_manager.AdbDeviceTcp", AdbDeviceTcpFake)


class CustomException(Exception):
    """A custom exception type."""


PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION = {"python": patch("{}.AdbDeviceTcpFake.connect".format(__name__), side_effect=CustomException), "server": patch("{}.ClientFakeSuccess.devices".format(__name__), side_effect=CustomException)}
