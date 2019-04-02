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
    FileNotFoundError = IOError


class BaseTV(object):
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

        # the max volume level (determined when first getting the volume level)
        self.max_volume = None

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

        return None

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

        return None

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
    def audio_state(self):
        """Check if audio is playing, paused, or idle.

        Returns
        -------
        str, None
            The audio state, as determined from the ADB shell command ``dumpsys audio``, or ``None`` if it could not be determined

        """
        output = self.adb_shell(constants.CMD_AUDIO_STATE)
        if output is None:
            return None
        if output == '1':
            return constants.STATE_PAUSED
        if output == '2':
            return constants.STATE_PLAYING
        return constants.STATE_IDLE

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
        str, None
            The ID of the current app, or ``None`` if it could not be determined

        """
        current_window = self.adb_shell(constants.CMD_CURRENT_APP)

        return self._current_app(current_window)

    @property
    def device(self):
        """Get the current playback device.

        Returns
        -------
        str, None
            The current playback device, or ``None`` if it could not be determined

        """
        stream_music = self._get_stream_music()

        return self._device(stream_music)

    @property
    def is_volume_muted(self):
        """Whether or not the volume is muted.

        Returns
        -------
        bool, None
            Whether or not the volume is muted, or ``None`` if it could not be determined

        """
        stream_music = self._get_stream_music()

        return self._is_volume_muted(stream_music)

    @property
    def media_session_state(self):
        """Get the state from the output of ``dumpsys media_session``.

        Returns
        -------
        int, None
            The state from the output of the ADB shell command ``dumpsys media_session``, or ``None`` if it could not be determined

        """
        media_session = self.adb_shell(constants.CMD_MEDIA_SESSION_STATE)

        return self._media_session_state(media_session)

    @property
    def running_apps(self):
        """Return a list of running user applications.

        Returns
        -------
        list
            A list of the running apps

        """
        ps = self.adb_shell(constants.CMD_RUNNING_APPS)

        return self._running_apps(ps)

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
    def volume(self):
        """Get the absolute volume level.

        Returns
        -------
        int, None
            The absolute volume level, or ``None`` if it could not be determined

        """
        stream_music = self._get_stream_music()
        device = self._device(stream_music)

        return self._volume(stream_music, device)

    @property
    def volume_level(self):
        """Get the relative volume level.

        Returns
        -------
        float, None
            The volume level (between 0 and 1), or ``None`` if it could not be determined

        """
        volume = self.volume

        return self._volume_level(volume)

    @property
    def wake_lock_size(self):
        """Get the size of the current wake lock.

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        locks_size = self.adb_shell(constants.CMD_WAKE_LOCK_SIZE)

        return self._wake_lock_size(locks_size)

    # ======================================================================= #
    #                                                                         #
    #                            Parse properties                             #
    #                                                                         #
    # ======================================================================= #
    @staticmethod
    def _audio_state(dumpsys_audio):
        """Parse the ``audio_state`` property from the output of ``adb shell dumpsys audio``.

        Parameters
        ----------
        dumpsys_audio : str, None
            The output of ``adb shell dumpsys audio``

        Returns
        -------
        str, None
            The audio state, or ``None`` if it could not be determined

        """
        if not dumpsys_audio:
            return None

        if 'started' in dumpsys_audio:
            return constants.STATE_PLAYING

        if 'paused' in dumpsys_audio:
            return constants.STATE_PAUSED

        return constants.STATE_IDLE

    @staticmethod
    def _current_app(current_window):
        """Return the current app from the output of ``adb shell dumpsys window windows | grep mCurrentFocus``.

        Parameters
        ----------
        current_window : str, None
            The output of ``adb shell dumpsys window windows | grep mCurrentFocus``

        Returns
        -------
        str, None
            The ID of the current app, or ``None`` if it could not be determined

        """
        if current_window is None:
            return None

        current_window = current_window.replace("\r", "")
        matches = constants.REGEX_WINDOW.search(current_window)

        # case 1: current app was successfully found
        if matches:
            return matches.group('package')

        # case 2: current app could not be found
        return None

    @staticmethod
    def _device(stream_music):
        """Get the current playback device from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``

        Returns
        -------
        str, None
            The current playback device, or ``None`` if it could not be determined

        """
        if not stream_music:
            return None

        matches = re.findall(constants.DEVICE_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0]

        return None

    def _get_stream_music(self, dumpsys_audio=None):
        """Get the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        dumpsys_audio : str, None
            The output of ``adb shell dumpsys audio``

        Returns
        -------
        str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``, or ``None`` if it could not be determined

        """
        if not dumpsys_audio:
            dumpsys_audio = self.adb_shell("dumpsys audio")

        if not dumpsys_audio:
            return None

        matches = re.findall(constants.STREAM_MUSIC_REGEX_PATTERN, dumpsys_audio, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0]

        return None

    @staticmethod
    def _is_volume_muted(stream_music):
        """Determine whether or not the volume is muted from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``

        Returns
        -------
        bool, None
            Whether or not the volume is muted, or ``None`` if it could not be determined

        """
        if not stream_music:
            return None

        matches = re.findall(constants.MUTED_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0] == 'true'

        return None

    @staticmethod
    def _media_session_state(media_session):
        """Get the state from the output of ``adb shell dumpsys media_session | grep -m 1 'state=PlaybackState {'``.

        Parameters
        ----------
        media_session : str, None
            The output of ``adb shell dumpsys media_session | grep -m 1 'state=PlaybackState {'``

        Returns
        -------
        int, None
            The state from the output of the ADB shell command ``dumpsys media_session``, or ``None`` if it could not be determined

        """
        if not media_session:
            return None

        matches = constants.REGEX_MEDIA_SESSION_STATE.search(media_session)
        if matches:
            return int(matches.group('state'))

        return None

    @staticmethod
    def _running_apps(ps):
        """Get the running apps from the output of ``ps | grep u0_a``.

        Parameters
        ----------
        ps : str, None
            The output of ``adb shell ps | grep u0_a``

        Returns
        -------
        list, None
            A list of the running apps, or ``None`` if it could not be determined

        """
        if ps:
            if isinstance(ps, list):
                return [line.strip().rsplit(' ', 1)[-1] for line in ps if line.strip()]
            return [line.strip().rsplit(' ', 1)[-1] for line in ps.splitlines() if line.strip()]

        return None

    def _volume(self, stream_music, device):
        """Get the absolute volume level from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``
        device : str, None
            The current playback device

        Returns
        -------
        int, None
            The absolute volume level, or ``None`` if it could not be determined

        """
        if not stream_music:
            return None

        if not self.max_volume:
            max_volume_matches = re.findall(constants.MAX_VOLUME_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
            if max_volume_matches:
                self.max_volume = float(max_volume_matches[0])
            else:
                self.max_volume = 15.

        if not device:
            return None

        volume_matches = re.findall(device + constants.VOLUME_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if volume_matches:
            return int(volume_matches[0])

        return None

    def _volume_level(self, volume):
        """Get the relative volume level from the absolute volume level.

        Parameters
        -------
        volume: int, None
            The absolute volume level

        Returns
        -------
        float, None
            The volume level (between 0 and 1), or ``None`` if it could not be determined

        """
        if volume is not None and self.max_volume:
            return volume / self.max_volume

        return None

    @staticmethod
    def _wake_lock_size(locks_size):
        """Get the size of the current wake lock from the output of ``adb shell dumpsys power | grep Locks | grep 'size='``.

        Parameters
        ----------
        locks_size : str, None
            The output of ``adb shell dumpsys power | grep Locks | grep 'size='``.

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        if locks_size:
            return int(locks_size.split("=")[1].strip())

        return None

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

    def mute_volume(self):
        """Mute the volume."""
        self._key(constants.KEY_MUTE)

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: media commands                      #
    #                                                                         #
    # ======================================================================= #
    def media_play(self):
        """Send media play action."""
        self._key(constants.KEY_PLAY)

    def media_pause(self):
        """Send media pause action."""
        self._key(constants.KEY_PAUSE)

    def media_play_pause(self):
        """Send media play/pause action."""
        self._key(constants.KEY_PLAY_PAUSE)

    def media_stop(self):
        """Send media stop action."""
        self._key(constants.KEY_STOP)

    def media_next_track(self):
        """Send media next action (results in fast-forward)."""
        self._key(constants.KEY_NEXT)

    def media_previous_track(self):
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

    # ======================================================================= #
    #                                                                         #
    #                              volume methods                             #
    #                                                                         #
    # ======================================================================= #
    def set_volume_level(self, volume_level, current_volume_level=None):
        """Set the volume to the desired level.

        .. note::

           This method works by sending volume up/down commands with a 1 second pause in between.  Without this pause,
           the device will do a quick power cycle.  This is the most robust solution I've found so far.


        Parameters
        ----------
        volume_level : float
            The new volume level (between 0 and 1)
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float, None
            The new volume level (between 0 and 1), or ``None`` if ``self.max_volume`` could not be determined

        """
        # if necessary, determine the current volume and/or the max volume
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = min(max(round(self.max_volume * current_volume_level), 0.), self.max_volume)

        # if `self.max_volume` could not be determined, do not proceed
        if not self.max_volume:
            return None

        new_volume = min(max(round(self.max_volume * volume_level), 0.), self.max_volume)

        # Case 1: the new volume is the same as the current volume
        if new_volume == current_volume:
            return new_volume / self.max_volume

        # Case 2: the new volume is less than the current volume
        if new_volume < current_volume:
            cmd = "(" + " && sleep 1 && ".join(["input keyevent {0}".format(constants.KEY_VOLUME_DOWN)] * int(current_volume - new_volume)) + ") &"

        # Case 3: the new volume is greater than the current volume
        else:
            cmd = "(" + " && sleep 1 && ".join(["input keyevent {0}".format(constants.KEY_VOLUME_UP)] * int(new_volume - current_volume)) + ") &"

        # send the volume down/up commands
        self.adb_shell(cmd)

        # return the new volume level
        return new_volume / self.max_volume

    def volume_up(self, current_volume_level=None):
        """Send volume up action.

        Parameters
        ----------
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float, None
            The new volume level (between 0 and 1), or ``None`` if ``self.max_volume`` could not be determined

        """
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = round(self.max_volume * current_volume_level)

        # send the volume up command
        self._key(constants.KEY_VOLUME_UP)

        # if `self.max_volume` could not be determined, return `None` as the new `volume_level`
        if not self.max_volume:
            return None

        # return the new volume level
        return min(current_volume + 1, self.max_volume) / self.max_volume

    def volume_down(self, current_volume_level=None):
        """Send volume down action.

        Parameters
        ----------
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float, None
            The new volume level (between 0 and 1), or ``None`` if ``self.max_volume`` could not be determined

        """
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = round(self.max_volume * current_volume_level)

        # send the volume down command
        self._key(constants.KEY_VOLUME_DOWN)

        # if `self.max_volume` could not be determined, return `None` as the new `volume_level`
        if not self.max_volume:
            return None

        # return the new volume level
        return max(current_volume - 1, 0.) / self.max_volume
