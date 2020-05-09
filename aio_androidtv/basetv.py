"""Communicate with an Android TV or Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging
import re

from . import constants
from .adb_manager import ADBPython

_LOGGER = logging.getLogger(__name__)


class BaseTV(object):
    """Base class for representing an Android TV / Fire TV device.

    The ``state_detection_rules`` parameter is of the format:

    .. code-block:: python

       state_detection_rules = {'com.amazon.tv.launcher': ['standby'],
                                'com.netflix.ninja': ['media_session_state'],
                                'com.ellation.vrv': ['audio_state'],
                                'com.hulu.plus': [{'playing': {'wake_lock_size' : 4}},
                                                  {'paused': {'wake_lock_size': 2}}],
                                'com.plexapp.android': [{'paused': {'media_session_state': 3, 'wake_lock_size': 1}},
                                                        {'playing': {'media_session_state': 3}},
                                                        'standby']}

    The keys are app IDs, and the values are lists of rules that are evaluated in order.

    :py:const:`~aio_androidtv.constants.VALID_STATES`

    .. code-block:: python

       VALID_STATES = ('idle', 'off', 'playing', 'paused', 'standby')


    **Valid rules:**

    * ``'standby'``, ``'playing'``, ``'paused'``, ``'idle'``, or ``'off'`` = always report the specified state when this app is open
    * ``'media_session_state'`` = try to use the :meth:`media_session_state` property to determine the state
    * ``'audio_state'`` = try to use the :meth:`audio_state` property to determine the state
    * ``{'<VALID_STATE>': {'<PROPERTY1>': VALUE1, '<PROPERTY2>': VALUE2, ...}}`` = check if each of the properties is equal to the specified value, and if so return the state

      * The valid properties are ``'media_session_state'``, ``'audio_state'``, and ``'wake_lock_size'``


    Parameters
    ----------
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication
    state_detection_rules : dict, None
        A dictionary of rules for determining the state (see above)

    """

    def __init__(self, host, port=5555, adbkey='', state_detection_rules=None):
        self.host = host
        self.port = int(port)
        self.adbkey = adbkey
        self._state_detection_rules = state_detection_rules
        self.device_properties = {}

        # make sure the rules are valid
        if self._state_detection_rules:
            for app_id, rules in self._state_detection_rules.items():
                if not isinstance(app_id, str):
                    raise TypeError("{0} is of type {1}, not str".format(app_id, type(app_id).__name__))
                state_detection_rules_validator(rules)

        # the max volume level (determined when first getting the volume level)
        self.max_volume = None

        # the handler for ADB commands
        self._adb = ADBPython(host, port, adbkey)

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    @property
    def available(self):
        """Whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        return self._adb.available

    async def adb_shell(self, cmd):
        """Send an ADB command.

        This calls :py:meth:`aio_androidtv.adb_manager.ADBPython.shell`.

        Parameters
        ----------
        cmd : str
            The ADB command to be sent

        Returns
        -------
        str, None
            The response from the device, if there is a response

        """
        return await self._adb.shell(cmd)

    async def adb_pull(self, local_path, device_path):
        """Pull a file from the device.

        This calls :py:meth:`aio_androidtv.adb_manager.ADBPython.pull`.

        Parameters
        ----------
        local_path : str
            The path where the file will be saved
        device_path : str
            The file on the device that will be pulled

        """
        return await self._adb.pull(local_path, device_path)

    async def adb_push(self, local_path, device_path):
        """Push a file to the device.

        This calls :py:meth:`aio_androidtv.adb_manager.ADBPython.push`.

        Parameters
        ----------
        local_path : str
            The file that will be pushed to the device
        device_path : str
            The path where the file will be saved on the device

        """
        return await self._adb.push(local_path, device_path)

    async def adb_screencap(self):
        """Take a screencap.

        This calls :py:meth:`aio_androidtv.adb_manager.ADBPython.screencap`.

        Returns
        -------
        bytes
            The screencap as a binary .png image

        """
        return await self._adb.screencap()

    async def adb_connect(self, always_log_errors=True, auth_timeout_s=constants.DEFAULT_AUTH_TIMEOUT_S):
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
        if isinstance(self._adb, ADBPython):
            return await self._adb.connect(always_log_errors, auth_timeout_s)

    async def adb_close(self):
        """Close the ADB connection.

        """
        await self._adb.close()

    # ======================================================================= #
    #                                                                         #
    #                        Home Assistant device info                       #
    #                                                                         #
    # ======================================================================= #
    async def get_device_properties(self):
        """Return a dictionary of device properties.

        Returns
        -------
        props : dict
            A dictionary with keys ``'wifimac'``, ``'ethmac'``, ``'serialno'``, ``'manufacturer'``, ``'model'``, and ``'sw_version'``

        """
        properties = await self._adb.shell(constants.CMD_MANUFACTURER + " && " +
                                           constants.CMD_MODEL + " && " +
                                           constants.CMD_SERIALNO + " && " +
                                           constants.CMD_VERSION + " && " +
                                           constants.CMD_MAC_WLAN0 + " && " +
                                           constants.CMD_MAC_ETH0)

        _LOGGER.debug("%s:%d `get_device_properties` response: %s", self.host, self.port, properties)

        if not properties:
            return {}

        lines = properties.strip().splitlines()
        if len(lines) != 6:
            return {}

        manufacturer, model, serialno, version, mac_wlan0_output, mac_eth0_output = lines

        if not serialno.strip():
            _LOGGER.warning("Could not obtain serialno for %s:%d, got: '%s'", self.host, self.port, serialno)
            serialno = None

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
    #                         Custom state detection                          #
    #                                                                         #
    # ======================================================================= #
    def _custom_state_detection(self, current_app=None, media_session_state=None, wake_lock_size=None, audio_state=None):
        """Use the rules in ``self._state_detection_rules`` to determine the state.

        Parameters
        ----------
        current_app : str, None
            The :meth:`current_app` property
        media_session_state : int, None
            The :meth:`media_session_state` property
        wake_lock_size : int, None
            The :meth:`wake_lock_size` property
        audio_state : str, None
            The :meth:`audio_state` property

        Returns
        -------
        str, None
            The state, if it could be determined using the rules in ``self._state_detection_rules``; otherwise, ``None``

        """
        if not self._state_detection_rules or current_app is None or current_app not in self._state_detection_rules:
            return None

        rules = self._state_detection_rules[current_app]

        for rule in rules:
            # The state is always the same for this app
            if rule in constants.VALID_STATES:
                return rule

            # Use the `media_session_state` property
            if rule == 'media_session_state':
                if media_session_state == 2:
                    return constants.STATE_PAUSED
                if media_session_state == 3:
                    return constants.STATE_PLAYING
                if media_session_state is not None:
                    return constants.STATE_STANDBY

            # Use the `audio_state` property
            if rule == 'audio_state' and audio_state in constants.VALID_STATES:
                return audio_state

            # Check conditions and if they are true, return the specified state
            if isinstance(rule, dict):
                for state, conditions in rule.items():
                    if state in constants.VALID_STATES and self._conditions_are_true(conditions, media_session_state, wake_lock_size, audio_state):
                        return state

        return None

    @staticmethod
    def _conditions_are_true(conditions, media_session_state=None, wake_lock_size=None, audio_state=None):
        """Check whether the conditions in ``conditions`` are true.

        Parameters
        ----------
        conditions : dict
            A dictionary of conditions to be checked (see the ``state_detection_rules`` parameter in :class:`~aio_androidtv.basetv.BaseTV`)
        media_session_state : int, None
            The :meth:`media_session_state` property
        wake_lock_size : int, None
            The :meth:`wake_lock_size` property
        audio_state : str, None
            The :meth:`audio_state` property

        Returns
        -------
        bool
            Whether or not all the conditions in ``conditions`` are true

        """
        for key, val in conditions.items():
            if key == 'media_session_state':
                if media_session_state is None or media_session_state != val:
                    return False

            elif key == 'wake_lock_size':
                if wake_lock_size is None or wake_lock_size != val:
                    return False

            elif key == 'audio_state':
                if audio_state is None or audio_state != val:
                    return False

            # key is invalid
            else:
                return False

        return True

    # ======================================================================= #
    #                                                                         #
    #                               Properties                                #
    #                                                                         #
    # ======================================================================= #
    async def audio_output_device(self):
        """Get the current audio playback device.

        Returns
        -------
        str, None
            The current audio playback device, or ``None`` if it could not be determined

        """
        stream_music = await self._get_stream_music()

        return self._audio_output_device(stream_music)

    async def audio_state(self):
        """Check if audio is playing, paused, or idle.

        Returns
        -------
        str, None
            The audio state, as determined from the ADB shell command :py:const:`aio_androidtv.constants.CMD_AUDIO_STATE`, or ``None`` if it could not be determined

        """
        audio_state_response = await self._adb.shell(constants.CMD_AUDIO_STATE)
        return self._audio_state(audio_state_response)

    async def awake(self):
        """Check if the device is awake (screensaver is not running).

        Returns
        -------
        bool
            Whether or not the device is awake (screensaver is not running)

        """
        return await self._adb.shell(constants.CMD_AWAKE + constants.CMD_SUCCESS1_FAILURE0) == '1'

    async def current_app(self):
        """Return the current app.

        Returns
        -------
        str, None
            The ID of the current app, or ``None`` if it could not be determined

        """
        current_app_response = await self._adb.shell(constants.CMD_CURRENT_APP)

        return self._current_app(current_app_response)

    async def is_volume_muted(self):
        """Whether or not the volume is muted.

        Returns
        -------
        bool, None
            Whether or not the volume is muted, or ``None`` if it could not be determined

        """
        stream_music = await self._get_stream_music()

        return self._is_volume_muted(stream_music)

    async def media_session_state(self):
        """Get the state from the output of ``dumpsys media_session``.

        Returns
        -------
        int, None
            The state from the output of the ADB shell command ``dumpsys media_session``, or ``None`` if it could not be determined

        """
        media_session_state_response = await self._adb.shell(constants.CMD_MEDIA_SESSION_STATE_FULL)

        _, media_session_state = self._current_app_media_session_state(media_session_state_response)

        return media_session_state

    async def screen_on(self):
        """Check if the screen is on.

        Returns
        -------
        bool
            Whether or not the device is on

        """
        return await self._adb.shell(constants.CMD_SCREEN_ON + constants.CMD_SUCCESS1_FAILURE0) == '1'

    async def volume(self):
        """Get the absolute volume level.

        Returns
        -------
        int, None
            The absolute volume level, or ``None`` if it could not be determined

        """
        stream_music = await self._get_stream_music()
        audio_output_device = self._audio_output_device(stream_music)

        return self._volume(stream_music, audio_output_device)

    async def volume_level(self):
        """Get the relative volume level.

        Returns
        -------
        float, None
            The volume level (between 0 and 1), or ``None`` if it could not be determined

        """
        volume = await self.volume()

        return self._volume_level(volume)

    async def wake_lock_size(self):
        """Get the size of the current wake lock.

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        wake_lock_size_response = await self._adb.shell(constants.CMD_WAKE_LOCK_SIZE)

        return self._wake_lock_size(wake_lock_size_response)

    # ======================================================================= #
    #                                                                         #
    #                            Parse properties                             #
    #                                                                         #
    # ======================================================================= #
    @staticmethod
    def _audio_output_device(stream_music):
        """Get the current audio playback device from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``

        Returns
        -------
        str, None
            The current audio playback device, or ``None`` if it could not be determined

        """
        if not stream_music:
            return None

        assert isinstance(stream_music, str), "stream_music is of type {}".format(type(stream_music))
        matches = re.findall(constants.DEVICE_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0]

        return None

    @staticmethod
    def _audio_state(audio_state_response):
        """Parse the :meth:`audio_state` property from the output of the command :py:const:`aio_androidtv.constants.CMD_AUDIO_STATE`.

        Parameters
        ----------
        audio_state_response : str, None
            The output of the command :py:const:`aio_androidtv.constants.CMD_AUDIO_STATE`

        Returns
        -------
        str, None
            The audio state, or ``None`` if it could not be determined

        """
        if not audio_state_response:
            return None
        if audio_state_response == '1':
            return constants.STATE_PAUSED
        if audio_state_response == '2':
            return constants.STATE_PLAYING
        return constants.STATE_IDLE

    @staticmethod
    def _current_app(current_app_response):
        """Get the current app from the output of the command :py:const:`aio_androidtv.constants.CMD_CURRENT_APP`.

        Parameters
        ----------
        current_app_response : str, None
            The output from the ADB command :py:const:`aio_androidtv.constants.CMD_CURRENT_APP`

        Returns
        -------
        str, None
            The current app, or ``None`` if it could not be determined

        """
        if not current_app_response or '=' in current_app_response or '{' in current_app_response:
            return None

        return current_app_response

    @staticmethod
    def _current_app_media_session_state(media_session_state_response):
        """Get the current app and the media session state properties from the output of :py:const:`aio_androidtv.constants.CMD_MEDIA_SESSION_STATE_FULL`.

        Parameters
        ----------
        media_session_state_response : str, None
            The output of :py:const:`aio_androidtv.constants.CMD_MEDIA_SESSION_STATE_FULL`

        Returns
        -------
        current_app : str, None
            The current app, or ``None`` if it could not be determined
        media_session_state : int, None
            The state from the output of the ADB shell command, or ``None`` if it could not be determined

        """
        if not media_session_state_response:
            return None, None

        lines = media_session_state_response.splitlines()

        current_app = BaseTV._current_app(lines[0].strip())

        if len(lines) > 1:
            media_session_state = BaseTV._media_session_state(lines[1], current_app)
        else:
            media_session_state = None

        return current_app, media_session_state

    async def _get_stream_music(self, stream_music_raw=None):
        """Get the ``STREAM_MUSIC`` block from the output of the command :py:const:`aio_androidtv.constants.CMD_STREAM_MUSIC`.

        Parameters
        ----------
        stream_music_raw : str, None
            The output of the command :py:const:`aio_androidtv.constants.CMD_STREAM_MUSIC`

        Returns
        -------
        str, None
            The ``STREAM_MUSIC`` block from the output of :py:const:`aio_androidtv.constants.CMD_STREAM_MUSIC`, or ``None`` if it could not be determined

        """
        if not stream_music_raw:
            stream_music_raw = await self._adb.shell(constants.CMD_STREAM_MUSIC)

        if not stream_music_raw:
            return None

        matches = re.findall(constants.STREAM_MUSIC_REGEX_PATTERN, stream_music_raw, re.DOTALL | re.MULTILINE)
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
    def _media_session_state(media_session_state_response, current_app):
        """Get the state from the output of :py:const:`aio_androidtv.constants.CMD_MEDIA_SESSION_STATE`.

        Parameters
        ----------
        media_session_state_response : str, None
            The output of :py:const:`aio_androidtv.constants.CMD_MEDIA_SESSION_STATE`
        current_app : str, None
            The current app, or ``None`` if it could not be determined

        Returns
        -------
        int, None
            The state from the output of the ADB shell command, or ``None`` if it could not be determined

        """
        if not media_session_state_response or not current_app:
            return None

        matches = constants.REGEX_MEDIA_SESSION_STATE.search(media_session_state_response)
        if matches:
            return int(matches.group('state'))

        return None

    @staticmethod
    def _running_apps(running_apps_response):
        """Get the running apps from the output of :py:const:`aio_androidtv.constants.CMD_RUNNING_APPS`.

        Parameters
        ----------
        running_apps_response : str, None
            The output of :py:const:`aio_androidtv.constants.CMD_RUNNING_APPS`

        Returns
        -------
        list, None
            A list of the running apps, or ``None`` if it could not be determined

        """
        if running_apps_response:
            if isinstance(running_apps_response, list):
                return [line.strip().rsplit(' ', 1)[-1] for line in running_apps_response if line.strip()]
            return [line.strip().rsplit(' ', 1)[-1] for line in running_apps_response.splitlines() if line.strip()]

        return None

    def _volume(self, stream_music, audio_output_device):
        """Get the absolute volume level from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``
        audio_output_device : str, None
            The current audio playback device

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

        if not audio_output_device:
            return None

        volume_matches = re.findall(audio_output_device + constants.VOLUME_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
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
    def _wake_lock_size(wake_lock_size_response):
        """Get the size of the current wake lock from the output of :py:const:`aio_androidtv.constants.CMD_WAKE_LOCK_SIZE`.

        Parameters
        ----------
        wake_lock_size_response : str, None
            The output of :py:const:`aio_androidtv.constants.CMD_WAKE_LOCK_SIZE`

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        if wake_lock_size_response:
            wake_lock_size_matches = constants.REGEX_WAKE_LOCK_SIZE.search(wake_lock_size_response)
            if wake_lock_size_matches:
                return int(wake_lock_size_matches.group('size'))

        return None

    # ======================================================================= #
    #                                                                         #
    #                               App methods                               #
    #                                                                         #
    # ======================================================================= #
    async def _send_intent(self, pkg, intent, count=1):
        """Send an intent to the device.

        Parameters
        ----------
        pkg : str
            The command that will be sent is ``monkey -p <pkg> -c <intent> <count>; echo $?``
        intent : str
            The command that will be sent is ``monkey -p <pkg> -c <intent> <count>; echo $?``
        count : int, str
            The command that will be sent is ``monkey -p <pkg> -c <intent> <count>; echo $?``

        Returns
        -------
        dict
            A dictionary with keys ``'output'`` and ``'retcode'``, if they could be determined; otherwise, an empty dictionary

        """
        cmd = 'monkey -p {} -c {} {}; echo $?'.format(pkg, intent, count)

        # adb shell outputs in weird format, so we cut it into lines,
        # separate the retcode and return info to the user
        res = await self._adb.shell(cmd)
        if res is None:
            return {}

        res = res.strip().split("\r\n")
        retcode = res[-1]
        output = "\n".join(res[:-1])

        return {"output": output, "retcode": retcode}

    async def launch_app(self, app):
        """Launch an app.

        Parameters
        ----------
        app : str
            The ID of the app that will be launched

        """
        await self._adb.shell(constants.CMD_LAUNCH_APP.format(app))

    async def stop_app(self, app):
        """Stop an app.

        Parameters
        ----------
        app : str
            The ID of the app that will be stopped

        Returns
        -------
        str, None
            The output of the ``am force-stop`` ADB shell command, or ``None`` if the device is unavailable

        """
        return await self._adb.shell("am force-stop {0}".format(app))

    async def start_intent(self, uri):
        """Start an intent on the device.

        Parameters
        ----------
        uri : str
            The intent that will be sent is ``am start -a android.intent.action.VIEW -d <uri>``

        """
        await self._adb.shell("am start -a android.intent.action.VIEW -d {}".format(uri))

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: basic commands                      #
    #                                                                         #
    # ======================================================================= #
    async def _key(self, key):
        """Send a key event to device.

        Parameters
        ----------
        key : str, int
            The Key constant

        """
        await self._adb.shell('input keyevent {0}'.format(key))

    async def power(self):
        """Send power action."""
        await self._key(constants.KEY_POWER)

    async def sleep(self):
        """Send sleep action."""
        await self._key(constants.KEY_SLEEP)

    async def home(self):
        """Send home action."""
        await self._key(constants.KEY_HOME)

    async def up(self):
        """Send up action."""
        await self._key(constants.KEY_UP)

    async def down(self):
        """Send down action."""
        await self._key(constants.KEY_DOWN)

    async def left(self):
        """Send left action."""
        await self._key(constants.KEY_LEFT)

    async def right(self):
        """Send right action."""
        await self._key(constants.KEY_RIGHT)

    async def enter(self):
        """Send enter action."""
        await self._key(constants.KEY_ENTER)

    async def back(self):
        """Send back action."""
        await self._key(constants.KEY_BACK)

    async def menu(self):
        """Send menu action."""
        await self._key(constants.KEY_MENU)

    async def mute_volume(self):
        """Mute the volume."""
        await self._key(constants.KEY_MUTE)

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: media commands                      #
    #                                                                         #
    # ======================================================================= #
    async def media_play(self):
        """Send media play action."""
        await self._key(constants.KEY_PLAY)

    async def media_pause(self):
        """Send media pause action."""
        await self._key(constants.KEY_PAUSE)

    async def media_play_pause(self):
        """Send media play/pause action."""
        await self._key(constants.KEY_PLAY_PAUSE)

    async def media_stop(self):
        """Send media stop action."""
        await self._key(constants.KEY_STOP)

    async def media_next_track(self):
        """Send media next action (results in fast-forward)."""
        await self._key(constants.KEY_NEXT)

    async def media_previous_track(self):
        """Send media previous action (results in rewind)."""
        await self._key(constants.KEY_PREVIOUS)

    # ======================================================================= #
    #                                                                         #
    #                   "key" methods: alphanumeric commands                  #
    #                                                                         #
    # ======================================================================= #
    async def space(self):
        """Send space keypress."""
        await self._key(constants.KEY_SPACE)

    async def key_0(self):
        """Send 0 keypress."""
        await self._key(constants.KEY_0)

    async def key_1(self):
        """Send 1 keypress."""
        await self._key(constants.KEY_1)

    async def key_2(self):
        """Send 2 keypress."""
        await self._key(constants.KEY_2)

    async def key_3(self):
        """Send 3 keypress."""
        await self._key(constants.KEY_3)

    async def key_4(self):
        """Send 4 keypress."""
        await self._key(constants.KEY_4)

    async def key_5(self):
        """Send 5 keypress."""
        await self._key(constants.KEY_5)

    async def key_6(self):
        """Send 6 keypress."""
        await self._key(constants.KEY_6)

    async def key_7(self):
        """Send 7 keypress."""
        await self._key(constants.KEY_7)

    async def key_8(self):
        """Send 8 keypress."""
        await self._key(constants.KEY_8)

    async def key_9(self):
        """Send 9 keypress."""
        await self._key(constants.KEY_9)

    async def key_a(self):
        """Send a keypress."""
        await self._key(constants.KEY_A)

    async def key_b(self):
        """Send b keypress."""
        await self._key(constants.KEY_B)

    async def key_c(self):
        """Send c keypress."""
        await self._key(constants.KEY_C)

    async def key_d(self):
        """Send d keypress."""
        await self._key(constants.KEY_D)

    async def key_e(self):
        """Send e keypress."""
        await self._key(constants.KEY_E)

    async def key_f(self):
        """Send f keypress."""
        await self._key(constants.KEY_F)

    async def key_g(self):
        """Send g keypress."""
        await self._key(constants.KEY_G)

    async def key_h(self):
        """Send h keypress."""
        await self._key(constants.KEY_H)

    async def key_i(self):
        """Send i keypress."""
        await self._key(constants.KEY_I)

    async def key_j(self):
        """Send j keypress."""
        await self._key(constants.KEY_J)

    async def key_k(self):
        """Send k keypress."""
        await self._key(constants.KEY_K)

    async def key_l(self):
        """Send l keypress."""
        await self._key(constants.KEY_L)

    async def key_m(self):
        """Send m keypress."""
        await self._key(constants.KEY_M)

    async def key_n(self):
        """Send n keypress."""
        await self._key(constants.KEY_N)

    async def key_o(self):
        """Send o keypress."""
        await self._key(constants.KEY_O)

    async def key_p(self):
        """Send p keypress."""
        await self._key(constants.KEY_P)

    async def key_q(self):
        """Send q keypress."""
        await self._key(constants.KEY_Q)

    async def key_r(self):
        """Send r keypress."""
        await self._key(constants.KEY_R)

    async def key_s(self):
        """Send s keypress."""
        await self._key(constants.KEY_S)

    async def key_t(self):
        """Send t keypress."""
        await self._key(constants.KEY_T)

    async def key_u(self):
        """Send u keypress."""
        await self._key(constants.KEY_U)

    async def key_v(self):
        """Send v keypress."""
        await self._key(constants.KEY_V)

    async def key_w(self):
        """Send w keypress."""
        await self._key(constants.KEY_W)

    async def key_x(self):
        """Send x keypress."""
        await self._key(constants.KEY_X)

    async def key_y(self):
        """Send y keypress."""
        await self._key(constants.KEY_Y)

    async def key_z(self):
        """Send z keypress."""
        await self._key(constants.KEY_Z)

    # ======================================================================= #
    #                                                                         #
    #                              volume methods                             #
    #                                                                         #
    # ======================================================================= #
    async def set_volume_level(self, volume_level):
        """Set the volume to the desired level.

        Parameters
        ----------
        volume_level : float
            The new volume level (between 0 and 1)

        Returns
        -------
        float, None
            The new volume level (between 0 and 1), or ``None`` if ``self.max_volume`` could not be determined

        """
        # if necessary, determine the max volume
        if not self.max_volume:
            _ = await self.volume()
            if not self.max_volume:
                return None

        new_volume = int(min(max(round(self.max_volume * volume_level), 0.), self.max_volume))

        await self._adb.shell("media volume --show --stream 3 --set {}".format(new_volume))

        # return the new volume level
        return new_volume / self.max_volume

    async def volume_up(self, current_volume_level=None):
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
            current_volume = await self.volume()
        else:
            current_volume = round(self.max_volume * current_volume_level)

        # send the volume up command
        await self._key(constants.KEY_VOLUME_UP)

        # if `self.max_volume` or `current_volume` could not be determined, return `None` as the new `volume_level`
        if not self.max_volume or current_volume is None:
            return None

        # return the new volume level
        return min(current_volume + 1, self.max_volume) / self.max_volume

    async def volume_down(self, current_volume_level=None):
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
            current_volume = await self.volume()
        else:
            current_volume = round(self.max_volume * current_volume_level)

        # send the volume down command
        await self._key(constants.KEY_VOLUME_DOWN)

        # if `self.max_volume` or `current_volume` could not be determined, return `None` as the new `volume_level`
        if not self.max_volume or current_volume is None:
            return None

        # return the new volume level
        return max(current_volume - 1, 0.) / self.max_volume


# ======================================================================= #
#                                                                         #
#                    Validate the state detection rules                   #
#                                                                         #
# ======================================================================= #
def state_detection_rules_validator(rules, exc=KeyError):
    """Validate the rules (i.e., the ``state_detection_rules`` value) for a given app ID (i.e., a key in ``state_detection_rules``).

    For each ``rule`` in ``rules``, this function checks that:

    * ``rule`` is a string or a dictionary
    * If ``rule`` is a string:

        * Check that ``rule`` is in :py:const:`~aio_androidtv.constants.VALID_STATES` or :py:const:`~aio_androidtv.constants.VALID_STATE_PROPERTIES`

    * If ``rule`` is a dictionary:

        * Check that each key is in :py:const:`~aio_androidtv.constants.VALID_STATES`
        * Check that each value is a dictionary

            * Check that each key is in :py:const:`~aio_androidtv.constants.VALID_PROPERTIES`
            * Check that each value is of the right type, according to :py:const:`~aio_androidtv.constants.VALID_PROPERTIES_TYPES`

    See :class:`~aio_androidtv.basetv.BaseTV` for more info about the ``state_detection_rules`` parameter.

    Parameters
    ----------
    rules : list
        A list of the rules that will be used to determine the state
    exc : Exception
        The exception that will be raised if a rule is invalid

    Returns
    -------
    rules : list
        The provided list of rules

    """
    for rule in rules:
        # A rule must be either a string or a dictionary
        if not isinstance(rule, (str, dict)):
            raise exc("Expected a string or a map, got {}".format(type(rule).__name__))

        # If a rule is a string, check that it is valid
        if isinstance(rule, str):
            if rule not in constants.VALID_STATE_PROPERTIES + constants.VALID_STATES:
                raise exc("Invalid rule '{0}' is not in {1}".format(rule, constants.VALID_STATE_PROPERTIES + constants.VALID_STATES))

        # If a rule is a dictionary, check that it is valid
        else:
            for state, conditions in rule.items():
                # The keys of the dictionary must be valid states
                if state not in constants.VALID_STATES:
                    raise exc("'{0}' is not a valid state for the 'state_detection_rules' parameter".format(state))

                # The values of the dictionary must be dictionaries
                if not isinstance(conditions, dict):
                    raise exc("Expected a map for entry '{0}' in 'state_detection_rules', got {1}".format(state, type(conditions).__name__))

                for prop, value in conditions.items():
                    # The keys of the dictionary must be valid properties that can be checked
                    if prop not in constants.VALID_PROPERTIES:
                        raise exc("Invalid property '{0}' is not in {1}".format(prop, constants.VALID_PROPERTIES))

                    # Make sure the value is of the right type
                    if not isinstance(value, constants.VALID_PROPERTIES_TYPES[prop]):
                        raise exc("Conditional value for property '{0}' must be of type {1}, not {2}".format(prop, constants.VALID_PROPERTIES_TYPES[prop].__name__, type(value).__name__))

    return rules
