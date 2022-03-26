"""Constants used throughout the code.

**Links**

* `ADB key event codes <https://developer.android.com/reference/android/view/KeyEvent>`_
* `MediaSession PlaybackState property <https://developer.android.com/reference/android/media/session/PlaybackState.html>`_

"""


import re
import sys

if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
    from enum import IntEnum, unique
else:  # pragma: no cover
    IntEnum = object

    def unique(cls):
        """A class decorator that does nothing."""
        return cls


@unique
class DeviceEnum(IntEnum):
    """An enum for the various device types."""

    BASETV = 0
    ANDROIDTV = 1
    FIRETV = 2


# Intents
INTENT_LAUNCH = "android.intent.category.LEANBACK_LAUNCHER"
INTENT_LAUNCH_FIRETV = "android.intent.category.LAUNCHER"
INTENT_HOME = "android.intent.category.HOME"

# Customizable commands
CUSTOM_AUDIO_STATE = "audio_state"
CUSTOM_CURRENT_APP = "current_app"
CUSTOM_CURRENT_APP_MEDIA_SESSION_STATE = "current_app_media_session_state"
CUSTOM_HDMI_INPUT = "hdmi_input"
CUSTOM_LAUNCH_APP = "launch_app"
CUSTOM_RUNNING_APPS = "running_apps"
CUSTOM_TURN_OFF = "turn_off"
CUSTOM_TURN_ON = "turn_on"
CUSTOMIZABLE_COMMANDS = {
    CUSTOM_AUDIO_STATE,
    CUSTOM_CURRENT_APP,
    CUSTOM_CURRENT_APP_MEDIA_SESSION_STATE,
    CUSTOM_HDMI_INPUT,
    CUSTOM_LAUNCH_APP,
    CUSTOM_RUNNING_APPS,
    CUSTOM_TURN_OFF,
    CUSTOM_TURN_ON,
}

#: The subset of `CUSTOMIZABLE_COMMANDS` that is potentially used in the ``update()`` method
HA_CUSTOMIZABLE_COMMANDS = (
    CUSTOM_AUDIO_STATE,
    CUSTOM_CURRENT_APP_MEDIA_SESSION_STATE,
    CUSTOM_HDMI_INPUT,
    CUSTOM_LAUNCH_APP,
    CUSTOM_RUNNING_APPS,
    CUSTOM_TURN_OFF,
    CUSTOM_TURN_ON,
)

# echo '1' if the previous shell command was successful
CMD_SUCCESS1 = r" && echo -e '1\c'"

# echo '1' if the previous shell command was successful, echo '0' if it was not
CMD_SUCCESS1_FAILURE0 = r" && echo -e '1\c' || echo -e '0\c'"

#: Get the audio state
CMD_AUDIO_STATE = r"dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')"

#: Get the audio state for an Android 11 device
CMD_AUDIO_STATE11 = (
    "CURRENT_AUDIO_STATE=$(dumpsys audio | sed -r -n '/[0-9]{2}-[0-9]{2}.*player piid:.*state:.*$/h; ${x;p;}') && "
    + r"echo $CURRENT_AUDIO_STATE | grep -q paused && echo -e '1\c' || { echo $CURRENT_AUDIO_STATE | grep -q started && echo '2\c' || echo '0\c' ; }"
)

#: Determine whether the device is awake
CMD_AWAKE = "dumpsys power | grep mWakefulness | grep -q Awake"

#: Parse current application identifier from dumpsys output and assign it to ``CURRENT_APP`` variable (assumes dumpsys output is momentarily set to ``CURRENT_APP`` variable)
CMD_PARSE_CURRENT_APP = "CURRENT_APP=${CURRENT_APP#*ActivityRecord{* * } && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP%\\}*}"

#: Parse current application for an Android 11 device
CMD_PARSE_CURRENT_APP11 = "CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* }"

#: Assign focused application identifier to ``CURRENT_APP`` variable
CMD_DEFINE_CURRENT_APP_VARIABLE = (
    "CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp') && " + CMD_PARSE_CURRENT_APP
)
#: Assign focused application identifier to ``CURRENT_APP`` variable for an Android 11 device
CMD_DEFINE_CURRENT_APP_VARIABLE11 = (
    "CURRENT_APP=$(dumpsys window windows | grep 'Window #1') && " + CMD_PARSE_CURRENT_APP11
)


#: Output identifier for current/focused application
CMD_CURRENT_APP = CMD_DEFINE_CURRENT_APP_VARIABLE + " && echo $CURRENT_APP"

#: Output identifier for current/focused application for an Android 11 device
CMD_CURRENT_APP11 = CMD_DEFINE_CURRENT_APP_VARIABLE11 + " && echo $CURRENT_APP"

#: Assign focused application identifier to ``CURRENT_APP`` variable (for a Google TV device)
CMD_DEFINE_CURRENT_APP_VARIABLE_GOOGLE_TV = (
    "CURRENT_APP=$(dumpsys activity a . | grep mResumedActivity) && " + CMD_PARSE_CURRENT_APP
)

#: Output identifier for current/focused application (for a Google TV device)
CMD_CURRENT_APP_GOOGLE_TV = CMD_DEFINE_CURRENT_APP_VARIABLE_GOOGLE_TV + " && echo $CURRENT_APP"

#: Get the HDMI input
CMD_HDMI_INPUT = (
    "dumpsys activity starter | grep -E -o '(ExternalTv|HDMI)InputService/HW[0-9]' -m 1 | grep -o 'HW[0-9]'"
)

#: Get the HDMI input for an Android 11 device
CMD_HDMI_INPUT11 = (
    "(HDMI=$(dumpsys tv_input | grep 'ResourceClientProfile {.*}' | grep -o -E '(hdmi_port=[0-9]|TV)') && { echo ${HDMI/hdmi_port=/HW} | cut -d' ' -f1 ; }) || "
    + CMD_HDMI_INPUT
)

#: Launch an app if it is not already the current app (assumes the variable ``CURRENT_APP`` has already been set)
CMD_LAUNCH_APP_CONDITION = (
    "if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c " + INTENT_LAUNCH + " --pct-syskeys 0 1; fi"
)

#: Launch an app if it is not already the current app (assumes the variable ``CURRENT_APP`` has already been set) on a Fire TV
CMD_LAUNCH_APP_CONDITION_FIRETV = (
    "if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c " + INTENT_LAUNCH_FIRETV + " --pct-syskeys 0 1; fi"
)

#: Launch an app if it is not already the current app
CMD_LAUNCH_APP = (
    CMD_DEFINE_CURRENT_APP_VARIABLE.replace("{", "{{").replace("}", "}}") + " && " + CMD_LAUNCH_APP_CONDITION
)

#: Launch an app if it is not already the current app on an Android 11 device
CMD_LAUNCH_APP11 = (
    CMD_DEFINE_CURRENT_APP_VARIABLE11.replace("{", "{{").replace("}", "}}") + " && " + CMD_LAUNCH_APP_CONDITION
)

#: Launch an app on a Fire TV device
CMD_LAUNCH_APP_FIRETV = (
    CMD_DEFINE_CURRENT_APP_VARIABLE.replace("{", "{{").replace("}", "}}") + " && " + CMD_LAUNCH_APP_CONDITION_FIRETV
)

#: Launch an app on a Google TV device
CMD_LAUNCH_APP_GOOGLE_TV = (
    CMD_DEFINE_CURRENT_APP_VARIABLE_GOOGLE_TV.replace("{", "{{").replace("}", "}}") + " && " + CMD_LAUNCH_APP_CONDITION
)

#: Get the state from ``dumpsys media_session``; this assumes that the variable ``CURRENT_APP`` has been defined
CMD_MEDIA_SESSION_STATE = "dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'"

#: Determine the current app and get the state from ``dumpsys media_session``
CMD_CURRENT_APP_MEDIA_SESSION_STATE = CMD_CURRENT_APP + " && " + CMD_MEDIA_SESSION_STATE

#: Determine the current app and get the state from ``dumpsys media_session`` for an Android 11 device
CMD_CURRENT_APP_MEDIA_SESSION_STATE11 = CMD_CURRENT_APP11 + " && " + CMD_MEDIA_SESSION_STATE

#: Determine the current app and get the state from ``dumpsys media_session`` for a Google TV device
CMD_CURRENT_APP_MEDIA_SESSION_STATE_GOOGLE_TV = CMD_CURRENT_APP_GOOGLE_TV + " && " + CMD_MEDIA_SESSION_STATE

#: Get the running apps for an Android TV device
CMD_RUNNING_APPS_ANDROIDTV = "ps -A | grep u0_a"

#: Get the running apps for a Fire TV device
CMD_RUNNING_APPS_FIRETV = "ps | grep u0_a"

#: Get installed apps
CMD_INSTALLED_APPS = "pm list packages"

#: Determine if the device is on
CMD_SCREEN_ON = (
    "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true')"
)

#: Get the "STREAM_MUSIC" block from ``dumpsys audio``
CMD_STREAM_MUSIC = r"dumpsys audio | grep '\- STREAM_MUSIC:' -A 11"

#: Turn off an Android TV device (note: `KEY_POWER = 26` is defined below)
CMD_TURN_OFF_ANDROIDTV = CMD_SCREEN_ON + " && input keyevent 26"

#: Turn off a Fire TV device (note: `KEY_SLEEP = 223` is defined below)
CMD_TURN_OFF_FIRETV = CMD_SCREEN_ON + " && input keyevent 223"

#: Turn on an Android TV device (note: `KEY_POWER = 26` is defined below)
CMD_TURN_ON_ANDROIDTV = CMD_SCREEN_ON + " || input keyevent 26"

#: Turn on a Fire TV device (note: `KEY_POWER = 26` and `KEY_HOME = 3` are defined below)
CMD_TURN_ON_FIRETV = CMD_SCREEN_ON + " || (input keyevent 26 && input keyevent 3)"

#: Get the wake lock size
CMD_WAKE_LOCK_SIZE = "dumpsys power | grep Locks | grep 'size='"

#: Determine if the device is on, the screen is on, and get the wake lock size
CMD_SCREEN_ON_AWAKE_WAKE_LOCK_SIZE = (
    CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && " + CMD_WAKE_LOCK_SIZE
)

# `getprop` commands
CMD_MANUFACTURER = "getprop ro.product.manufacturer"
CMD_MODEL = "getprop ro.product.model"
CMD_SERIALNO = "getprop ro.serialno"
CMD_VERSION = "getprop ro.build.version.release"

# Commands for getting the MAC address
CMD_MAC_WLAN0 = "ip addr show wlan0 | grep -m 1 ether"
CMD_MAC_ETH0 = "ip addr show eth0 | grep -m 1 ether"

#: The command used for getting the device properties
CMD_DEVICE_PROPERTIES = CMD_MANUFACTURER + " && " + CMD_MODEL + " && " + CMD_SERIALNO + " && " + CMD_VERSION


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
KEYS = {
    "BACK": KEY_BACK,
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
    "YELLOW": KEY_YELLOW,
}


# Android TV / Fire TV states
STATE_ON = "on"
STATE_IDLE = "idle"
STATE_OFF = "off"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_STANDBY = "standby"
STATE_STOPPED = "stopped"
STATE_UNKNOWN = "unknown"

#: States that are valid (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_STATES = (STATE_IDLE, STATE_OFF, STATE_PLAYING, STATE_PAUSED, STATE_STANDBY)

#: Properties that can be used to determine the current state (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_STATE_PROPERTIES = ("audio_state", "media_session_state")

#: Properties that can be checked for custom state detection (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_PROPERTIES = VALID_STATE_PROPERTIES + ("wake_lock_size",)

#: The required type for each entry in :py:const:`VALID_PROPERTIES` (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_PROPERTIES_TYPES = {"audio_state": str, "media_session_state": int, "wake_lock_size": int}

# https://developer.android.com/reference/android/media/session/PlaybackState.html
#: States for the :attr:`~androidtv.basetv.basetv.BaseTV.media_session_state` property
MEDIA_SESSION_STATES = {0: None, 1: STATE_STOPPED, 2: STATE_PAUSED, 3: STATE_PLAYING}


# Apps
APP_AE_TV = "com.aetn.aetv.watch"
APP_AMAZON_PRIME_VIDEO = "com.amazon.avod.thirdpartyclient"
APP_AMAZON_VIDEO = "com.amazon.avod"
APP_APPLE_TV_PLUS = "com.apple.atve.android.appletv"
APP_APPLE_TV_PLUS_FIRETV = "com.apple.atve.amazon.appletv"
APP_APPLE_TV_PLUS_SONY = "com.apple.atve.sony.appletv"
APP_ATV_LAUNCHER = "com.google.android.tvlauncher"
APP_BELL_FIBE = "com.quickplay.android.bellmediaplayer"
APP_CBC_GEM = "ca.cbc.android.cbctv"
APP_COMEDY_CENTRAL = "com.vmn.android.comedycentral"
APP_CRAVE = "ca.bellmedia.cravetv"
APP_DAILYMOTION = "com.dailymotion.dailymotion"
APP_DEEZER = "deezer.android.tv"
APP_DISNEY_PLUS = "com.disney.disneyplus"
APP_DISNEY_PLUS_HOTSTAR = "in.startv.hotstar"
APP_DS_PHOTO = "com.synology.dsphoto"
APP_DS_VIDEO = "com.synology.dsvideo"
APP_ES_FILE_EXPLORER = "com.estrongs.android.pop"
APP_FACEBOOK = "com.facebook.katana"
APP_FAWESOME = "com.future.moviesByFawesomeAndroidTV"
APP_FIREFOX = "org.mozilla.tv.firefox"
APP_FIRETV_PACKAGE_LAUNCHER = "com.amazon.tv.launcher"
APP_FIRETV_PACKAGE_SETTINGS = "com.amazon.tv.settings"
APP_FIRETV_STORE = "com.amazon.venezia"
APP_FOOD_NETWORK_GO = "tv.accedo.foodnetwork"
APP_FRANCE_TV = "fr.francetv.pluzz"
APP_GLOBAL_TV = "com.shawmedia.smglobal"
APP_GOOGLE_CAST = "com.google.android.apps.mediashell"
APP_GOOGLE_TV_LAUNCHER = "com.google.android.apps.tv.launcherx"
APP_HAYSTACK_NEWS = "com.haystack.android"
APP_HBO_GO = "eu.hbogo.androidtv.production"
APP_HBO_GO_2 = "com.HBO"
APP_HOICHOI = "com.viewlift.hoichoi"
APP_HULU = "com.hulu.plus"
APP_HUNGAMA_PLAY = "com.hungama.movies.tv"
APP_IMDB_TV = "com.amazon.imdb.tv.android.app"
APP_IPTV = "ru.iptvremote.android.iptv"
APP_IPTV_SMARTERS_PRO = "com.nst.iptvsmarterstvbox"
APP_JELLYFIN_TV = "org.jellyfin.androidtv"
APP_JIO_CINEMA = "com.jio.media.stb.ondemand"
APP_KODI = "org.xbmc.kodi"
APP_LIVE_CHANNELS = "com.google.android.tv"
APP_MIJN_RADIO = "org.samsonsen.nederlandse.radio.holland.nl"
APP_MOLOTOV = "tv.molotov.app"
APP_MRMC = "tv.mrmc.mrmc"
APP_MRMC_LITE = "tv.mrmc.mrmc.lite"
APP_MX_PLAYER = "com.mxtech.videoplayer.ad"
APP_NETFLIX = "com.netflix.ninja"
APP_NLZIET = "nl.nlziet"
APP_NOS = "nl.nos.app"
APP_NPO = "nl.uitzendinggemist"
APP_OCS = "com.orange.ocsgo"
APP_PLAY_GAMES = "com.google.android.play.games"
APP_PLAY_MUSIC = "com.google.android.music"
APP_PLAY_STORE = "com.android.vending"
APP_PLAY_VIDEOS = "com.google.android.videos"
APP_PLEX = "com.plexapp.android"
APP_PRIME_VIDEO = "com.amazon.amazonvideo.livingroom"
APP_PRIME_VIDEO_FIRETV = "com.amazon.firebat"
APP_SETTINGS = "com.android.tv.settings"
APP_SMART_YOUTUBE_TV = "com.liskovsoft.videomanager"
APP_SONY_ACTION_MENU = "com.sony.dtv.scrums.action"
APP_SONY_ALBUM = "com.sony.dtv.osat.album"
APP_SONY_BRAVIA_SYNC_MENU = "com.sony.dtv.braviasyncmenu"
APP_SONY_BRAVIA_TUTORIALS = "com.sony.dtv.bravialifehack"
APP_SONY_DISCOVER = "com.sony.dtv.discovery"
APP_SONY_HELP = "com.sony.dtv.smarthelp"
APP_SONY_INTERNET_BROWSER = "com.vewd.core.integration.dia"
APP_SONY_LIV = "com.sonyliv"
APP_SONY_MUSIC = "com.sony.dtv.osat.music"
APP_SONY_SCREEN_MIRRORING = "com.sony.dtv.networkapp.wifidirect"
APP_SONY_SELECT = "com.sony.dtv.sonyselect"
APP_SONY_TIMERS = "com.sony.dtv.timers"
APP_SONY_TV = "com.sony.dtv.tvx"
APP_SONY_VIDEO = "com.sony.dtv.osat.video"
APP_SPORT1 = "de.sport1.firetv.video"
APP_SPOTIFY = "com.spotify.tv.android"
APP_STEAM_LINK = "com.valvesoftware.steamlink"
APP_SYFY = "com.amazon.webapps.nbc.syfy"
APP_T2 = "tv.perception.clients.tv.android"
APP_TED = "com.ted.android.tv"
APP_TUNEIN = "tunein.player"
APP_TVHEADEND = "de.cyberdream.dreamepg.tvh.tv.player"
APP_TWITCH = "tv.twitch.android.app"
APP_TWITCH_FIRETV = "tv.twitch.android.viewer"
APP_VEVO = "com.vevo.tv"
APP_VH1 = "com.mtvn.vh1android"
APP_VIMEO = "com.vimeo.android.videoapp"
APP_VLC = "org.videolan.vlc"
APP_VOYO = "com.phonegap.voyo"
APP_VRV = "com.ellation.vrv"
APP_WAIPU_TV = "de.exaring.waipu.firetv.live"
APP_WATCH_TNT = "com.turner.tnt.android.networkapp"
APP_YOUTUBE = "com.google.android.youtube.tv"
APP_YOUTUBE_FIRETV = "com.amazon.firetv.youtube"
APP_YOUTUBE_KIDS = "com.google.android.youtube.tvkids"
APP_YOUTUBE_KIDS_FIRETV = "com.amazon.firetv.youtube.kids"
APP_YOUTUBE_MUSIC = "com.google.android.youtube.tvmusic"
APP_YOUTUBE_TV = "com.google.android.youtube.tvunplugged"
APP_ZEE5 = "com.graymatrix.did"
APP_ZIGGO_GO_TV = "com.ziggo.tv"
APPS = {
    APP_AE_TV: "A&E",
    APP_AMAZON_PRIME_VIDEO: "Amazon Prime Video",
    APP_AMAZON_VIDEO: "Amazon Video",
    APP_APPLE_TV_PLUS: "Apple TV+",
    APP_APPLE_TV_PLUS_FIRETV: "Apple TV+ (Fire TV)",
    APP_APPLE_TV_PLUS_SONY: "Apple TV+ (Sony)",
    APP_ATV_LAUNCHER: "Android TV Launcher",
    APP_BELL_FIBE: "Bell Fibe",
    APP_CBC_GEM: "CBC Gem",
    APP_COMEDY_CENTRAL: "Comedy Central",
    APP_CRAVE: "Crave",
    APP_DAILYMOTION: "Dailymotion",
    APP_DEEZER: "Deezer",
    APP_DISNEY_PLUS: "Disney+",
    APP_DISNEY_PLUS_HOTSTAR: "Disney+ Hotstar",
    APP_DS_PHOTO: "DS photo",
    APP_DS_VIDEO: "DS video",
    APP_ES_FILE_EXPLORER: "ES File Explorer",
    APP_FACEBOOK: "Facebook Watch",
    APP_FAWESOME: "Fawsome",
    APP_FIREFOX: "Firefox",
    APP_FIRETV_STORE: "FireTV Store",
    APP_FOOD_NETWORK_GO: "Food Network GO",
    APP_FRANCE_TV: "France TV",
    APP_GLOBAL_TV: "Global TV",
    APP_GOOGLE_CAST: "Google Cast",
    APP_GOOGLE_TV_LAUNCHER: "Google TV Launcher",
    APP_HAYSTACK_NEWS: "Haystack News",
    APP_HBO_GO: "HBO GO",
    APP_HBO_GO_2: "HBO GO (2)",
    APP_HOICHOI: "Hoichoi",
    APP_HULU: "Hulu",
    APP_HUNGAMA_PLAY: "Hungama Play",
    APP_IMDB_TV: "IMDb TV",
    APP_IPTV: "IPTV",
    APP_IPTV_SMARTERS_PRO: "IPTV Smarters Pro",
    APP_JELLYFIN_TV: "Jellyfin",
    APP_JIO_CINEMA: "Jio Cinema",
    APP_KODI: "Kodi",
    APP_LIVE_CHANNELS: "Live Channels",
    APP_MIJN_RADIO: "Mijn Radio",
    APP_MOLOTOV: "Molotov",
    APP_MRMC: "MrMC",
    APP_MRMC_LITE: "MrMC Lite",
    APP_MX_PLAYER: "MX Player",
    APP_NETFLIX: "Netflix",
    APP_NLZIET: "NLZIET",
    APP_NOS: "NOS",
    APP_NPO: "NPO",
    APP_OCS: "OCS",
    APP_PLAY_GAMES: "Play Games",
    APP_PLAY_MUSIC: "Play Music",
    APP_PLAY_STORE: "Play Store",
    APP_PLAY_VIDEOS: "Play Movies & TV",
    APP_PLEX: "Plex",
    APP_PRIME_VIDEO: "Prime Video",
    APP_PRIME_VIDEO_FIRETV: "Prime Video (FireTV)",
    APP_SETTINGS: "Settings",
    APP_SMART_YOUTUBE_TV: "Smart YouTube TV",
    APP_SONY_ACTION_MENU: "Action Menu",
    APP_SONY_ALBUM: "Album",
    APP_SONY_BRAVIA_SYNC_MENU: "Sync Menu",
    APP_SONY_BRAVIA_TUTORIALS: "BRAVIA Tutorials",
    APP_SONY_DISCOVER: "Discover",
    APP_SONY_HELP: "Help",
    APP_SONY_INTERNET_BROWSER: "Internet Browser",
    APP_SONY_LIV: "SonyLIV",
    APP_SONY_MUSIC: "Music",
    APP_SONY_SCREEN_MIRRORING: "Screen mirroring",
    APP_SONY_SELECT: "Sony Select",
    APP_SONY_TIMERS: "Timers",
    APP_SONY_TV: "TV",
    APP_SONY_VIDEO: "Video",
    APP_SPORT1: "Sport 1",
    APP_SPOTIFY: "Spotify",
    APP_STEAM_LINK: "Steam Link",
    APP_SYFY: "Syfy",
    APP_T2: "T-2 TV",
    APP_TED: "TED",
    APP_TUNEIN: "TuneIn Radio",
    APP_TVHEADEND: "DreamPlayer TVHeadend",
    APP_TWITCH: "Twitch",
    APP_TWITCH_FIRETV: "Twitch (FireTV)",
    APP_VEVO: "Vevo",
    APP_VH1: "VH1",
    APP_VIMEO: "Vimeo",
    APP_VLC: "VLC",
    APP_VOYO: "VOYO",
    APP_VRV: "VRV",
    APP_WAIPU_TV: "Waipu TV",
    APP_WATCH_TNT: "Watch TNT",
    APP_YOUTUBE: "YouTube",
    APP_YOUTUBE_FIRETV: "YouTube (FireTV)",
    APP_YOUTUBE_KIDS: "YouTube Kids",
    APP_YOUTUBE_KIDS_FIRETV: "YouTube Kids (FireTV)",
    APP_YOUTUBE_MUSIC: "YouTube Music",
    APP_YOUTUBE_TV: "YouTube TV",
    APP_ZEE5: "ZEE5",
    APP_ZIGGO_GO_TV: "Ziggo GO TV",
}


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

#: Default transport timeout (in s) for :meth:`adb_shell.handle.tcp_handle.TcpHandle.connect` and :meth:`adb_shell.handle.tcp_handle_async.TcpHandleAsync.connect`
DEFAULT_TRANSPORT_TIMEOUT_S = 1.0

#: Default timeout (in s) for :class:`adb_shell.handle.tcp_handle.TcpHandle` and :class:`adb_shell.handle.tcp_handle_async.TcpHandleAsync`
DEFAULT_ADB_TIMEOUT_S = 9.0

#: Default timeout for acquiring the lock that protects ADB commands
DEFAULT_LOCK_TIMEOUT_S = 3.0
