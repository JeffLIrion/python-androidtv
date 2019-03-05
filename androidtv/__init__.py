#!/usr/bin/env python

"""
Communicate with an Android TV device via ADB over a network.

ADB Debugging must be enabled.
"""

import logging
import re
from socket import error as socket_error
import sys
import threading

from adb import adb_commands
from adb.sign_pythonrsa import PythonRSASigner
# from adb.adb_protocol import InvalidChecksumError
from adb_messenger.client import Client as AdbClient

if sys.version_info[0] > 2 and sys.version_info[1] > 1:
    LOCK_KWARGS = {'timeout': 3}
else:
    LOCK_KWARGS = {}


Signer = PythonRSASigner.FromRSAKeyPath

# Matches window windows output for app & activity name gathering
WINDOW_REGEX = re.compile(r"Window\{(?P<id>.+?) (?P<user>.+) (?P<package>.+?)(?:\/(?P<activity>.+?))?\}$", re.MULTILINE)

# Regular expression patterns
BLOCK_REGEX_PATTERN = "STREAM_MUSIC(.*?)- STREAM"
DEVICE_REGEX_PATTERN = r"Devices: (.*?)\W"
MUTED_REGEX_PATTERN = r"Muted: (.*?)\W"
VOLUME_REGEX_PATTERN = r"\): (\d{1,})"

PROP_REGEX_PATTERN = r".*?\[(.*?)]"
WIFIMAC_PROP_REGEX_PATTERN = "wifimac" + PROP_REGEX_PATTERN
WIFIMAC_REGEX_PATTERN = "ether (.*?) brd"
SERIALNO_REGEX_PATTERN = "serialno" + PROP_REGEX_PATTERN
MANUF_REGEX_PATTERN = "manufacturer" + PROP_REGEX_PATTERN
MODEL_REGEX_PATTERN = "product.model" + PROP_REGEX_PATTERN
VERSION_REGEX_PATTERN = "version.release" + PROP_REGEX_PATTERN

# ADB shell commands for getting the `screen_on`, `awake`, `wake_lock`, `audio_state`, and `current_app` properties
SCREEN_ON_CMD = "dumpsys power | grep 'Display Power' | grep -q 'state=ON'"
AWAKE_CMD = "dumpsys power | grep mWakefulness | grep -q Awake"
WAKE_LOCK_CMD = "dumpsys power | grep Locks | grep -q 'size=0'"
WAKE_LOCK_SIZE_CMD = "dumpsys power | grep Locks | grep 'size='"
AUDIO_STATE_CMD = r"dumpsys audio | grep -q paused && echo -e '1\c' || (dumpsys audio | grep -q started && echo '2\c' || echo '0\c')"
CURRENT_APP_CMD = "dumpsys window windows | grep mCurrentFocus"

# echo '1' if the previous shell command was successful
SUCCESS1 = r" && echo -e '1\c'"

# echo '1' if the previous shell command was successful, echo '0' if it was not
SUCCESS1_FAILURE0 = r" && echo -e '1\c' || echo -e '0\c'"

# https://developer.android.com/reference/android/view/KeyEvent
# ADB key event codes.
BACK = 4
BLUE = 186
COMPONENT1 = 249
COMPONENT2 = 250
COMPOSITE1 = 247
COMPOSITE2 = 248
DOWN = 20
END = 123
ENTER = 66
GREEN = 184
HDMI1 = 243
HDMI2 = 244
HDMI3 = 245
HDMI4 = 246
HOME = 3
INPUT = 178
LEFT = 21
MENU = 82
MOVE_HOME = 122
MUTE = 164
NEXT = 87
PAIRING = 225
PAUSE = 127
PLAY = 126
PLAY_PAUSE = 85
POWER = 26
PREVIOUS = 88
RESUME = 224
RIGHT = 22
SAT = 237
SEARCH = 84
SETTINGS = 176
SLEEP = 223
STOP = 86
SUSPEND = 276
SYSDOWN = 281
SYSLEFT = 282
SYSRIGHT = 283
SYSUP = 280
TEXT = 233
TOP = 122
UP = 19
VGA = 251
VOLUME_DOWN = 25
VOLUME_UP = 24
YELLOW = 185

# Alphanumeric key event codes.
SPACE = 62
KEY_0 = 7
KEY_1 = 8
KEY_2 = 9
KEY_3 = 10
KEY_4 = 11
KEY_5 = 12
KEY_6 = 13
KEY_7 = 14
KEY_8 = 15
KEY_9 = 16
KEY_A = 29
KEY_B = 30
KEY_C = 31
KEY_D = 32
KEY_E = 33
KEY_F = 34
KEY_G = 35
KEY_H = 36
KEY_I = 37
KEY_J = 38
KEY_K = 39
KEY_L = 40
KEY_M = 41
KEY_N = 42
KEY_O = 43
KEY_P = 44
KEY_Q = 45
KEY_R = 46
KEY_S = 47
KEY_T = 48
KEY_U = 49
KEY_V = 50
KEY_W = 51
KEY_X = 52
KEY_Y = 53
KEY_Z = 54

# Android TV actions
ACTIONS = {
    "BACK": BACK,
    "BLUE": BLUE,
    "COMPONENT1": COMPONENT1,
    "COMPONENT2": COMPONENT2,
    "COMPOSITE1": COMPOSITE1,
    "COMPOSITE2": COMPOSITE2,
    "DOWN": DOWN,
    "END": END,
    "ENTER": ENTER,
    "GREEN": GREEN,
    "HDMI1": HDMI1,
    "HDMI2": HDMI2,
    "HDMI3": HDMI3,
    "HDMI4": HDMI4,
    "HOME": HOME,
    "INPUT": INPUT,
    "LEFT": LEFT,
    "MENU": MENU,
    "MOVE_HOME": MOVE_HOME,
    "MUTE": MUTE,
    "PAIRING": PAIRING,
    "POWER": POWER,
    "RESUME": RESUME,
    "RIGHT": RIGHT,
    "SAT": SAT,
    "SEARCH": SEARCH,
    "SETTINGS": SETTINGS,
    "SLEEP": SLEEP,
    "SUSPEND": SUSPEND,
    "SYSDOWN": SYSDOWN,
    "SYSLEFT": SYSLEFT,
    "SYSRIGHT": SYSRIGHT,
    "SYSUP": SYSUP,
    "TEXT": TEXT,
    "TOP": TOP,
    "UP": UP,
    "VGA": VGA,
    "VOLUME_DOWN": VOLUME_DOWN,
    "VOLUME_UP": VOLUME_UP,
    "YELLOW": YELLOW
}

# Android TV states.
STATE_ON = 'on'
STATE_IDLE = 'idle'
STATE_OFF = 'off'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_STANDBY = 'standby'
STATE_UNKNOWN = 'unknown'


class AndroidTV:
    """Represents an Android TV device."""

    def __init__(self, host, adbkey='', adb_server_ip='', adb_server_port=5037):
        """Initialize AndroidTV object.

        :param host: Host in format <address>:port.
        :param adbkey: The path to the "adbkey" file
        :param adb_server_ip: the IP address for the ADB server
        :param adb_server_port: the port for the ADB server
        """
        self.host = host
        self.adbkey = adbkey
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port

        self.properties = None

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
        if self._available:
            self.properties = self.device_info()

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    def _adb_shell_python_adb(self, cmd):
        if not self.available:
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):
            try:
                return self._adb.Shell(cmd)
            finally:
                self._adb_lock.release()

    def _adb_shell_pure_python_adb(self, cmd):
        if not self._available:
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):
            try:
                return self._adb_device.shell(cmd)
            finally:
                self._adb_lock.release()

    def _dump(self, service, grep=None):
        """Perform a service dump.

        :param service: Service to dump.
        :param grep: Grep for this string.
        :returns: Dump, optionally grepped.
        """
        if grep:
            return self.adb_shell('dumpsys {0} | grep "{1}"'.format(service, grep))

        return self.adb_shell('dumpsys {0}'.format(service))

    def _dump_has(self, service, grep, search):
        """Check if a dump has particular content.

        :param service: Service to dump.
        :param grep: Grep for this string.
        :param search: Check for this substring.
        :returns: Found or not.
        """
        dump_grep = self._dump(service, grep=grep)

        if not dump_grep:
            return False

        return dump_grep.strip().find(search) > -1

    def _key(self, key):
        """Send a key event to device.

        :param key: Key constant.
        """
        self.adb_shell('input keyevent {0}'.format(key))

    def connect(self, always_log_errors=True):
        """Connect to an Android TV device.

        Will attempt to establish ADB connection to the given host.
        Failure sets state to UNKNOWN and disables sending actions.

        :returns: True if successful, False otherwise
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

    def start_intent(self, uri):
        """Start an intent on the device."""
        self.adb_shell("am start -a android.intent.action.VIEW -d {}".format(uri))

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def update(self):
        """Update the device status."""
        # Get the properties needed for the update.
        screen_on, awake, wake_lock_size, _current_app, audio_state, device, muted, volume = self.get_properties(lazy=True)

        # Get the current app.
        if isinstance(_current_app, dict) and 'package' in _current_app:
            current_app = _current_app['package']
        else:
            current_app = None

        # Check if device is off.
        if not screen_on:
            return STATE_OFF, current_app, device, muted, volume

        # TODO: determine the state differently based on the current app
        if audio_state:
            state = audio_state

        else:
            if not awake:
                state = STATE_IDLE
            elif wake_lock_size == 1:
                state = STATE_PLAYING
            else:
                state = STATE_PAUSED

        return state, current_app, device, muted, volume

    # ======================================================================= #
    #                                                                         #
    #                        Home Assistant device info                       #
    #                                                                         #
    # ======================================================================= #
    def device_info(self):
        """Return a dictionary of device properties."""
        properties = self.adb_shell('getprop')

        if 'wifimac' in properties:
            wifimac = re.findall(WIFIMAC_PROP_REGEX_PATTERN, properties)[0]
        else:
            wifi_out = self.adb_shell('ip addr show wlan0')
            wifimac = re.findall(WIFIMAC_REGEX_PATTERN, wifi_out)[0]

        serialno = re.findall(SERIALNO_REGEX_PATTERN, properties)[0]
        manufacturer = re.findall(MANUF_REGEX_PATTERN, properties)[0]
        model = re.findall(MODEL_REGEX_PATTERN, properties)[0]
        version = re.findall(VERSION_REGEX_PATTERN, properties)[0]

        props = {'wifimac': wifimac,
                 'serialno': serialno,
                 'manufacturer': manufacturer,
                 'model': model,
                 'sw_version': version}

        return props

    # ======================================================================= #
    #                                                                         #
    #                              App methods                                #
    #                                                                         #
    # ======================================================================= #
    # def app_state(self, app):
    #     """Informs if application is running """
    #     if not self.available or not self.screen_on:
    #         return STATE_OFF
    #     if self.current_app["package"] == app:
    #         return STATE_ON
    #     return STATE_OFF

    # def launch_app(self, app):
    #     if not self.available:
    #         return None
    #
    #     return self._send_intent(app, INTENT_LAUNCH)

    # def stop_app(self, app):
    #     if not self.available:
    #         return None
    #
    #     return self._send_intent(PACKAGE_LAUNCHER, INTENT_HOME)

    # ======================================================================= #
    #                                                                         #
    #                               properties                                #
    #                                                                         #
    # ======================================================================= #
    @property
    def available(self):
        """Check whether the ADB connection is intact."""
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

    # @property
    # def running_apps(self):
    #     """Return a list of running user applications."""
    #     ps = self.adb_shell("ps | grep u0_a")
    #     if ps:
    #         return [line.strip().rsplit(' ', 1)[-1] for line in ps.splitlines() if line.strip()]
    #     return []

    @property
    def current_app(self):
        """Return the current app."""
        current_focus = self.adb_shell(CURRENT_APP_CMD)
        if current_focus is None:
            return None

        current_focus = current_focus.replace("\r", "")
        matches = WINDOW_REGEX.search(current_focus)

        # case 1: current app was successfully found
        if matches:
            (pkg, activity) = matches.group("package", "activity")
            return {"package": pkg, "activity": activity}

        # case 2: current app could not be found
        logging.warning("Couldn't get current app, reply was %s", current_focus)
        return None

    @property
    def screen_on(self):
        """Check if the screen is on."""
        return self.adb_shell(SCREEN_ON_CMD + SUCCESS1_FAILURE0) == '1'

    @property
    def awake(self):
        """Check if the device is awake (screensaver is not running)."""
        return self.adb_shell(AWAKE_CMD + SUCCESS1_FAILURE0) == '1'

    @property
    def wake_lock(self):
        """Check for wake locks (device is playing)."""
        return self.adb_shell(WAKE_LOCK_CMD + SUCCESS1_FAILURE0) == '1'

    @property
    def wake_lock_size(self):
        """Get the size of the current wake lock."""
        output = self.adb_shell(WAKE_LOCK_SIZE_CMD)
        if not output:
            return None
        return int(output.split("=")[1].strip())

    @property
    def audio_state(self):
        """Check if audio is playing, paused, or idle."""
        output = self.adb_shell(AUDIO_STATE_CMD)
        if output is None:
            return None
        if output == '1':
            return STATE_PAUSED
        if output == '2':
            return STATE_PLAYING
        return STATE_IDLE

    @property
    def device(self):
        """Get the current playback device."""
        output = self.adb_shell("dumpsys audio")
        if not output:
            return None

        stream_block = re.findall(BLOCK_REGEX_PATTERN, output, re.DOTALL | re.MULTILINE)[0]
        return re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]

    @property
    def muted(self):
        """Whether or not the volume is muted."""
        output = self.adb_shell("dumpsys audio")
        if not output:
            return None

        stream_block = re.findall(BLOCK_REGEX_PATTERN, output, re.DOTALL | re.MULTILINE)[0]
        return re.findall(MUTED_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0] == 'true'

    @property
    def volume(self):
        """Get the volume level."""
        output = self.adb_shell("dumpsys audio")
        if not output:
            return None

        stream_block = re.findall(BLOCK_REGEX_PATTERN, output, re.DOTALL | re.MULTILINE)[0]
        device = re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]
        volume_level = re.findall(device + VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]

        return round(1 / 15 * float(volume_level), 2)

    def get_properties(self, lazy=False):
        """Get the properties needed for Home Assistant updates."""
        output = self.adb_shell(SCREEN_ON_CMD + (SUCCESS1 if lazy else SUCCESS1_FAILURE0) + " && " +
                                AWAKE_CMD + (SUCCESS1 if lazy else SUCCESS1_FAILURE0) + " && " +
                                WAKE_LOCK_SIZE_CMD + " && " +
                                CURRENT_APP_CMD + " && " +
                                "dumpsys audio")

        # ADB command was unsuccessful
        if output is None:
            return None, None, None, None, None, None, None, None

        # `screen_on` property
        if not output:
            return False, False, -1, None, None, None, None, None
        screen_on = output[0] == '1'

        # `awake` property
        if len(output) < 2:
            return screen_on, False, -1, None, None, None, None, None
        awake = output[1] == '1'

        lines = output.strip().splitlines()

        # `wake_lock_size` property
        if len(lines[0]) < 3:
            return screen_on, awake, -1, None, None, None, None, None
        wake_lock_size = int(lines[0].split("=")[1].strip())

        # `current_app` property
        if len(lines) < 2:
            return screen_on, awake, wake_lock_size, None, None, None, None, None

        matches = WINDOW_REGEX.search(lines[1])
        if matches:
            # case 1: current app was successfully found
            (pkg, activity) = matches.group("package", "activity")
            current_app = {"package": pkg, "activity": activity}
        else:
            # case 2: current app could not be found
            logging.warning("Couldn't get current app, reply was %s", lines[1])
            current_app = None

        # "dumpsys audio" output
        if len(lines) < 3:
            return screen_on, awake, wake_lock_size, current_app, None, None, None, None

        audio_output = "\n".join(lines[2:])

        # `audio_state` property
        if 'started' in audio_output:
            audio_state = STATE_PLAYING
        elif 'paused' in audio_output:
            audio_state = STATE_PAUSED
        else:
            audio_state = STATE_IDLE

        matches = re.findall(BLOCK_REGEX_PATTERN, audio_output, re.DOTALL | re.MULTILINE)
        if not matches:
            return screen_on, awake, wake_lock_size, current_app, audio_state, None, None, None
        stream_block = matches[0]

        # `device` property
        matches = re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
        if matches:
            device = matches[0]

            # `volume` property
            matches = re.findall(device + VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
            if matches:
                volume = round(1 / 15 * float(matches[0]), 2)
            else:
                volume = None

        else:
            device = None
            volume = None

        # `muted` property
        matches = re.findall(MUTED_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
        if matches:
            muted = matches[0] == 'true'
        else:
            muted = None

        return screen_on, awake, wake_lock_size, current_app, audio_state, device, muted, volume

    # ======================================================================= #
    #                                                                         #
    #                           turn on/off methods                           #
    #                                                                         #
    # ======================================================================= #
    def turn_on(self):
        """Send power action if device is off."""
        self.adb_shell(SCREEN_ON_CMD + " || input keyevent {0}".format(POWER))

    def turn_off(self):
        """Send power action if device is not off."""
        self.adb_shell(SCREEN_ON_CMD + " && input keyevent {0}".format(POWER))

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: basic commands                      #
    #                                                                         #
    # ======================================================================= #

    def _power(self):
        """Send power action."""
        self._key(POWER)

    def home(self):
        """Send home action."""
        self._key(HOME)

    def up(self):
        """Send up action."""
        self._key(UP)

    def down(self):
        """Send down action."""
        self._key(DOWN)

    def left(self):
        """Send left action."""
        self._key(LEFT)

    def right(self):
        """Send right action."""
        self._key(RIGHT)

    def enter(self):
        """Send enter action."""
        self._key(ENTER)

    def back(self):
        """Send back action."""
        self._key(BACK)

    def menu(self):
        """Send menu action."""
        self._key(MENU)

    def volume_up(self):
        """Send volume up action."""
        self._key(VOLUME_UP)

    def volume_down(self):
        """Send volume down action."""
        self._key(VOLUME_DOWN)

    def mute_volume(self):
        """Mute the volume."""
        self._key(MUTE)

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: media commands                      #
    #                                                                         #
    # ======================================================================= #
    def media_play_pause(self):
        """Send media play/pause action."""
        self._key(PLAY_PAUSE)

    def media_play(self):
        """Send media play action."""
        self._key(PLAY)

    def media_pause(self):
        """Send media pause action."""
        self._key(PAUSE)

    def media_stop(self):
        """Send media stop action."""
        self._key(STOP)

    def media_next(self):
        """Send media next action (results in fast-forward)."""
        self._key(NEXT)

    def media_previous(self):
        """Send media previous action (results in rewind)."""
        self._key(PREVIOUS)

    # ======================================================================= #
    #                                                                         #
    #                       "key" methods: key commands                       #
    #                                                                         #
    # ======================================================================= #
    def space(self):
        """Send space keypress."""
        self._key(SPACE)

    def key_0(self):
        """Send 0 keypress."""
        self._key(KEY_0)

    def key_1(self):
        """Send 1 keypress."""
        self._key(KEY_1)

    def key_2(self):
        """Send 2 keypress."""
        self._key(KEY_2)

    def key_3(self):
        """Send 3 keypress."""
        self._key(KEY_3)

    def key_4(self):
        """Send 4 keypress."""
        self._key(KEY_4)

    def key_5(self):
        """Send 5 keypress."""
        self._key(KEY_5)

    def key_6(self):
        """Send 6 keypress."""
        self._key(KEY_6)

    def key_7(self):
        """Send 7 keypress."""
        self._key(KEY_7)

    def key_8(self):
        """Send 8 keypress."""
        self._key(KEY_8)

    def key_9(self):
        """Send 9 keypress."""
        self._key(KEY_9)

    def key_a(self):
        """Send a keypress."""
        self._key(KEY_A)

    def key_b(self):
        """Send b keypress."""
        self._key(KEY_B)

    def key_c(self):
        """Send c keypress."""
        self._key(KEY_C)

    def key_d(self):
        """Send d keypress."""
        self._key(KEY_D)

    def key_e(self):
        """Send e keypress."""
        self._key(KEY_E)

    def key_f(self):
        """Send f keypress."""
        self._key(KEY_F)

    def key_g(self):
        """Send g keypress."""
        self._key(KEY_G)

    def key_h(self):
        """Send h keypress."""
        self._key(KEY_H)

    def key_i(self):
        """Send i keypress."""
        self._key(KEY_I)

    def key_j(self):
        """Send j keypress."""
        self._key(KEY_J)

    def key_k(self):
        """Send k keypress."""
        self._key(KEY_K)

    def key_l(self):
        """Send l keypress."""
        self._key(KEY_L)

    def key_m(self):
        """Send m keypress."""
        self._key(KEY_M)

    def key_n(self):
        """Send n keypress."""
        self._key(KEY_N)

    def key_o(self):
        """Send o keypress."""
        self._key(KEY_O)

    def key_p(self):
        """Send p keypress."""
        self._key(KEY_P)

    def key_q(self):
        """Send q keypress."""
        self._key(KEY_Q)

    def key_r(self):
        """Send r keypress."""
        self._key(KEY_R)

    def key_s(self):
        """Send s keypress."""
        self._key(KEY_S)

    def key_t(self):
        """Send t keypress."""
        self._key(KEY_T)

    def key_u(self):
        """Send u keypress."""
        self._key(KEY_U)

    def key_v(self):
        """Send v keypress."""
        self._key(KEY_V)

    def key_w(self):
        """Send w keypress."""
        self._key(KEY_W)

    def key_x(self):
        """Send x keypress."""
        self._key(KEY_X)

    def key_y(self):
        """Send y keypress."""
        self._key(KEY_Y)

    def key_z(self):
        """Send z keypress."""
        self._key(KEY_Z)
