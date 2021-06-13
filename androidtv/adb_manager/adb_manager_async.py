"""Classes to manage ADB connections.

* :py:class:`ADBPythonAsync` utilizes a Python implementation of the ADB protocol.
* :py:class:`ADBServerAsync` utilizes an ADB server to communicate with the device.

"""


import asyncio
from contextlib import asynccontextmanager
import logging

from adb_shell.adb_device_async import AdbDeviceTcpAsync
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import aiofiles
from ppadb.client import Client

from ..constants import DEFAULT_ADB_TIMEOUT_S, DEFAULT_AUTH_TIMEOUT_S, DEFAULT_LOCK_TIMEOUT_S
from ..exceptions import LockNotAcquiredException

_LOGGER = logging.getLogger(__name__)


class DeviceAsync:
    """An async wrapper for the pure-python-adb ``Device`` class."""
    def __init__(self, device):
        self._device = device

    async def pull(self, device_path, local_path):
        """Download a file."""
        return await asyncio.get_running_loop().run_in_executor(None, self._device.pull, device_path, local_path)

    async def push(self, local_path, device_path):
        """Upload a file."""
        return await asyncio.get_running_loop().run_in_executor(None, self._device.push, local_path, device_path)

    async def screencap(self):
        """Take a screencap."""
        return await asyncio.get_running_loop().run_in_executor(None, self._device.screencap)

    async def shell(self, cmd):
        """Send a shell command."""
        return await asyncio.get_running_loop().run_in_executor(None, self._device.shell, cmd)


# pylint: disable=too-few-public-methods
class ClientAsync:
    """An async wrapper for the pure-python-adb ``Client`` class."""
    def __init__(self, host, port):
        self._client = Client(host, port)

    async def device(self, serial):
        """Get a ``DeviceAsync`` instance."""
        dev = await asyncio.get_running_loop().run_in_executor(None, self._client.device, serial)
        if dev:
            return DeviceAsync(dev)
        return None


@asynccontextmanager
async def _acquire(lock, timeout=DEFAULT_LOCK_TIMEOUT_S):
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

        except asyncio.TimeoutError as exc:
            raise LockNotAcquiredException from exc

    finally:
        if acquired:
            lock.release()


class ADBPythonAsync(object):
    """A manager for ADB connections that uses a Python implementation of the ADB protocol.

    Parameters
    ----------
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication
    signer : PythonRSASigner, None
        The signer for the ADB keys, as loaded by :meth:`ADBPythonAsync.load_adbkey`

    """
    def __init__(self, host, port, adbkey='', signer=None):
        self.host = host
        self.port = int(port)
        self.adbkey = adbkey
        self._adb = AdbDeviceTcpAsync(host=self.host, port=self.port, default_transport_timeout_s=DEFAULT_ADB_TIMEOUT_S)
        self._signer = signer

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
                        if not self._signer:
                            self._signer = await self.load_adbkey(self.adbkey)

                        await self._adb.connect(rsa_keys=[self._signer], transport_timeout_s=1.0, auth_timeout_s=auth_timeout_s)

                    # Connect without authentication
                    else:
                        await self._adb.connect(transport_timeout_s=1.0, auth_timeout_s=auth_timeout_s)

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

    @staticmethod
    async def load_adbkey(adbkey):
        """Load the ADB keys.

        Parameters
        ----------
        adbkey : str
            The path to the ``adbkey`` file for ADB authentication

        Returns
        -------
        PythonRSASigner
            The ``PythonRSASigner`` with the key files loaded

        """
        # private key
        async with aiofiles.open(adbkey) as f:
            priv = await f.read()

        # public key
        try:
            async with aiofiles.open(adbkey + '.pub') as f:
                pub = await f.read()
        except FileNotFoundError:
            pub = ''

        return PythonRSASigner(pub, priv)

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
            if result and result[5:6] == b"\r":
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


class ADBServerAsync(object):
    """A manager for ADB connections that uses an ADB server.

    Parameters
    ----------
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
    adb_server_ip : str
        The IP address of the ADB server
    adb_server_port : int
        The port for the ADB server

    """
    def __init__(self, host, port=5555, adb_server_ip='', adb_server_port=5037):
        self.host = host
        self.port = int(port)
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port
        self._adb_client = None
        self._adb_device = None

        # keep track of whether the ADB connection is/was intact
        self._available = False
        self._was_available = False

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
        if not self._adb_client or not self._adb_device:
            return False

        return self._available

    async def close(self):
        """Close the ADB server socket connection.

        Currently, this doesn't do anything except set ``self._available = False``.

        """
        self._available = False

    async def connect(self, always_log_errors=True):
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
        try:
            async with _acquire(self._adb_lock):
                # Catch exceptions
                try:
                    self._adb_client = ClientAsync(host=self.adb_server_ip, port=self.adb_server_port)
                    self._adb_device = await self._adb_client.device('{}:{}'.format(self.host, self.port))

                    # ADB connection successfully established
                    if self._adb_device:
                        _LOGGER.debug("ADB connection to %s:%d via ADB server %s:%d successfully established", self.host, self.port, self.adb_server_ip, self.adb_server_port)
                        self._available = True
                        self._was_available = True
                        return True

                    # ADB connection attempt failed (without an exception)
                    if self._was_available or always_log_errors:
                        _LOGGER.warning("Couldn't connect to %s:%d via ADB server %s:%d because the server is not connected to the device", self.host, self.port, self.adb_server_ip, self.adb_server_port)

                    await self.close()
                    self._available = False
                    self._was_available = False
                    return False

                # ADB connection attempt failed
                except Exception as exc:  # noqa pylint: disable=broad-except
                    if self._was_available or always_log_errors:
                        _LOGGER.warning("Couldn't connect to %s:%d via ADB server %s:%d, error: %s", self.host, self.port, self.adb_server_ip, self.adb_server_port, exc)

                    await self.close()
                    self._available = False
                    self._was_available = False
                    return False

        except LockNotAcquiredException:
            _LOGGER.warning("Couldn't connect to %s:%d via ADB server %s:%d because pure-python-adb lock not acquired.", self.host, self.port, self.adb_server_ip, self.adb_server_port)
            await self.close()
            self._available = False
            self._was_available = False
            return False

    async def pull(self, local_path, device_path):
        """Pull a file from the device using an ADB server.

        Parameters
        ----------
        local_path : str
            The path where the file will be saved
        device_path : str
            The file on the device that will be pulled

        """
        if not self.available:
            _LOGGER.debug("ADB command not sent to %s:%d via ADB server %s:%d because pure-python-adb connection is not established: pull(%s, %s)", self.host, self.port, self.adb_server_ip, self.adb_server_port, local_path, device_path)
            return

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Sending command to %s:%d via ADB server %s:%d: pull(%s, %s)", self.host, self.port, self.adb_server_ip, self.adb_server_port, local_path, device_path)
            await self._adb_device.pull(device_path, local_path)
            return

    async def push(self, local_path, device_path):
        """Push a file to the device using an ADB server.

        Parameters
        ----------
        local_path : str
            The file that will be pushed to the device
        device_path : str
            The path where the file will be saved on the device

        """
        if not self.available:
            _LOGGER.debug("ADB command not sent to %s:%d via ADB server %s:%d because pure-python-adb connection is not established: push(%s, %s)", self.host, self.port, self.adb_server_ip, self.adb_server_port, local_path, device_path)
            return

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Sending command to %s:%d via ADB server %s:%d: push(%s, %s)", self.host, self.port, self.adb_server_ip, self.adb_server_port, local_path, device_path)
            await self._adb_device.push(local_path, device_path)
            return

    async def screencap(self):
        """Take a screenshot using an ADB server.

        Returns
        -------
        bytes, None
            The screencap as a binary .png image, or ``None`` if there was an ``IndexError`` exception

        """
        if not self.available:
            _LOGGER.debug("ADB screencap not taken from %s:%d via ADB server %s:%d because pure-python-adb connection is not established", self.host, self.port, self.adb_server_ip, self.adb_server_port)
            return None

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Taking screencap from %s:%d via ADB server %s:%d", self.host, self.port, self.adb_server_ip, self.adb_server_port)
            return await self._adb_device.screencap()

    async def shell(self, cmd):
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
        if not self.available:
            _LOGGER.debug("ADB command not sent to %s:%d via ADB server %s:%d because pure-python-adb connection is not established: %s", self.host, self.port, self.adb_server_ip, self.adb_server_port, cmd)
            return None

        async with _acquire(self._adb_lock):
            _LOGGER.debug("Sending command to %s:%d via ADB server %s:%d: %s", self.host, self.port, self.adb_server_ip, self.adb_server_port, cmd)
            return await self._adb_device.shell(cmd)
