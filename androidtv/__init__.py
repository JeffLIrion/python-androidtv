#!/usr/bin/env python

"""
Communicate with an Android TV device via ADB over a network.

ADB Debugging must be enabled.
"""

import logging
import re
from socket import error as socket_error

from adb import adb_commands
from adb.sign_pythonrsa import PythonRSASigner
from adb.adb_protocol import InvalidChecksumError
from adb_messenger.client import Client as AdbClient


Signer = PythonRSASigner.FromRSAKeyPath

# Matches window windows output for app & activity name gathering
WINDOW_REGEX = re.compile("Window\{(?P<id>.+?) (?P<user>.+) (?P<package>.+?)(?:\/(?P<activity>.+?))?\}$", re.MULTILINE)

# Regular expression patterns
BLOCK_REGEX_PATTERN = 'STREAM_MUSIC(.*?)- STREAM'
DEVICE_REGEX_PATTERN = 'Devices: (.*?)\W'
MUTED_REGEX_PATTERN = 'Muted: (.*?)\W'
VOLUME_REGEX_PATTERN = '\): (\d{1,})'

PROP_REGEX_PATTERN ='.*?\[(.*?)]'
WIFIMAC_PROP_REGEX_PATTERN = 'wifimac' + PROP_REGEX_PATTERN
WIFIMAC_REGEX_PATTERN = 'ether (.*?) brd'
SERIALNO_REGEX_PATTERN = 'serialno' + PROP_REGEX_PATTERN
MANUF_REGEX_PATTERN = 'manufacturer' + PROP_REGEX_PATTERN
MODEL_REGEX_PATTERN = 'product.model' + PROP_REGEX_PATTERN
VERSION_REGEX_PATTERN = 'version.release' + PROP_REGEX_PATTERN

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

# Fire TV event codes
# MENU = 1
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
    "back": BACK,
    "blue": BLUE,
    "component1": COMPONENT1,
    "component2": COMPONENT2,
    "composite1": COMPOSITE1,
    "composite2": COMPOSITE2,
    "down": DOWN,
    "end": END,
    "enter": ENTER,
    "green": GREEN,
    "hdmi1": HDMI1,
    "hdmi2": HDMI2,
    "hdmi3": HDMI3,
    "hdmi4": HDMI4,
    "home": HOME,
    "input": INPUT,
    "left": LEFT,
    "menu": MENU,
    "move_home": MOVE_HOME,
    "mute": MUTE,
    "pairing": PAIRING,
    "power": POWER,
    "resume": RESUME,
    "right": RIGHT,
    "sat": SAT,
    "search": SEARCH,
    "settings": SETTINGS,
    "sleep": SLEEP,
    "suspend": SUSPEND,
    "sysdown": SYSDOWN,
    "sysleft": SYSLEFT,
    "sysright": SYSRIGHT,
    "sysup": SYSUP,
    "text": TEXT,
    "top": TOP,
    "up": UP,
    "vga": VGA,
    "voldown": VOLUME_DOWN,
    "volup": VOLUME_UP,
    "yellow": YELLOW
}

# Android TV states.
STATE_ON = 'on'
STATE_IDLE = 'idle'
STATE_OFF = 'off'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_STANDBY = 'standby'
STATE_UNKNOWN = 'unknown'

# PACKAGE_LAUNCHER = "com.amazon.tv.launcher"
# PACKAGE_SETTINGS = "com.amazon.tv.settings"
# INTENT_LAUNCH = "android.intent.category.LAUNCHER"
# INTENT_HOME = "android.intent.category.HOME


class AndroidTV:
    """ Represents an Android TV device. """

    def __init__(self, host, adbkey='', adb_server_ip='', adb_server_port=5037):
        """ Initialize AndroidTV object.

        :param host: Host in format <address>:port.
        :param adbkey: The path to the "adbkey" file
        :param adb_server_ip: the IP address for the ADB server
        :param adb_server_port: the port for the ADB server
        """
        self.host = host
        self.adbkey = adbkey
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port

        self.state = STATE_UNKNOWN
        self.muted = False
        self.device = None
        self.volume = 0.
        self.app_id = None
        self.properties = None
        # self.app_name = None

        # keep track of whether the ADB connection is intact
        self._available = False

        # the attributes used for sending ADB commands; filled in in `self.connect()`
        self._adb = None  # python-adb
        self._adb_client = None  # pure-python-adb
        self._adb_device = None  # pure-python-adb

        # the method used for sending ADB commands
        if not self.adb_server_ip:
            # python-adb
            self._adb_shell = self._adb_shell_python_adb
        else:
            # pure-python-adb
            self._adb_shell = self._adb_shell_pure_python_adb

        # establish the ADB connection
        _ = self.connect()

        # get device properties
        if self._available:
            self.properties = self.device_info()

    def connect(self):
        """ Connect to an Android TV device.

        Will attempt to establish ADB connection to the given host.
        Failure sets state to UNKNOWN and disables sending actions.
        """
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
                self._adb = None
                if self._available:
                    self._available = False
                    if serr.strerror is None:
                        serr.strerror = "Timed out trying to connect to ADB device."
                    logging.warning("Couldn't connect to host: %s, error: %s", self.host, serr.strerror)

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

    def update(self):
        """ Update the device status. """
        # Check if device is disconnected.
        if not self.available:
            self.state = STATE_UNKNOWN
            # self.muted = False
            # self.device = None
            # self.volume = 0.
            self.app_id = None
            # self.app_name = None

            # Update was not successful.
            return False

        # Check if device is off.
        elif not self.screen_on:
            self.state = STATE_OFF
            self.app_id = None
            # self.app_name = None

        # Get information from the audio status.
        else:
            audio_output = self._dump('audio')

            if 'started' in audio_output:
                self.state = STATE_PLAYING
            elif 'paused' in audio_output:
                self.state = STATE_PAUSED
            else:
                self.state = STATE_IDLE

            stream_block = re.findall(BLOCK_REGEX_PATTERN, audio_output,
                                      re.DOTALL | re.MULTILINE)[0]
            self.device = re.findall(DEVICE_REGEX_PATTERN, stream_block,
                                     re.DOTALL | re.MULTILINE)[0]
            self.muted = re.findall(MUTED_REGEX_PATTERN, stream_block,
                                    re.DOTALL | re.MULTILINE)[0] == 'true'

            volume_level = re.findall(self.device + VOLUME_REGEX_PATTERN, stream_block,
                                      re.DOTALL | re.MULTILINE)[0]
            self.volume = round(1/15 * float(volume_level), 2)

            self.app_id = self.current_app
            # self.app_name = self.app_id

        # Update was successful.
        return True

    def device_info(self):
        properties = self._adb_shell('getprop')

        if 'wifimac' in properties:
            wifimac = re.findall(WIFIMAC_PROP_REGEX_PATTERN, properties)[0]
        else:
            wifi_out = self._adb_shell('ip addr show wlan0')
            wifimac = re.findall(WIFIMAC_REGEX_PATTERN, wifi_out)[0]
        serialno = re.findall(SERIALNO_REGEX_PATTERN, properties)[0]
        manufacturer = re.findall(MANUF_REGEX_PATTERN, properties)[0]
        model = re.findall(MODEL_REGEX_PATTERN, properties)[0]
        version = re.findall(VERSION_REGEX_PATTERN, properties)[0]

        props = {
            'wifimac': wifimac,
            'serialno': serialno,
            'manufacturer': manufacturer,
            'model': model,
            'sw_version': version}

        return props

    # def app_state(self, app):
    #     """ Informs if application is running """
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
    # @property
    # def state(self):
    #     """ Compute and return the device state.
    #
    #     :returns: Device state.
    #     """
    #     # Check if device is disconnected.
    #     if not self.available:
    #         return STATE_UNKNOWN
    #
    #     # Check if device is off.
    #     if not self.screen_on:
    #         return STATE_OFF
    #
    #     # Get the state from the audio.
    #     return self._audio_state

    @property
    def available(self):
        """ Check whether the ADB connection is intact. """
        if not self.adb_server_ip:
            # python-adb
            return bool(self._adb)

        # pure-python-adb
        try:
            # make sure the server is available
            adb_devices = self._adb_client.devices()

            # make sure the device is available
            try:
                if any([self.host in dev.get_serial_no() for dev in adb_devices]):
                    if not self._available:
                        self._available = True
                    return True
                else:
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
    def current_app(self):
        current_focus = self._dump("window windows", "mCurrentFocus").replace("\r", "")

        matches = WINDOW_REGEX.search(current_focus)
        if matches:
            (pkg, activity) = matches.group('package', 'activity')
            return {"package": pkg, "activity": activity}
        else:
            logging.warning("Couldn't get current app, reply was %s", current_focus)
            return None

    # @property
    # def running_apps(self):
    #     """ Return an array of running user applications """
    #     return self._ps('u0_a')

    @property
    def screen_on(self):
        """ Check if the screen is on. """
        return self._dump_has('power', 'Display Power', 'state=ON')

    @property
    def awake(self):
        """ Check if the device is awake (screen saver is not running). """
        return self._dump_has('power', 'mWakefulness', 'Awake')

    @property
    def wake_lock(self):
        """ Check for wake locks (device is playing). """
        return not self._dump_has('power', 'Locks', 'size=0')

    # @property
    # def launcher(self):
    #     """ Check if the active application is the Amazon TV launcher. """
    #     return self.current_app["package"] == PACKAGE_LAUNCHER

    # @property
    # def settings(self):
    #     """ Check if the active application is the Amazon menu. """
    #     return self.current_app["package"] == PACKAGE_SETTINGS

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    def _adb_shell_python_adb(self, cmd):
        if not self.available:
            return None
        return self._adb.Shell(cmd)

    def _adb_shell_pure_python_adb(self, cmd):
        if not self._available:
            return None
        return self._adb_device.shell(cmd)

    def _input(self, cmd):
        """ Send input to the device.

        :param cmd: Input command.
        """
        self._adb_shell('input {0}'.format(cmd))

    def _dump(self, service, grep=None):
        """ Perform a service dump.

        :param service: Service to dump.
        :param grep: Grep for this string.
        :returns: Dump, optionally grepped.
        """
        if grep:
            return self._adb_shell('dumpsys {0} | grep "{1}"'.format(service, grep))

        return self._adb_shell('dumpsys {0}'.format(service))

    def _dump_has(self, service, grep, search):
        """ Check if a dump has particular content.

        :param service: Service to dump.
        :param grep: Grep for this string.
        :param search: Check for this substring.
        :returns: Found or not.
        """
        dump_grep = self._dump(service, grep=grep)

        if not dump_grep:
            return False

        return dump_grep.strip().find(search) > -1

    # def _send_intent(self, pkg, intent, count=1):
    #     if not self.available:
    #         return None
    #
    #     cmd = 'monkey -p {} -c {} {}; echo $?'.format(pkg, intent, count)
    #     logging.debug("Sending an intent %s to %s (count: %s)", intent, pkg, count)
    #
    #     # adb shell outputs in weird format, so we cut it into lines,
    #     # separate the retcode and return info to the user
    #     res = self._adb_shell(cmd).strip().split("\r\n")
    #     retcode = res[-1]
    #     output = "\n".join(res[:-1])
    #
    #     return {"retcode": retcode, "output": output}

    # def _ps(self, search=''):
    #     """ Perform a ps command with optional filtering.
    #
    #     :param search: Check for this substring.
    #     :returns: List of matching fields
    #     """
    #     if not self.available:
    #         return
    #     result = []
    #     ps = self._adb.StreamingShell('ps')
    #     try:
    #         for bad_line in ps:
    #             # The splitting of the StreamingShell doesn't always work
    #             # this is to ensure that we get only one line
    #             for line in bad_line.splitlines():
    #                 if search in line:
    #                     result.append(line.strip().rsplit(' ',1)[-1])
    #         return result
    #     except InvalidChecksumError as e:
    #         print(e)
    #         self.connect()
    #         raise IOError

    # ======================================================================= #
    #                                                                         #
    #                         Home Assistant services                         #
    #                                                                         #
    # ======================================================================= #
    def input_key(self, key):
        """Input the key to the device."""
        self._adb_shell("input keyevent {}".format(key))

    def start_intent(self, uri):
        """Start an intent on the device."""
        self._adb_shell(
            "am start -a android.intent.action.VIEW -d {}".format(uri))

    def do_action(self, action):
        """Input the key corresponding to the action."""
        self._adb_shell(
            "input keyevent {}".format(ACTIONS[action]))

    # ======================================================================= #
    #                                                                         #
    #                           turn on/off methods                           #
    #                                                                         #
    # ======================================================================= #
    def turn_on(self):
        """ Send power action if device is off. """
        if not self.screen_on:
            self._power()

    def turn_off(self):
        """ Send power action if device is not off. """
        if self.screen_on:
            self._power()

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: basic commands                      #
    #                                                                         #
    # ======================================================================= #
    def _key(self, key):
        """ Send a key event to device.

        :param key: Key constant.
        """
        self._input('keyevent {0}'.format(key))

    def _power(self):
        """ Send power action. """
        self._key(POWER)

    def home(self):
        """ Send home action. """
        self._key(HOME)

    def up(self):
        """ Send up action. """
        self._key(UP)

    def down(self):
        """ Send down action. """
        self._key(DOWN)

    def left(self):
        """ Send left action. """
        self._key(LEFT)

    def right(self):
        """ Send right action. """
        self._key(RIGHT)

    def enter(self):
        """ Send enter action. """
        self._key(ENTER)

    def back(self):
        """ Send back action. """
        self._key(BACK)

    def menu(self):
        """ Send menu action. """
        self._key(MENU)

    def volume_up(self):
        """ Send volume up action. """
        self._key(VOLUME_UP)

    def volume_down(self):
        """ Send volume down action. """
        self._key(VOLUME_DOWN)

    def mute_volume(self):
        """ Mute the volume. """
        self._key(MUTE)

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: media commands                      #
    #                                                                         #
    # ======================================================================= #
    def media_play_pause(self):
        """ Send media play/pause action. """
        self._key(PLAY_PAUSE)

    def media_play(self):
        """ Send media play action. """
        self._key(PLAY)

    def media_pause(self):
        """ Send media pause action. """
        self._key(PAUSE)

    def media_stop(self):
        """ Send media stop action. """
        self._key(STOP)

    def media_next(self):
        """ Send media next action (results in fast-forward). """
        self._key(NEXT)

    def media_previous(self):
        """ Send media previous action (results in rewind). """
        self._key(PREVIOUS)

    # ======================================================================= #
    #                                                                         #
    #                       "key" methods: key commands                       #
    #                                                                         #
    # ======================================================================= #
    def space(self):
        """ Send space keypress. """
        self._key(SPACE)

    def key_0(self):
        """ Send 0 keypress. """
        self._key(KEY_0)

    def key_1(self):
        """ Send 1 keypress. """
        self._key(KEY_1)

    def key_2(self):
        """ Send 2 keypress. """
        self._key(KEY_2)

    def key_3(self):
        """ Send 3 keypress. """
        self._key(KEY_3)

    def key_4(self):
        """ Send 4 keypress. """
        self._key(KEY_4)

    def key_5(self):
        """ Send 5 keypress. """
        self._key(KEY_5)

    def key_6(self):
        """ Send 6 keypress. """
        self._key(KEY_6)

    def key_7(self):
        """ Send 7 keypress. """
        self._key(KEY_7)

    def key_8(self):
        """ Send 8 keypress. """
        self._key(KEY_8)

    def key_9(self):
        """ Send 9 keypress. """
        self._key(KEY_9)

    def key_a(self):
        """ Send a keypress. """
        self._key(KEY_A)

    def key_b(self):
        """ Send b keypress. """
        self._key(KEY_B)

    def key_c(self):
        """ Send c keypress. """
        self._key(KEY_C)

    def key_d(self):
        """ Send d keypress. """
        self._key(KEY_D)

    def key_e(self):
        """ Send e keypress. """
        self._key(KEY_E)

    def key_f(self):
        """ Send f keypress. """
        self._key(KEY_F)

    def key_g(self):
        """ Send g keypress. """
        self._key(KEY_G)

    def key_h(self):
        """ Send h keypress. """
        self._key(KEY_H)

    def key_i(self):
        """ Send i keypress. """
        self._key(KEY_I)

    def key_j(self):
        """ Send j keypress. """
        self._key(KEY_J)

    def key_k(self):
        """ Send k keypress. """
        self._key(KEY_K)

    def key_l(self):
        """ Send l keypress. """
        self._key(KEY_L)

    def key_m(self):
        """ Send m keypress. """
        self._key(KEY_M)

    def key_n(self):
        """ Send n keypress. """
        self._key(KEY_N)

    def key_o(self):
        """ Send o keypress. """
        self._key(KEY_O)

    def key_p(self):
        """ Send p keypress. """
        self._key(KEY_P)

    def key_q(self):
        """ Send q keypress. """
        self._key(KEY_Q)

    def key_r(self):
        """ Send r keypress. """
        self._key(KEY_R)

    def key_s(self):
        """ Send s keypress. """
        self._key(KEY_S)

    def key_t(self):
        """ Send t keypress. """
        self._key(KEY_T)

    def key_u(self):
        """ Send u keypress. """
        self._key(KEY_U)

    def key_v(self):
        """ Send v keypress. """
        self._key(KEY_V)

    def key_w(self):
        """ Send w keypress. """
        self._key(KEY_W)

    def key_x(self):
        """ Send x keypress. """
        self._key(KEY_X)

    def key_y(self):
        """ Send y keypress. """
        self._key(KEY_Y)

    def key_z(self):
        """ Send z keypress. """
        self._key(KEY_Z)
