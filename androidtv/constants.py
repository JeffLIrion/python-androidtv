"""Constants used throughout the code.

**Links**

* `ADB key event codes <https://developer.android.com/reference/android/view/KeyEvent>`_
* `MediaSession PlaybackState property <https://developer.android.com/reference/android/media/session/PlaybackState.html>`_

"""


import re


# Intents
INTENT_LAUNCH = "android.intent.category.LAUNCHER"
INTENT_HOME = "android.intent.category.HOME"


# echo '1' if the previous shell command was successful
CMD_SUCCESS1 = r" && echo -e '1\c'"

# echo '1' if the previous shell command was successful, echo '0' if it was not
CMD_SUCCESS1_FAILURE0 = r" && echo -e '1\c' || echo -e '0\c'"

#: Get the audio state
CMD_AUDIO_STATE = r"dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')"

#: Determine whether the device is awake
CMD_AWAKE = "dumpsys power | grep mWakefulness | grep -q Awake"

#: Get the current app
CMD_CURRENT_APP = "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP"

#: Get the current app for a Google TV device
CMD_CURRENT_APP_GOOGLE_TV = "CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP"

#: Get the HDMI input
CMD_HDMI_INPUT = "dumpsys activity starter | grep -o 'HDMIInputService\\/HW[0-9]' -m 1 | grep -o 'HW[0-9]'"

#: Launch an app if it is not already the current app
CMD_LAUNCH_APP = "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${{CURRENT_APP#*{{* * }} && CURRENT_APP=${{CURRENT_APP%%/*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c " + INTENT_LAUNCH + " --pct-syskeys 0 1; fi"

#: Launch an app if it is not already the current app (for Google TV devices)
CMD_LAUNCH_APP_GOOGLE_TV = "CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${{CURRENT_APP%%/*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c " + INTENT_LAUNCH + " --pct-syskeys 0 1; fi"

#: Get the state from ``dumpsys media_session``; this assumes that the variable ``CURRENT_APP`` has been defined
CMD_MEDIA_SESSION_STATE = "dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'"

#: Determine the current app and get the state from ``dumpsys media_session``
CMD_MEDIA_SESSION_STATE_FULL = CMD_CURRENT_APP + " && " + CMD_MEDIA_SESSION_STATE

#: Get the running apps for an Android TV device
CMD_RUNNING_APPS_ANDROIDTV = "ps -A | grep u0_a"

#: Get the running apps for a Fire TV device
CMD_RUNNING_APPS_FIRETV = "ps | grep u0_a"

#: Get installed apps
CMD_INSTALLED_APPS = "pm list packages"

#: Determine if the device is on
CMD_SCREEN_ON = "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true')"

#: Get the "STREAM_MUSIC" block from ``dumpsys audio``
CMD_STREAM_MUSIC = r"dumpsys audio | grep '\- STREAM_MUSIC:' -A 11"

#: Get the wake lock size
CMD_WAKE_LOCK_SIZE = "dumpsys power | grep Locks | grep 'size='"

#: Get the properties for an Android TV device (``lazy=True, get_running_apps=True``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_ANDROIDTV_PROPERTIES_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC + " && " + CMD_RUNNING_APPS_ANDROIDTV

#: Get the properties for an Android TV device (``lazy=True, get_running_apps=False``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_ANDROIDTV_PROPERTIES_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC

#: Get the properties for an Android TV device (``lazy=False, get_running_apps=True``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC + " && " + CMD_RUNNING_APPS_ANDROIDTV

#: Get the properties for an Android TV device (``lazy=False, get_running_apps=False``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC

#: Get the properties for a Google TV device (``lazy=True, get_running_apps=True``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_GOOGLE_TV_PROPERTIES_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP_GOOGLE_TV + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC + " && " + CMD_RUNNING_APPS_ANDROIDTV

#: Get the properties for a Google TV device (``lazy=True, get_running_apps=False``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_GOOGLE_TV_PROPERTIES_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP_GOOGLE_TV + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC

#: Get the properties for a Google TV device (``lazy=False, get_running_apps=True``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP_GOOGLE_TV + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC + " && " + CMD_RUNNING_APPS_ANDROIDTV

#: Get the properties for a Google TV device (``lazy=False, get_running_apps=False``); see :py:meth:`androidtv.androidtv.androidtv_sync.AndroidTVSync.get_properties` and :py:meth:`androidtv.androidtv.androidtv_async.AndroidTVAsync.get_properties`
CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP_GOOGLE_TV + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_STREAM_MUSIC

#: Get the properties for a Fire TV device (``lazy=True, get_running_apps=True``); see :py:meth:`androidtv.firetv.firetv_sync.FireTVSync.get_properties` and :py:meth:`androidtv.firetv.firetv_async.FireTVAsync.get_properties`
CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_RUNNING_APPS_FIRETV

#: Get the properties for a Fire TV device (``lazy=True, get_running_apps=False``); see :py:meth:`androidtv.firetv.firetv_sync.FireTVSync.get_properties` and :py:meth:`androidtv.firetv.firetv_async.FireTVAsync.get_properties`
CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo)"

#: Get the properties for a Fire TV device (``lazy=False, get_running_apps=True``); see :py:meth:`androidtv.firetv.firetv_sync.FireTVSync.get_properties` and :py:meth:`androidtv.firetv.firetv_async.FireTVAsync.get_properties`
CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo) && " + CMD_RUNNING_APPS_FIRETV

#: Get the properties for a Fire TV device (``lazy=False, get_running_apps=False``); see :py:meth:`androidtv.firetv.firetv_sync.FireTVSync.get_properties` and :py:meth:`androidtv.firetv.firetv_async.FireTVAsync.get_properties`
CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && (" + CMD_HDMI_INPUT + " || echo)"

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
KEY_ESCAPE = 111
KEY_FAST_FORWARD = 90
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
KEY_RED = 183
KEY_RESUME = 224
KEY_REWIND = 89
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
KEY_WAKEUP = 224
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
        "ESCAPE": KEY_ESCAPE,
        "FAST_FORWARD": KEY_FAST_FORWARD,
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
        "RED": KEY_RED,
        "RESUME": KEY_RESUME,
        "REWIND": KEY_REWIND,
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
        "WAKEUP": KEY_WAKEUP,
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

#: States that are valid (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_STATES = (STATE_IDLE, STATE_OFF, STATE_PLAYING, STATE_PAUSED, STATE_STANDBY)

#: Properties that can be used to determine the current state (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_STATE_PROPERTIES = ("audio_state", "media_session_state")

#: Properties that can be checked for custom state detection (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_PROPERTIES = VALID_STATE_PROPERTIES + ("wake_lock_size",)

#: The required type for each entry in :py:const:`VALID_PROPERTIES` (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_PROPERTIES_TYPES = {"audio_state": str,
                          "media_session_state": int,
                          "wake_lock_size": int}

# https://developer.android.com/reference/android/media/session/PlaybackState.html
#: States for the :attr:`~androidtv.basetv.basetv.BaseTV.media_session_state` property
MEDIA_SESSION_STATES = {0: None,
                        1: STATE_STOPPED,
                        2: STATE_PAUSED,
                        3: STATE_PLAYING}


# Apps
APP_AE_TV = 'com.aetn.aetv.watch'
APP_AMAZON_VIDEO = 'com.amazon.avod'
APP_AMZ_VIDEO = 'com.amazon.avod.thirdpartyclient'
APP_APPLE_TV = 'com.apple.atve.amazon.appletv'
APP_ATV_LAUNCHER = 'com.google.android.tvlauncher'
APP_BELL_FIBE = 'com.quickplay.android.bellmediaplayer'
APP_COMEDY_CENTRAL = 'com.vmn.android.comedycentral'
APP_DISNEY_PLUS = 'com.disney.disneyplus'
APP_ES_FILE_EXPLORER = 'com.estrongs.android.pop'
APP_FAWESOME = 'com.future.moviesByFawesomeAndroidTV'
APP_FIREFOX = 'org.mozilla.tv.firefox'
APP_FIRETV_PACKAGE_LAUNCHER = 'com.amazon.tv.launcher'
APP_FIRETV_PACKAGE_SETTINGS = 'com.amazon.tv.settings'
APP_FIRETV_STORE = 'com.amazon.venezia'
APP_FOOD_NETWORK_GO = 'tv.accedo.foodnetwork'
APP_FRANCE_TV = 'fr.francetv.pluzz'
APP_GOOGLE_CAST = 'com.google.android.apps.mediashell'
APP_HBO_GO = 'eu.hbogo.androidtv.production'
APP_HBO_GO_2 = 'com.HBO'
APP_HULU = 'com.hulu.plus'
APP_IMDB_TV = 'com.amazon.imdb.tv.android.app'
APP_IPTV_SMARTERS_PRO = 'com.nst.iptvsmarterstvbox'
APP_JELLYFIN_TV = 'org.jellyfin.androidtv'
APP_KODI = 'org.xbmc.kodi'
APP_MOLOTOV = 'tv.molotov.app'
APP_NETFLIX = 'com.netflix.ninja'
APP_OCS = 'com.orange.ocsgo'
APP_PLAY_GAMES = 'com.google.android.games'
APP_PLAY_MUSIC = 'com.google.android.music'
APP_PLAY_STORE = 'com.android.vending'
APP_PLAY_VIDEOS = 'com.android.videos'
APP_PLEX = 'com.plexapp.android'
APP_PRIME_VIDEO = 'com.amazon.amazonvideo.livingroom'
APP_PRIME_VIDEO_2 = 'com.amazon.firebat'
APP_SMART_YOUTUBE_TV = 'com.liskovsoft.videomanager'
APP_SPORT1 = 'de.sport1.firetv.video'
APP_SPOTIFY = 'com.spotify.tv.android'
APP_STEAM_LINK = 'com.valvesoftware.steamlink'
APP_SYFY = 'com.amazon.webapps.nbc.syfy'
APP_TVHEADEND = 'de.cyberdream.dreamepg.tvh.tv.player'
APP_TWITCH = 'tv.twitch.android.viewer'
APP_TWITCH_APP = 'tv.twitch.android.app'
APP_VH1 = 'com.mtvn.vh1android'
APP_VLC = 'org.videolan.vlc'
APP_VRV = 'com.ellation.vrv'
APP_WAIPU_TV = 'de.exaring.waipu.firetv.live'
APP_WATCH_TNT = 'com.turner.tnt.android.networkapp'
APP_YOUTUBE = 'com.google.android.youtube.tv'
APP_YOUTUBE_2 = 'com.amazon.firetv.youtube'
APP_ZIGGO_GO_TV = 'com.ziggo.tv'
APPS = {APP_AE_TV: 'A&E',
        APP_AMAZON_VIDEO: 'Amazon Video',
        APP_AMZ_VIDEO: 'Amz Video',
        APP_APPLE_TV: 'Apple TV',
        APP_ATV_LAUNCHER: 'Android TV Launcher',
        APP_BELL_FIBE: 'Bell Fibe',
        APP_COMEDY_CENTRAL: 'Comedy Central',
        APP_DISNEY_PLUS: 'Disney+',
        APP_ES_FILE_EXPLORER: 'ES File Explorer',
        APP_FAWESOME: 'Fawsome',
        APP_FIREFOX: 'Firefox',
        APP_FIRETV_STORE: 'FireTV Store',
        APP_FOOD_NETWORK_GO: 'Food Network GO',
        APP_FRANCE_TV: 'France TV',
        APP_GOOGLE_CAST: 'Google Cast',
        APP_HBO_GO: 'HBO GO',
        APP_HBO_GO_2: 'HBO GO (2)',
        APP_HULU: 'Hulu',
        APP_IMDB_TV: 'IMDb TV',
        APP_IPTV_SMARTERS_PRO: 'IPTV Smarters Pro',
        APP_JELLYFIN_TV: 'Jellyfin',
        APP_KODI: 'Kodi',
        APP_MOLOTOV: 'Molotov',
        APP_NETFLIX: 'Netflix',
        APP_OCS: 'OCS',
        APP_PLAY_GAMES: 'Play Games',
        APP_PLAY_MUSIC: 'Play Music',
        APP_PLAY_STORE: 'Play Store',
        APP_PLAY_VIDEOS: 'Play Videos',
        APP_PLEX: 'Plex',
        APP_PRIME_VIDEO: 'Prime Video',
        APP_PRIME_VIDEO_2: 'Prime Video (2)',
        APP_SMART_YOUTUBE_TV: 'Smart YouTube TV',
        APP_SPORT1: 'Sport 1',
        APP_SPOTIFY: 'Spotify',
        APP_STEAM_LINK: 'Steam Link',
        APP_SYFY: 'Syfy',
        APP_TVHEADEND: 'DreamPLayer TVHeadend',
        APP_TWITCH: 'Twitch',
        APP_TWITCH_APP: 'Twitch App',
        APP_VH1: 'VH1',
        APP_VLC: 'VLC',
        APP_VRV: 'VRV',
        APP_WAIPU_TV: 'Waipu TV',
        APP_WATCH_TNT: 'Watch TNT',
        APP_YOUTUBE: 'YouTube',
        APP_YOUTUBE_2: 'YouTube (FireTV)',
        APP_ZIGGO_GO_TV: 'Ziggo GO TV'}


# Regular expressions
REGEX_MEDIA_SESSION_STATE = re.compile(r"state=(?P<state>[0-9]+)", re.MULTILINE)
REGEX_WAKE_LOCK_SIZE = re.compile(r"size=(?P<size>[0-9]+)")

# Regular expression patterns
DEVICE_REGEX_PATTERN = r"Devices: (.*?)\W"
MAC_REGEX_PATTERN = "ether (.*?) brd"
MAX_VOLUME_REGEX_PATTERN = r"Max: (\d{1,})"
MUTED_REGEX_PATTERN = r"Muted: (.*?)\W"
STREAM_MUSIC_REGEX_PATTERN = "STREAM_MUSIC(.*?)- STREAM"
VOLUME_REGEX_PATTERN = r"\): (\d{1,})"

#: Default authentication timeout (in s) for :meth:`adb_shell.handle.tcp_handle.TcpHandle.connect` and :meth:`adb_shell.handle.tcp_handle_async.TcpHandleAsync.connect`
DEFAULT_AUTH_TIMEOUT_S = 10.0

#: Default timeout (in s) for :class:`adb_shell.handle.tcp_handle.TcpHandle` and :class:`adb_shell.handle.tcp_handle_async.TcpHandleAsync`
DEFAULT_ADB_TIMEOUT_S = 9.0

#: Default timeout for acquiring the lock that protects ADB commands
DEFAULT_LOCK_TIMEOUT_S = 3.0
