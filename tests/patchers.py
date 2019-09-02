from socket import error as socket_error

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


class AdbCommandsFake(object):
    """A fake of the `adb.adb_commands.AdbCommands` class."""

    def ConnectDevice(self, *args, **kwargs):
        """Try to connect to a device."""
        raise NotImplementedError

    def Shell(self, cmd):
        """Send an ADB shell command."""
        raise NotImplementedError


class AdbCommandsFakeSuccess(AdbCommandsFake):
    """A fake of the `adb.adb_commands.AdbCommands` class when the connection attempt succeeds."""

    def ConnectDevice(self, *args, **kwargs):
        """Successfully connect to a device."""
        return self


class AdbCommandsFakeFail(AdbCommandsFake):
    """A fake of the `adb.adb_commands.AdbCommands` class when the connection attempt fails."""

    def ConnectDevice(self, *args, **kwargs):
        """Fail to connect to a device."""
        raise socket_error


class ClientFakeSuccess(object):
    """A fake of the `adb_messenger.client.Client` class when the connection and shell commands succeed."""

    def __init__(self, host='127.0.0.1', port=5037):
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
    """A fake of the `adb_messenger.client.Client` class when the connection and shell commands fail."""

    def __init__(self, host='127.0.0.1', port=5037):
        self._devices = []

    def devices(self):
        """Get a list of the connected devices."""
        return self._devices

    def device(self, serial):
        """Mock the `Client.device` method when the device is not connected via ADB."""
        self._devices = []
        return None


class DeviceFake(object):
    """A fake of the `adb_messenger.device.Device` class."""

    def __init__(self, host):
        self.host = host

    def get_serial_no(self):
        """Get the serial number for the device (IP:PORT)."""
        return self.host

    def shell(self, cmd):
        """Send an ADB shell command."""
        raise NotImplementedError


def patch_connect(success):
    """Mock the `adb.adb_commands.AdbCommands` and `adb_messenger.client.Client` classes."""

    if success:
        return {'python': patch('androidtv.adb_manager.AdbCommands', AdbCommandsFakeSuccess), 'server': patch('androidtv.adb_manager.Client', ClientFakeSuccess)}
    return {'python': patch('androidtv.adb_manager.AdbCommands', AdbCommandsFakeFail), 'server': patch('androidtv.adb_manager.Client', ClientFakeFail)}


def patch_shell(response=None, error=False):
    """Mock the `AdbCommandsFakeSuccess.Shell` / `AdbCommandsFakeFail.Shell` and `DeviceFake.shell` methods."""

    def shell_success(self, cmd):
        """Mock the `AdbCommandsFake.Shell` and `DeviceFake.shell` methods when they are successful."""
        self.shell_cmd = cmd
        return response

    def shell_fail_python(self, cmd):
        """Mock the `AdbCommandsFake.Shell` method when it fails."""
        self.shell_cmd = cmd
        raise AttributeError

    def shell_fail_server(self, cmd):
        """Mock the `DeviceFake.shell` method when it fails."""
        self.shell_cmd = cmd
        raise ConnectionResetError

    if not error:
        return {'python': patch('{}.AdbCommandsFake.Shell'.format(__name__), shell_success), 'server': patch('{}.DeviceFake.shell'.format(__name__), shell_success)}
    return {'python': patch('{}.AdbCommandsFake.Shell'.format(__name__), shell_fail_python), 'server': patch('{}.DeviceFake.shell'.format(__name__), shell_fail_server)}
