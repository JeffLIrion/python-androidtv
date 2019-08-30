from socket import error as socket_error

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


class AdbCommandsFake(object):
    """A fake of the ``adb.adb_commands.AdbCommands`` class."""

    def ConnectDevice(self):
        raise NotImplementedError

    def Shell(self, cmd):
        raise NotImplementedError


class ClientFake(object):
    """A fake of the ``adb_messenger.client.Client`` class."""

    def __init__(self, host, port):
        self._devices = []

    def devices(self):
        return self._devices

    def device(self, host):
        raise NotImplementedError


class DeviceFake(object):
    """A fake of the ``adb_messenger.device.Device`` class."""

    def __init__(self, host):
        self.host = host

    def get_serial_no(self):
        return self.host

    def shell(self, cmd):
        raise NotImplementedError


def ConnectDevice_success(self):
    return self


def ConnectDevice_fail(self):
    raise socket_error


def device_success(self, host):
    device = DeviceFake(host)
    self._devices.append(device)
    return device


def device_fail(self, host):
    self._devices = []
    return None


def shell_success(self, cmd):
    self.cmd = cmd

def patch_connect(success):
    if success:
        return patch('{}.AdbCommandsFake.ConnectDevice'.format(__name__), ConnectDevice_success), patch('{}.ClientFake.device'.format(__name__), device_success)
    return patch('{}.AdbCommandsFake.ConnectDevice'.format(__name__), return_value=None), patch('{}.ClientFake.device'.format(__name__), device_fail)


def patch_shell(response, error=False):
    def shell_success(self, cmd):
        self.cmd = cmd
        return response

    def shell_fail_python(self, cmd):
        self.cmd = cmd
        raise AttributeError

    def shell_fail_server(self, cmd):
        self.cmd = cmd
        raise ConnectionResetError

    if not error:
        return patch('{}.AdbCommandsFake.Shell'.format(__name__), shell_success), patch('{}.DeviceFake.shell'.format(__name__), shell_success)
    return patch('{}.AdbCommandsFake.Shell'.format(__name__), shell_fail_python), patch('{}.DeviceFake.shell'.format(__name__), shell_fail_server)


def adb_command_success(self, cmd):
    """Return ``cmd``."""
    return cmd


def connect_device_success(self, *args, **kwargs):
    """Return `self`, which will result in the ADB connection being interpreted as available."""
    return self


def connect_device_fail(self, *args, **kwargs):
    """Raise a socket error."""
    raise socket_error


def adb_shell_python_adb_error(self, cmd):
    """Raise an error that is among those caught for the Python ADB implementation."""
    raise AttributeError


def adb_shell_adb_server_error(self, cmd):
    """Raise an error that is among those caught for the ADB server implementation."""
    raise ConnectionResetError


class AdbAvailable(object):
    """A class that indicates the ADB connection is available."""

    def shell(self, cmd):
        """Send an ADB shell command (ADB server implementation)."""
        return cmd


class AdbUnavailable(object):
    """A class with ADB shell methods that raise errors."""

    def __bool__(self):
        """Return `False` to indicate that the ADB connection is unavailable."""
        return False

    def shell(self, cmd):
        """Raise an error that pertains to the Python ADB implementation."""
        raise ConnectionResetError


def patch_shell(response):
    def shell(self, cmd):
        self.shell_cmd = cmd
        return response

    return patch('androidtv.adb_helper.ADBPython.shell', shell)


PATCH_PYTHON_ADB_CONNECT_SUCCESS = patch(
    "adb.adb_commands.AdbCommands.ConnectDevice", connect_device_success
)
PATCH_PYTHON_ADB_COMMAND_SUCCESS = patch(
    "adb.adb_commands.AdbCommands.Shell", adb_command_success
)
PATCH_PYTHON_ADB_CONNECT_FAIL = patch(
    "adb.adb_commands.AdbCommands.ConnectDevice", connect_device_fail
)
PATCH_PYTHON_ADB_COMMAND_FAIL = patch(
    "adb.adb_commands.AdbCommands.Shell", adb_shell_python_adb_error
)
PATCH_PYTHON_ADB_COMMAND_NONE = patch(
    "adb.adb_commands.AdbCommands.Shell", return_value=None
)

PATCH_ADB_SERVER_CONNECT_SUCCESS = patch(
    "adb_messenger.client.Client.device", return_value=AdbAvailable()
)
PATCH_ADB_SERVER_AVAILABLE = patch(
    "androidtv.basetv.BaseTV.available", return_value=True
)
PATCH_ADB_SERVER_AVAILABLE2 = patch(
    "androidtv.adb_helper.ADBServer.available", return_value=True
)
PATCH_ADB_SERVER_UNAVAILABLE = patch(
    "androidtv.adb_helper.ADBServer.available", return_value=False
)
PATCH_ADB_SERVER_CONNECT_FAIL = patch(
    "adb_messenger.client.Client.device", return_value=False
)
PATCH_ADB_SERVER_COMMAND_FAIL = patch(
    "{}.AdbAvailable.shell".format(__name__), adb_shell_adb_server_error
)
PATCH_ADB_SERVER_COMMAND_NONE = patch(
    "{}.AdbAvailable.shell".format(__name__), return_value=None
)

