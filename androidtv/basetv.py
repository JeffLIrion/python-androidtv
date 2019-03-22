"""Communicate with an Android TV or Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging
import re
from socket import error as socket_error
import sys
import threading

from adb import adb_commands
from adb.sign_pythonrsa import PythonRSASigner
from adb_messenger.client import Client as AdbClient

from . import constants

if sys.version_info[0] > 2 and sys.version_info[1] > 1:
    LOCK_KWARGS = {'timeout': 3}
else:
    LOCK_KWARGS = {}


Signer = PythonRSASigner.FromRSAKeyPath


class BaseTV:
    """Base class for representing an Android TV / Fire TV device."""

    def __init__(self, host, adbkey='', adb_server_ip='', adb_server_port=5037):
        """Initialize a ``BaseTV`` object.

        Parameters
        ----------
        host : str
            The address of the device in the format ``<ip address>:<host>``
        adbkey : str
            The path to the ``adbkey`` file for ADB authentication; the file ``adbkey.pub`` must be in the same directory
        adb_server_ip : str
            The IP address of the ADB server
        adb_server_port : int
            The port for the ADB server

        """
        self.host = host
        self.adbkey = adbkey
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port

        # keep track of whether the ADB connection is intact
        self._available = False

        # use a lock to make sure that ADB commands don't overlap
        self._adb_lock = threading.Lock()

        # the attributes used for sending ADB commands; filled in in `self.connect()`
        self._adb = None  # python-adb
        self._adb_client = None  # pure-python-adb
        self._adb_device = None  # pure-python-adb

        # the method used for sending ADB commands
        if not self.adb_server_ip:
            # python-adb
            self.adb_shell = self._adb_shell_python_adb
        else:
            # pure-python-adb
            self.adb_shell = self._adb_shell_pure_python_adb

        # establish the ADB connection
        self.connect()

        # get device properties
        self.device_properties = self.get_device_properties()

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    def _adb_shell_python_adb(self, cmd):
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
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):
            try:
                return self._adb.Shell(cmd)
            finally:
                self._adb_lock.release()

    def _adb_shell_pure_python_adb(self, cmd):
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
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):
            try:
                return self._adb_device.shell(cmd)
            finally:
                self._adb_lock.release()

    def _key(self, key):
        """Send a key event to device.

        Parameters
        ----------
        key : str, int
            The Key constant

        """
        self.adb_shell('input keyevent {0}'.format(key))

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
        self._adb_lock.acquire(**LOCK_KWARGS)
        try:
            if not self.adb_server_ip:
                # python-adb
                try:
                    if self.adbkey:
                        signer = Signer(self.adbkey)

                        # Connect to the device
                        self._adb = adb_commands.AdbCommands().ConnectDevice(serial=self.host, rsa_keys=[signer], default_timeout_ms=9000)
                    else:
                        self._adb = adb_commands.AdbCommands().ConnectDevice(serial=self.host, default_timeout_ms=9000)

                    # ADB connection successfully established
                    self._available = True

                except socket_error as serr:
                    if self._available or always_log_errors:
                        if serr.strerror is None:
                            serr.strerror = "Timed out trying to connect to ADB device."
                        logging.warning("Couldn't connect to host: %s, error: %s", self.host, serr.strerror)

                    # ADB connection attempt failed
                    self._adb = None
                    self._available = False

                finally:
                    return self._available

            else:
                # pure-python-adb
                try:
                    self._adb_client = AdbClient(host=self.adb_server_ip, port=self.adb_server_port)
                    self._adb_device = self._adb_client.device(self.host)
                    self._available = bool(self._adb_device)

                except:
                    self._available = False

                finally:
                    return self._available

        finally:
            self._adb_lock.release()

    # ======================================================================= #
    #                                                                         #
    #                        Home Assistant device info                       #
    #                                                                         #
    # ======================================================================= #
    def get_device_properties(self):
        """Return a dictionary of device properties.

        Returns
        -------
        props : dict
            A dictionary with keys ``'wifimac'``, ``'ethmac'``, ``'serialno'``, ``'manufacturer'``, ``'model'``, and ``'sw_version'``

        """
        properties = self.adb_shell(constants.CMD_MANUFACTURER + " && " +
                                    constants.CMD_MODEL + " && " +
                                    constants.CMD_SERIALNO + " && " +
                                    constants.CMD_VERSION + " && " +
                                    constants.CMD_MAC_WLAN0 + " && " +
                                    constants.CMD_MAC_ETH0)

        if not properties:
            return {}

        lines = properties.strip().splitlines()
        if len(lines) != 6:
            return {}

        manufacturer, model, serialno, version, mac_wlan0_output, mac_eth0_output = lines

        mac_wlan0_matches = re.findall(constants.MAC_REGEX_PATTERN, mac_wlan0_output)
        if mac_wlan0_matches:
            wifimac = mac_wlan0_matches[0]
        else:
            wifimac = None

        mac_eth0_matches = re.findall(constants.MAC_REGEX_PATTERN, mac_eth0_output)
        if mac_eth0_matches:
            ethmac = mac_eth0_matches[0]
        else:
            ethmac = None

        props = {'manufacturer': manufacturer,
                 'model': model,
                 'serialno': serialno,
                 'sw_version': version,
                 'wifimac': wifimac,
                 'ethmac': ethmac}

        return props

    # ======================================================================= #
    #                                                                         #
    #                               Properties                                #
    #                                                                         #
    # ======================================================================= #
    @property
    def available(self):
        """Check whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        if not self.adb_server_ip:
            # python-adb
            return bool(self._adb)

        # pure-python-adb
        try:
            # make sure the server is available
            adb_devices = self._adb_client.devices()

            # make sure the device is available
            try:
                # case 1: the device is currently available
                if any([self.host in dev.get_serial_no() for dev in adb_devices]):
                    if not self._available:
                        self._available = True
                    return True

                # case 2: the device is not currently available
                if self._available:
                    logging.error('ADB server is not connected to the device.')
                    self._available = False
                return False

            except RuntimeError:
                if self._available:
                    logging.error('ADB device is unavailable; encountered an error when searching for device.')
                    self._available = False
                return False

        except RuntimeError:
            if self._available:
                logging.error('ADB server is unavailable.')
                self._available = False
            return False

    @property
    def awake(self):
        """Check if the device is awake (screensaver is not running).

        Returns
        -------
        bool
            Whether or not the device is awake (screensaver is not running)

        """
        return self.adb_shell(constants.CMD_AWAKE + constants.CMD_SUCCESS1_FAILURE0) == '1'

    @property
    def current_app(self):
        """Return the current app.

        Returns
        -------
        dict
            A dictionary with keys ``'package'`` and ``'activity'`` if the current app was found; otherwise, ``None``

        """
        current_focus = self.adb_shell(constants.CMD_CURRENT_APP)
        if current_focus is None:
            return None

        current_focus = current_focus.replace("\r", "")
        matches = constants.REGEX_WINDOW.search(current_focus)

        # case 1: current app was successfully found
        if matches:
            (pkg, activity) = matches.group("package", "activity")
            return {"package": pkg, "activity": activity}

        # case 2: current app could not be found
        logging.warning("Couldn't get current app, reply was %s", current_focus)
        return None

    @property
    def manufacturer(self):
        """Get the 'manufacturer' property from the device.

        Returns
        -------
        str, None
            The manufacturer of the device

        """
        output = self.adb_shell(constants.CMD_MANUFACTURER)
        if not output:
            return None
        return output.strip()

    @property
    def media_session_state(self):
        """Get the state from the output of ``dumpsys media_session``.

        Returns
        -------
        int, None
            The state from the output of the ADB shell command ``dumpsys media_session``, or ``None`` if it could not be determined

        """
        output = self.adb_shell(constants.CMD_MEDIA_SESSION_STATE)
        if not output:
            return None

        matches = constants.REGEX_MEDIA_SESSION_STATE.search(output)
        if matches:
            return int(matches.group('state'))
        return None

    @property
    def screen_on(self):
        """Check if the screen is on.

        Returns
        -------
        bool
            Whether or not the device is on

        """
        return self.adb_shell(constants.CMD_SCREEN_ON + constants.CMD_SUCCESS1_FAILURE0) == '1'

    @property
    def wake_lock(self):
        """Check for wake locks (device is playing).

        Returns
        -------
        bool
            Whether or not the ``wake_lock_size`` property is equal to 1.

        """
        return self.adb_shell(constants.CMD_WAKE_LOCK + constants.CMD_SUCCESS1_FAILURE0) == '1'

    @property
    def wake_lock_size(self):
        """Get the size of the current wake lock.

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        output = self.adb_shell(constants.CMD_WAKE_LOCK_SIZE)
        if not output:
            return None
        return int(output.split("=")[1].strip())

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: basic commands                      #
    #                                                                         #
    # ======================================================================= #

    def power(self):
        """Send power action."""
        self._key(constants.KEY_POWER)

    def sleep(self):
        """Send sleep action."""
        self._key(constants.KEY_SLEEP)

    def home(self):
        """Send home action."""
        self._key(constants.KEY_HOME)

    def up(self):
        """Send up action."""
        self._key(constants.KEY_UP)

    def down(self):
        """Send down action."""
        self._key(constants.KEY_DOWN)

    def left(self):
        """Send left action."""
        self._key(constants.KEY_LEFT)

    def right(self):
        """Send right action."""
        self._key(constants.KEY_RIGHT)

    def enter(self):
        """Send enter action."""
        self._key(constants.KEY_ENTER)

    def back(self):
        """Send back action."""
        self._key(constants.KEY_BACK)

    def menu(self):
        """Send menu action."""
        self._key(constants.KEY_MENU)

    def volume_up(self):
        """Send volume up action."""
        self._key(constants.KEY_VOLUME_UP)

    def volume_down(self):
        """Send volume down action."""
        self._key(constants.KEY_VOLUME_DOWN)

    def mute_volume(self):
        """Mute the volume."""
        self._key(constants.KEY_MUTE)

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: media commands                      #
    #                                                                         #
    # ======================================================================= #
    def media_play_pause(self):
        """Send media play/pause action."""
        self._key(constants.KEY_PLAY_PAUSE)

    def media_play(self):
        """Send media play action."""
        self._key(constants.KEY_PLAY)

    def media_pause(self):
        """Send media pause action."""
        self._key(constants.KEY_PAUSE)

    def media_stop(self):
        """Send media stop action."""
        self._key(constants.KEY_STOP)

    def media_next(self):
        """Send media next action (results in fast-forward)."""
        self._key(constants.KEY_NEXT)

    def media_previous(self):
        """Send media previous action (results in rewind)."""
        self._key(constants.KEY_PREVIOUS)

    # ======================================================================= #
    #                                                                         #
    #                   "key" methods: alphanumeric commands                  #
    #                                                                         #
    # ======================================================================= #
    def space(self):
        """Send space keypress."""
        self._key(constants.KEY_SPACE)

    def key_0(self):
        """Send 0 keypress."""
        self._key(constants.KEY_0)

    def key_1(self):
        """Send 1 keypress."""
        self._key(constants.KEY_1)

    def key_2(self):
        """Send 2 keypress."""
        self._key(constants.KEY_2)

    def key_3(self):
        """Send 3 keypress."""
        self._key(constants.KEY_3)

    def key_4(self):
        """Send 4 keypress."""
        self._key(constants.KEY_4)

    def key_5(self):
        """Send 5 keypress."""
        self._key(constants.KEY_5)

    def key_6(self):
        """Send 6 keypress."""
        self._key(constants.KEY_6)

    def key_7(self):
        """Send 7 keypress."""
        self._key(constants.KEY_7)

    def key_8(self):
        """Send 8 keypress."""
        self._key(constants.KEY_8)

    def key_9(self):
        """Send 9 keypress."""
        self._key(constants.KEY_9)

    def key_a(self):
        """Send a keypress."""
        self._key(constants.KEY_A)

    def key_b(self):
        """Send b keypress."""
        self._key(constants.KEY_B)

    def key_c(self):
        """Send c keypress."""
        self._key(constants.KEY_C)

    def key_d(self):
        """Send d keypress."""
        self._key(constants.KEY_D)

    def key_e(self):
        """Send e keypress."""
        self._key(constants.KEY_E)

    def key_f(self):
        """Send f keypress."""
        self._key(constants.KEY_F)

    def key_g(self):
        """Send g keypress."""
        self._key(constants.KEY_G)

    def key_h(self):
        """Send h keypress."""
        self._key(constants.KEY_H)

    def key_i(self):
        """Send i keypress."""
        self._key(constants.KEY_I)

    def key_j(self):
        """Send j keypress."""
        self._key(constants.KEY_J)

    def key_k(self):
        """Send k keypress."""
        self._key(constants.KEY_K)

    def key_l(self):
        """Send l keypress."""
        self._key(constants.KEY_L)

    def key_m(self):
        """Send m keypress."""
        self._key(constants.KEY_M)

    def key_n(self):
        """Send n keypress."""
        self._key(constants.KEY_N)

    def key_o(self):
        """Send o keypress."""
        self._key(constants.KEY_O)

    def key_p(self):
        """Send p keypress."""
        self._key(constants.KEY_P)

    def key_q(self):
        """Send q keypress."""
        self._key(constants.KEY_Q)

    def key_r(self):
        """Send r keypress."""
        self._key(constants.KEY_R)

    def key_s(self):
        """Send s keypress."""
        self._key(constants.KEY_S)

    def key_t(self):
        """Send t keypress."""
        self._key(constants.KEY_T)

    def key_u(self):
        """Send u keypress."""
        self._key(constants.KEY_U)

    def key_v(self):
        """Send v keypress."""
        self._key(constants.KEY_V)

    def key_w(self):
        """Send w keypress."""
        self._key(constants.KEY_W)

    def key_x(self):
        """Send x keypress."""
        self._key(constants.KEY_X)

    def key_y(self):
        """Send y keypress."""
        self._key(constants.KEY_Y)

    def key_z(self):
        """Send z keypress."""
        self._key(constants.KEY_Z)
