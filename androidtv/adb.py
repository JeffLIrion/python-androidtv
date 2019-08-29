"""Communicate with an Android TV or Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging
from socket import error as socket_error
import sys
import threading

from adb import adb_commands
from adb.sign_pythonrsa import PythonRSASigner
from adb_messenger.client import Client as AdbClient

_LOGGER = logging.getLogger(__name__)

if sys.version_info[0] > 2 and sys.version_info[1] > 1:
    LOCK_KWARGS = {'timeout': 3}
else:
    LOCK_KWARGS = {}
    FileNotFoundError = IOError  # pylint: disable=redefined-builtin


class ADBPython(object):
    """TODO."""

    def __init__(self, host, adbkey=''):
        """TODO."""
        self.host = host
        self.adbkey = adbkey
        self._adb = None

        # keep track of whether the ADB connection is intact
        self._available = False

        # use a lock to make sure that ADB commands don't overlap
        self._adb_lock = threading.Lock()

    @property
    def available(self):
        """Check whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        return bool(self._adb)

    def connect(self, always_log_errors=True):
        """Connect to an Android TV / Fire TV device.

        Parameters
        ----------
        always_log_errors : bool
            If True, errors will always be logged; otherwise, errors will only be logged on the first failed reconnect attempt

        Returns
        -------
        bool
            Whether or not the connection was successfully established and the device is available

        """
        self._adb_lock.acquire(**LOCK_KWARGS)  # pylint: disable=unexpected-keyword-arg

        # Make sure that we release the lock
        try:
            # Catch errors
            try:
                if self.adbkey:
                    # private key
                    with open(self.adbkey) as f:
                        priv = f.read()

                    # public key
                    try:
                        with open(self.adbkey + '.pub') as f:
                            pub = f.read()
                    except FileNotFoundError:
                        pub = ''

                    signer = PythonRSASigner(pub, priv)

                    # Connect to the device
                    self._adb = adb_commands.AdbCommands().ConnectDevice(serial=self.host, rsa_keys=[signer], default_timeout_ms=9000)
                else:
                    self._adb = adb_commands.AdbCommands().ConnectDevice(serial=self.host, default_timeout_ms=9000)

                # ADB connection successfully established
                self._available = True
                _LOGGER.debug("ADB connection to %s successfully established", self.host)

            except socket_error as serr:
                if self._available or always_log_errors:
                    if serr.strerror is None:
                        serr.strerror = "Timed out trying to connect to ADB device."
                    _LOGGER.warning("Couldn't connect to host %s, error: %s", self.host, serr.strerror)

                # ADB connection attempt failed
                self._adb = None
                self._available = False

            finally:
                return self._available

        finally:
            self._adb_lock.release()

    def shell(self, cmd):
        """Send an ADB command using the Python ADB implementation.

        Parameters
        ----------
        cmd : str
            The ADB command to be sent

        Returns
        -------
        str, None
            The response from the device, if there is a response

        """
        if not self.available:
            _LOGGER.debug("ADB command not sent to %s because python-adb connection is not established: %s", self.host, cmd)
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):  # pylint: disable=unexpected-keyword-arg
            _LOGGER.debug("Sending command to %s via python-adb: %s", self.host, cmd)
            try:
                return self._adb.Shell(cmd)
            finally:
                self._adb_lock.release()
        else:
            _LOGGER.debug("ADB command not sent to %s because python-adb lock not acquired: %s", self.host, cmd)

        return None


class ADBServer(object):
    """TODO."""

    def __init__(self, host, adb_server_ip='', adb_server_port=5037):
        """TODO."""
        self.host = host
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port
        self._adb_client = None
        self._adb_device = None

        # keep track of whether the ADB connection is intact
        self._available = False

        # use a lock to make sure that ADB commands don't overlap
        self._adb_lock = threading.Lock()

    @property
    def available(self):
        """Check whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        return bool(self._adb)

    def connect(self, always_log_errors=True):
        """Connect to an Android TV / Fire TV device.

        Parameters
        ----------
        always_log_errors : bool
            If True, errors will always be logged; otherwise, errors will only be logged on the first failed reconnect attempt

        Returns
        -------
        bool
            Whether or not the connection was successfully established and the device is available

        """
        self._adb_lock.acquire(**LOCK_KWARGS)  # pylint: disable=unexpected-keyword-arg

        # Make sure that we release the lock
        try:
            try:
                self._adb_client = AdbClient(host=self.adb_server_ip, port=self.adb_server_port)
                self._adb_device = self._adb_client.device(self.host)

                # ADB connection successfully established
                if self._adb_device:
                    _LOGGER.debug("ADB connection to %s via ADB server %s:%s successfully established", self.host, self.adb_server_ip, self.adb_server_port)
                    self._available = True

                # ADB connection attempt failed (without an exception)
                else:
                    if self._available or always_log_errors:
                        _LOGGER.warning("Couldn't connect to host %s via ADB server %s:%s", self.host, self.adb_server_ip, self.adb_server_port)
                    self._available = False

            except Exception as exc:  # noqa pylint: disable=broad-except
                if self._available or always_log_errors:
                    _LOGGER.warning("Couldn't connect to host %s via ADB server %s:%s, error: %s", self.host, self.adb_server_ip, self.adb_server_port, exc)

                # ADB connection attempt failed
                self._available = False

            finally:
                return self._available

        finally:
            self._adb_lock.release()

    def shell(self, cmd):
        """Send an ADB command using an ADB server.

        Parameters
        ----------
        cmd : str
            The ADB command to be sent

        Returns
        -------
        str, None
            The response from the device, if there is a response

        """
        if not self._available:
            _LOGGER.debug("ADB command not sent to %s via ADB server %s:%s because pure-python-adb connection is not established: %s", self.host, self.adb_server_ip, self.adb_server_port, cmd)
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):  # pylint: disable=unexpected-keyword-arg
            _LOGGER.debug("Sending command to %s via ADB server %s:%s: %s", self.host, self.adb_server_ip, self.adb_server_port, cmd)
            try:
                return self._adb_device.shell(cmd)
            finally:
                self._adb_lock.release()
        else:
            _LOGGER.debug("ADB command not sent to %s via ADB server %s:%s because pure-python-adb lock not acquired: %s", self.host, self.adb_server_ip, self.adb_server_port, cmd)

        return None

