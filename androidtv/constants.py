"""Constants used in the ``BaseTV``, ``AndroidTV``, and ``FireTV`` classes."""


import re


# echo '1' if the previous shell command was successful
CMD_SUCCESS1 = r" && echo -e '1\c'"

# echo '1' if the previous shell command was successful, echo '0' if it was not
CMD_SUCCESS1_FAILURE0 = r" && echo -e '1\c' || echo -e '0\c'"

# ADB shell commands for getting various properties
CMD_AWAKE = "dumpsys power | grep mWakefulness | grep -q Awake"
CMD_CURRENT_APP = "dumpsys window windows | grep mCurrentFocus"
CMD_MEDIA_SESSION_STATE = "dumpsys media_session | grep -m 1 'state=PlaybackState {'"
CMD_SCREEN_ON = "dumpsys power | grep 'Display Power' | grep -q 'state=ON'"
CMD_WAKE_LOCK = "dumpsys power | grep Locks | grep -q 'size=0'"
CMD_WAKE_LOCK_SIZE = "dumpsys power | grep Locks | grep 'size='"

# `getprop` commands
CMD_MANUFACTURER = "getprop ro.product.manufacturer"
CMD_MODEL = "getprop ro.product.model"
CMD_SERIALNO = "getprop ro.serialno"
CMD_VERSION = "getprop ro.build.version.release"

# Commands for getting the MAC address
CMD_MAC_WLAN0 = "ip addr show wlan0 | grep -m 1 ether"
CMD_MAC_ETH0 = "ip addr show eth0 | grep -m 1 ether"


# ADB key event codes
# https://developer.android.com/reference/android/view/KeyEvent
KEY_BACK = 4
KEY_BLUE = 186
KEY_CENTER = 23
KEY_COMPONENT1 = 249
KEY_COMPONENT2 = 250
KEY_COMPOSITE1 = 247
KEY_COMPOSITE2 = 248
KEY_DOWN = 20
KEY_END = 123
KEY_ENTER = 66
KEY_GREEN = 184
KEY_HDMI1 = 243
KEY_HDMI2 = 244
KEY_HDMI3 = 245
KEY_HDMI4 = 246
KEY_HOME = 3
KEY_INPUT = 178
KEY_LEFT = 21
KEY_MENU = 82
KEY_MOVE_HOME = 122
KEY_MUTE = 164
KEY_NEXT = 87
KEY_PAIRING = 225
KEY_PAUSE = 127
KEY_PLAY = 126
KEY_PLAY_PAUSE = 85
KEY_POWER = 26
KEY_PREVIOUS = 88
KEY_RESUME = 224
KEY_RIGHT = 22
KEY_SAT = 237
KEY_SEARCH = 84
KEY_SETTINGS = 176
KEY_SLEEP = 223
KEY_SPACE = 62
KEY_STOP = 86
KEY_SUSPEND = 276
KEY_SYSDOWN = 281
KEY_SYSLEFT = 282
KEY_SYSRIGHT = 283
KEY_SYSUP = 280
KEY_TEXT = 233
KEY_TOP = 122
KEY_UP = 19
KEY_VGA = 251
KEY_VOLUME_DOWN = 25
KEY_VOLUME_UP = 24
KEY_YELLOW = 185


# Alphanumeric key event codes
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


# Android TV keys
KEYS = {"BACK": KEY_BACK,
        "BLUE": KEY_BLUE,
        "CENTER": KEY_CENTER,
        "COMPONENT1": KEY_COMPONENT1,
        "COMPONENT2": KEY_COMPONENT2,
        "COMPOSITE1": KEY_COMPOSITE1,
        "COMPOSITE2": KEY_COMPOSITE2,
        "DOWN": KEY_DOWN,
        "END": KEY_END,
        "ENTER": KEY_ENTER,
        "GREEN": KEY_GREEN,
        "HDMI1": KEY_HDMI1,
        "HDMI2": KEY_HDMI2,
        "HDMI3": KEY_HDMI3,
        "HDMI4": KEY_HDMI4,
        "HOME": KEY_HOME,
        "INPUT": KEY_INPUT,
        "LEFT": KEY_LEFT,
        "MENU": KEY_MENU,
        "MOVE_HOME": KEY_MOVE_HOME,
        "MUTE": KEY_MUTE,
        "PAIRING": KEY_PAIRING,
        "POWER": KEY_POWER,
        "RESUME": KEY_RESUME,
        "RIGHT": KEY_RIGHT,
        "SAT": KEY_SAT,
        "SEARCH": KEY_SEARCH,
        "SETTINGS": KEY_SETTINGS,
        "SLEEP": KEY_SLEEP,
        "SUSPEND": KEY_SUSPEND,
        "SYSDOWN": KEY_SYSDOWN,
        "SYSLEFT": KEY_SYSLEFT,
        "SYSRIGHT": KEY_SYSRIGHT,
        "SYSUP": KEY_SYSUP,
        "TEXT": KEY_TEXT,
        "TOP": KEY_TOP,
        "UP": KEY_UP,
        "VGA": KEY_VGA,
        "VOLUME_DOWN": KEY_VOLUME_DOWN,
        "VOLUME_UP": KEY_VOLUME_UP,
        "YELLOW": KEY_YELLOW}


# Android TV / Fire TV states
STATE_ON = 'on'
STATE_IDLE = 'idle'
STATE_OFF = 'off'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_STANDBY = 'standby'
STATE_STOPPED = 'stopped'
STATE_UNKNOWN = 'unknown'

# States for the `media_session_state` property
# https://developer.android.com/reference/android/media/session/PlaybackState.html
MEDIA_SESSION_STATES = {0: None,
                        1: STATE_STOPPED,
                        2: STATE_PAUSED,
                        3: STATE_PLAYING}


# Apps
APP_AMAZON_VIDEO = 'com.amazon.avod'
APP_KODI = 'org.xbmc.kodi'
APP_NETFLIX = 'com.netflix.ninja'
APP_VLC = 'org.videolan.vlc'
APPS = {APP_AMAZON_VIDEO: 'Amazon Video',
        APP_KODI: 'Kodi',
        APP_NETFLIX: 'Netflix',
        APP_VLC: 'VLC'}


# Regular expressions
REGEX_MEDIA_SESSION_STATE = re.compile(r"state=(?P<state>[0-9]+)", re.MULTILINE)
REGEX_WINDOW = re.compile(r"Window\{(?P<id>.+?) (?P<user>.+) (?P<package>.+?)(?:\/(?P<activity>.+?))?\}$", re.MULTILINE)

# Regular expression patterns
BLOCK_REGEX_PATTERN = "STREAM_MUSIC(.*?)- STREAM"
DEVICE_REGEX_PATTERN = r"Devices: (.*?)\W"
MUTED_REGEX_PATTERN = r"Muted: (.*?)\W"
VOLUME_REGEX_PATTERN = r"\): (\d{1,})"
MAC_REGEX_PATTERN = "ether (.*?) brd"
