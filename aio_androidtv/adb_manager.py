"""Classes to manage ADB connections.

* :py:class:`ADBPython` utilizes a Python implementation of the ADB protocol.

"""


import asyncio
from contextlib import asynccontextmanager
import logging

from aio_adb_shell.adb_device import AdbDeviceTcp
from aio_adb_shell.auth.sign_pythonrsa import PythonRSASigner

from .constants import DEFAULT_AUTH_TIMEOUT_S
from .exceptions import LockNotAcquiredException

_LOGGER = logging.getLogger(__name__)

#: Default timeout for acquiring the async lock that protects ADB commands
DEFAULT_TIMEOUT = 3.0


@asynccontextmanager
async def _acquire(lock, timeout=DEFAULT_TIMEOUT):
    """Handle acquisition and release of an ``asyncio.Lock`` object with a timeout.

    Parameters
    ----------
    lock : asyncio.Lock
        The lock that we will try to acquire
    timeout : float
        The timeout in seconds

    Yields
    ------
    acquired : bool
        Whether or not the lock was acquired

    Raises
    ------
    LockNotAcquiredException
        Raised if the lock was not acquired

    """
    try:
        acquired = False
        try:
            acquired = await asyncio.wait_for(lock.acquire(), timeout)
            if not acquired:
                raise LockNotAcquiredException
            yield acquired

        except asyncio.TimeoutError:
            raise LockNotAcquiredException

    finally:
        if acquired:
            lock.release()


class ADBPython(object):
    """A manager for ADB connections that uses a Python implementation of the ADB protocol.

    Parameters
    ----------
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication

    """
    def __init__(self, host, port, adbkey=''):
        self.host = host
        self.port = int(port)
        self.adbkey = adbkey
        self._adb = AdbDeviceTcp(host=self.host, port=self.port, default_timeout_s=9., banner=b'aio-androidtv')

        # keep track of whether the ADB connection is intact
        self._available = False

        # use a lock to make sure that ADB commands don't overlap
        self._adb_lock = asyncio.Lock()

    @property
    def available(self):
        """Check whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        return self._adb.available

    async def close(self):
        """Close the ADB socket connection.

        """
        await self._adb.close()

    async def connect(self, always_log_errors=True, auth_timeout_s=DEFAULT_AUTH_TIMEOUT_S):
        """Connect to an Android TV / Fire TV device.

        Parameters
        ----------
        always_log_errors : bool
            If True, errors will always be logged; otherwise, errors will only be logged on the first failed reconnect attempt
        auth_timeout_s : float
            Authentication timeout (in seconds)

        Returns
        -------
        bool
            Whether or not the connection was successfully established and the device is available

        """
        try:
            async with _acquire(self._adb_lock):
                # Catch exceptions
                try:
                    # Connect with authentication
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

                        await self._adb.connect(rsa_keys=[signer], auth_timeout_s=auth_timeout_s)

                    # Connect without authentication
                    else:
                        await self._adb.connect(auth_timeout_s=auth_timeout_s)

                    # ADB connection successfully established
                    _LOGGER.debug("ADB connection to %s:%d successfully established", self.host, self.port)
                    self._available = True
                    return True

                except OSError as exc:
                    if self._available or always_log_errors:
                        if exc.strerror is None:
                            exc.strerror = "Timed out trying to connect to ADB device."
                        _LOGGER.warning("Couldn't connect to %s:%d.  %s: %s", self.host, self.port, exc.__class__.__name__, exc.strerror)

                    # ADB connection attempt failed
                    await self.close()
                    self._available = False
                    return False

                except Exception as exc:  # pylint: disable=broad-except
                    if self._available or always_log_errors:
                        _LOGGER.warning("Couldn't connect to %s:%d.  %s: %s", self.host, self.port, exc.__class__.__name__, exc)

                    # ADB connection attempt failed
                    await self.close()
                    self._available = False
                    return False

        except LockNotAcquiredException:
            _LOGGER.warning("Couldn't connect to %s:%d because adb-shell lock not acquired.", self.host, self.port)
            await self.close()
            self._available = False
            return False

    async def pull(self, local_path, device_path):
        """Pull a file from the device using the Python ADB implementation.

        Parameters
        ----------
        local_path : str
            The path where the file will be saved
        device_path : str
            The file on the device that will be pulled

        """
        if not self.available:
            _LOGGER.debug("ADB command not sent to %s:%d because adb-shell connection is not established: pull(%s, %s)", self.host, self.port, local_path, device_path)
            return

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Sending command to %s:%d via adb-shell: pull(%s, %s)", self.host, self.port, local_path, device_path)
            await self._adb.pull(device_path, local_path)
            return

    async def push(self, local_path, device_path):
        """Push a file to the device using the Python ADB implementation.

        Parameters
        ----------
        local_path : str
            The file that will be pushed to the device
        device_path : str
            The path where the file will be saved on the device

        """
        if not self.available:
            _LOGGER.debug("ADB command not sent to %s:%d because adb-shell connection is not established: push(%s, %s)", self.host, self.port, local_path, device_path)
            return

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Sending command to %s:%d via adb-shell: push(%s, %s)", self.host, self.port, local_path, device_path)
            await self._adb.push(local_path, device_path)
            return

    async def screencap(self):
        """Take a screenshot using the Python ADB implementation.

        Returns
        -------
        bytes
            The screencap as a binary .png image

        """
        if not self.available:
            _LOGGER.debug("ADB screencap not taken from %s:%d because adb-shell connection is not established", self.host, self.port)
            return None

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Taking screencap from %s:%d via adb-shell", self.host, self.port)
            result = await self._adb.shell("screencap -p", decode=False)
            if result[5:6] == b"\r":
                return result.replace(b"\r\n", b"\n")
            return result

    async def shell(self, cmd):
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
            _LOGGER.debug("ADB command not sent to %s:%d because adb-shell connection is not established: %s", self.host, self.port, cmd)
            return None

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Sending command to %s:%d via adb-shell: %s", self.host, self.port, cmd)
            return await self._adb.shell(cmd)
