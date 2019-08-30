import functools
import logging
from socket import error as socket_error
import sys
import unittest

try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch


sys.path.insert(0, '..')

from androidtv import setup
from androidtv.constants import APPS, KEYS, STATE_IDLE, STATE_OFF, STATE_PAUSED, STATE_PLAYING, STATE_STANDBY


_LOGGER = logging.getLogger(__name__)


class MediaPlayerDevice(object):
    @staticmethod
    def schedule_update_ha_state():
        raise NotImplementedError


# =========================================================================== #
#                                                                             #
#                               media_player.py                               #
#                                                                             #
# =========================================================================== #


# Translate from `AndroidTV` / `FireTV` reported state to HA state.
ANDROIDTV_STATES = {
    "off": STATE_OFF,
    "idle": STATE_IDLE,
    "standby": STATE_STANDBY,
    "playing": STATE_PLAYING,
    "paused": STATE_PAUSED,
}


def adb_decorator(override_available=False):
    """Send an ADB command if the device is available and catch exceptions."""

    def _adb_decorator(func):
        """Wait if previous ADB commands haven't finished."""

        @functools.wraps(func)
        def _adb_exception_catcher(self, *args, **kwargs):
            # If the device is unavailable, don't do anything
            if not self.available and not override_available:
                return None

            try:
                return func(self, *args, **kwargs)
            except self.exceptions as err:
                _LOGGER.error(
                    "Failed to execute an ADB command. ADB connection re-"
                    "establishing attempt in the next update. Error: %s",
                    err,
                )
                self._available = False  # pylint: disable=protected-access
                return None

        return _adb_exception_catcher

    return _adb_decorator


class ADBDevice(MediaPlayerDevice):
    """Representation of an Android TV or Fire TV device."""

    def __init__(self, aftv, name, apps, turn_on_command, turn_off_command):
        """Initialize the Android TV / Fire TV device."""
        self.aftv = aftv
        self._name = name
        self._apps = APPS.copy()
        self._apps.update(apps)
        self._keys = KEYS

        self._device_properties = self.aftv.device_properties
        self._unique_id = self._device_properties.get("serialno")

        self.turn_on_command = turn_on_command
        self.turn_off_command = turn_off_command

        # ADB exceptions to catch
        if not self.aftv.adb_server_ip:
            # Using "python-adb" (Python ADB implementation)
            from adb.adb_protocol import (
                InvalidChecksumError,
                InvalidCommandError,
                InvalidResponseError,
            )
            from adb.usb_exceptions import TcpTimeoutException

            self.exceptions = (
                AttributeError,
                BrokenPipeError,
                TypeError,
                ValueError,
                InvalidChecksumError,
                InvalidCommandError,
                InvalidResponseError,
                TcpTimeoutException,
            )
        else:
            # Using "pure-python-adb" (communicate with ADB server)
            self.exceptions = (ConnectionResetError, RuntimeError)

        # Property attributes
        self._adb_response = None
        self._available = self.aftv.available
        self._current_app = None
        self._state = None

    @property
    def available(self):
        """Return whether or not the ADB connection is valid."""
        return self._available

    @property
    def state(self):
        """Return the state of the player."""
        return self._state

    @adb_decorator()
    def adb_command(self, cmd):
        """Send an ADB command to an Android TV / Fire TV device."""
        key = self._keys.get(cmd)
        if key:
            self.aftv.adb_shell("input keyevent {}".format(key))
            self._adb_response = None
            self.schedule_update_ha_state()
            return

        if cmd == "GET_PROPERTIES":
            self._adb_response = str(self.aftv.get_properties_dict())
            self.schedule_update_ha_state()
            return self._adb_response

        response = self.aftv.adb_shell(cmd)
        if isinstance(response, str) and response.strip():
            self._adb_response = response.strip()
        else:
            self._adb_response = None

        self.schedule_update_ha_state()
        return self._adb_response


class AndroidTVDevice(ADBDevice):
    """Representation of an Android TV device."""

    def __init__(self, aftv, name, apps, turn_on_command, turn_off_command):
        """Initialize the Android TV device."""
        super().__init__(aftv, name, apps, turn_on_command, turn_off_command)

        self._device = None
        self._is_volume_muted = None
        self._volume_level = None

    @adb_decorator(override_available=True)
    def update(self):
        """Update the device state and, if necessary, re-connect."""
        # Check if device is disconnected.
        if not self._available:
            # Try to connect
            self._available = self.aftv.connect(always_log_errors=False)

            # To be safe, wait until the next update to run ADB commands if
            # using the Python ADB implementation.
            if not self.aftv.adb_server_ip:
                return

        # If the ADB connection is not intact, don't update.
        if not self._available:
            return

        # Get the updated state and attributes.
        state, self._current_app, self._device, self._is_volume_muted, self._volume_level = (
            self.aftv.update()
        )

        self._state = ANDROIDTV_STATES.get(state)
        if self._state is None:
            self._available = False


class FireTVDevice(ADBDevice):
    """Representation of a Fire TV device."""

    def __init__(
        self, aftv, name, apps, get_sources, turn_on_command, turn_off_command
    ):
        """Initialize the Fire TV device."""
        super().__init__(aftv, name, apps, turn_on_command, turn_off_command)

        self._get_sources = get_sources
        self._running_apps = None

    @adb_decorator(override_available=True)
    def update(self):
        """Update the device state and, if necessary, re-connect."""
        # Check if device is disconnected.
        if not self._available:
            # Try to connect
            self._available = self.aftv.connect(always_log_errors=False)

            # To be safe, wait until the next update to run ADB commands if
            # using the Python ADB implementation.
            if not self.aftv.adb_server_ip:
                return

        # If the ADB connection is not intact, don't update.
        if not self._available:
            return

        # Get the `state`, `current_app`, and `running_apps`.
        state, self._current_app, self._running_apps = self.aftv.update(
            self._get_sources
        )

        self._state = ANDROIDTV_STATES.get(state)
        if self._state is None:
            self._available = False


# =========================================================================== #
#                                                                             #
#                            test_media_player.py                             #
#                                                                             #
# =========================================================================== #


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
        return ""


class AdbUnavailable(object):
    """A class with ADB shell methods that raise errors."""

    def __bool__(self):
        """Return `False` to indicate that the ADB connection is unavailable."""
        return False

    def shell(self, cmd):
        """Raise an error that pertains to the Python ADB implementation."""
        raise ConnectionResetError


PATCH_PYTHON_ADB_CONNECT_SUCCESS = patch(
    "adb.adb_commands.AdbCommands.ConnectDevice", connect_device_success
)
PATCH_PYTHON_ADB_COMMAND_SUCCESS = patch(
    "adb.adb_commands.AdbCommands.Shell", return_value=""
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
PATCH_ADB_SERVER_CONNECT_FAIL = patch(
    "adb_messenger.client.Client.device", return_value=AdbUnavailable()
)
PATCH_ADB_SERVER_COMMAND_FAIL = patch(
    "{}.AdbAvailable.shell".format(__name__), adb_shell_adb_server_error
)
PATCH_ADB_SERVER_COMMAND_NONE = patch(
    "{}.AdbAvailable.shell".format(__name__), return_value=None
)


@unittest.skipIf(sys.version_info.major == 2, "Test requires Python 3")
class TestAndroidTVPythonImplementation(unittest.TestCase):
    """Test the androidtv media player for an Android TV device."""

    def setUp(self):
        """Set up an `AndroidTVDevice` media player."""
        with PATCH_PYTHON_ADB_CONNECT_SUCCESS, PATCH_PYTHON_ADB_COMMAND_SUCCESS:
            aftv = setup("IP:PORT", device_class="androidtv")
            self.aftv = AndroidTVDevice(aftv, "Fake Android TV", {}, None, None)

    def test_reconnect(self):
        """Test that the error and reconnection attempts are logged correctly.

        "Handles device/service unavailable. Log a warning once when
        unavailable, log once when reconnected."

        https://developers.home-assistant.io/docs/en/integration_quality_scale_index.html
        """
        with self.assertLogs(level=logging.WARNING) as logs:
            with PATCH_PYTHON_ADB_CONNECT_FAIL, PATCH_PYTHON_ADB_COMMAND_FAIL:
                for _ in range(5):
                    self.aftv.update()
                    self.assertFalse(self.aftv.available)
                    self.assertIsNone(self.aftv.state)

        assert len(logs.output) == 2
        assert logs.output[0].startswith("ERROR")
        assert logs.output[1].startswith("WARNING")

        with self.assertLogs(level=logging.DEBUG) as logs:
            with PATCH_PYTHON_ADB_CONNECT_SUCCESS, PATCH_PYTHON_ADB_COMMAND_SUCCESS:
                # Update 1 will reconnect
                self.aftv.update()
                self.assertTrue(self.aftv.available)

                # Update 2 will update the state
                self.aftv.update()
                self.assertTrue(self.aftv.available)
                self.assertIsNotNone(self.aftv.state)

        assert (
            "ADB connection to {} successfully established".format(self.aftv.aftv.host)
            in logs.output[0]
        )

    def test_adb_shell_returns_none(self):
        """Test the case that the ADB shell command returns `None`.

        The state should be `None` and the device should be unavailable.
        """
        with PATCH_PYTHON_ADB_COMMAND_NONE:
            self.aftv.update()
            self.assertFalse(self.aftv.available)
            self.assertIsNone(self.aftv.state)

        with PATCH_PYTHON_ADB_CONNECT_SUCCESS, PATCH_PYTHON_ADB_COMMAND_SUCCESS:
            # Update 1 will reconnect
            self.aftv.update()
            self.assertTrue(self.aftv.available)

            # Update 2 will update the state
            self.aftv.update()
            self.assertTrue(self.aftv.available)
            self.assertIsNotNone(self.aftv.state)


@unittest.skipIf(sys.version_info.major == 2, "Test requires Python 3")
class TestAndroidTVServerImplementation(unittest.TestCase):
    """Test the androidtv media player for an Android TV device."""

    def setUp(self):
        """Set up an `AndroidTVDevice` media player."""
        with PATCH_ADB_SERVER_CONNECT_SUCCESS, PATCH_ADB_SERVER_AVAILABLE:
            aftv = setup(
                "IP:PORT", adb_server_ip="ADB_SERVER_IP", device_class="androidtv"
            )
            self.aftv = AndroidTVDevice(aftv, "Fake Android TV", {}, None, None)

    def test_reconnect(self):
        """Test that the error and reconnection attempts are logged correctly.

        "Handles device/service unavailable. Log a warning once when
        unavailable, log once when reconnected."

        https://developers.home-assistant.io/docs/en/integration_quality_scale_index.html
        """
        with self.assertLogs(level=logging.WARNING) as logs:
            with PATCH_ADB_SERVER_CONNECT_FAIL, PATCH_ADB_SERVER_COMMAND_FAIL:
                for _ in range(5):
                    self.aftv.update()
                    self.assertFalse(self.aftv.available)
                    self.assertIsNone(self.aftv.state)

        assert len(logs.output) == 2
        assert logs.output[0].startswith("ERROR")
        assert logs.output[1].startswith("WARNING")

        with self.assertLogs(level=logging.DEBUG) as logs:
            with PATCH_ADB_SERVER_CONNECT_SUCCESS:
                self.aftv.update()
                self.assertTrue(self.aftv.available)
                self.assertIsNotNone(self.aftv.state)

        assert (
            "ADB connection to {} via ADB server {}:{} successfully established".format(
                self.aftv.aftv.host,
                self.aftv.aftv.adb_server_ip,
                self.aftv.aftv.adb_server_port,
            )
            in logs.output[0]
        )

    def test_adb_shell_returns_none(self):
        """Test the case that the ADB shell command returns `None`.

        The state should be `None` and the device should be unavailable.
        """
        with PATCH_ADB_SERVER_COMMAND_NONE:
            self.aftv.update()
            self.assertFalse(self.aftv.available)
            self.assertIsNone(self.aftv.state)

        with PATCH_ADB_SERVER_CONNECT_SUCCESS:
            self.aftv.update()
            self.assertTrue(self.aftv.available)
            self.assertIsNotNone(self.aftv.state)


@unittest.skipIf(sys.version_info.major == 2, "Test requires Python 3")
class TestFireTVPythonImplementation(TestAndroidTVPythonImplementation):
    """Test the androidtv media player for a Fire TV device."""

    def setUp(self):
        """Set up a `FireTVDevice` media player."""
        with PATCH_PYTHON_ADB_CONNECT_SUCCESS, PATCH_PYTHON_ADB_COMMAND_SUCCESS:
            aftv = setup("IP:PORT", device_class="firetv")
            self.aftv = FireTVDevice(aftv, "Fake Fire TV", {}, True, None, None)


@unittest.skipIf(sys.version_info.major == 2, "Test requires Python 3")
class TestFireTVServerImplementation(TestAndroidTVServerImplementation):
    """Test the androidtv media player for a Fire TV device."""

    def setUp(self):
        """Set up a `FireTVDevice` media player."""
        with PATCH_ADB_SERVER_CONNECT_SUCCESS, PATCH_ADB_SERVER_AVAILABLE:
            aftv = setup(
                "IP:PORT", adb_server_ip="ADB_SERVER_IP", device_class="firetv"
            )
            self.aftv = FireTVDevice(aftv, "Fake Fire TV", {}, True, None, None)
