"""Communicate with an Android TV or Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging
import re

from .. import constants

_LOGGER = logging.getLogger(__name__)


class BaseTV(object):  # pylint: disable=too-few-public-methods
    """Base class for representing an Android TV / Fire TV device.

    The ``state_detection_rules`` parameter is of the format:

    .. code-block:: python

       state_detection_rules = {'com.amazon.tv.launcher': ['idle'],
                                'com.netflix.ninja': ['media_session_state'],
                                'com.ellation.vrv': ['audio_state'],
                                'com.hulu.plus': [{'playing': {'wake_lock_size' : 4}},
                                                  {'paused': {'wake_lock_size': 2}}],
                                'com.plexapp.android': [{'paused': {'media_session_state': 3, 'wake_lock_size': 1}},
                                                        {'playing': {'media_session_state': 3}},
                                                        'idle']}

    The keys are app IDs, and the values are lists of rules that are evaluated in order.

    :py:const:`~androidtv.constants.VALID_STATES`

    .. code-block:: python

       VALID_STATES = ('idle', 'off', 'playing', 'paused', 'standby')


    **Valid rules:**

    * ``'idle'``, ``'playing'``, ``'paused'``, ``'standby'``, or ``'off'`` = always report the specified state when this app is open
    * ``'media_session_state'`` = try to use the :meth:`media_session_state` property to determine the state
    * ``'audio_state'`` = try to use the :meth:`audio_state` property to determine the state
    * ``{'<VALID_STATE>': {'<PROPERTY1>': VALUE1, '<PROPERTY2>': VALUE2, ...}}`` = check if each of the properties is equal to the specified value, and if so return the state

      * The valid properties are ``'media_session_state'``, ``'audio_state'``, and ``'wake_lock_size'``


    Parameters
    ----------
    adb : ADBPythonSync, ADBServerSync, ADBPythonAsync, ADBServerAsync
        The handler for ADB commands
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication
    adb_server_ip : str
        The IP address of the ADB server
    adb_server_port : int
        The port for the ADB server
    state_detection_rules : dict, None
        A dictionary of rules for determining the state (see above)

    """

    DEVICE_ENUM = constants.DeviceEnum.BASETV

    def __init__(
        self, adb, host, port=5555, adbkey="", adb_server_ip="", adb_server_port=5037, state_detection_rules=None
    ):
        self._adb = adb
        self.host = host
        self.port = int(port)
        self.adbkey = adbkey
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port
        self._state_detection_rules = state_detection_rules
        self.device_properties = {}
        self.installed_apps = []

        # make sure the rules are valid
        if self._state_detection_rules:
            for app_id, rules in self._state_detection_rules.items():
                if not isinstance(app_id, str):
                    raise TypeError("{0} is of type {1}, not str".format(app_id, type(app_id).__name__))
                state_detection_rules_validator(rules)

        # the max volume level (determined when first getting the volume level)
        self.max_volume = None

        # Customizable commands
        self._custom_commands = {}

    # ======================================================================= #
    #                                                                         #
    #                      Device-specific ADB commands                       #
    #                                                                         #
    # ======================================================================= #
    def customize_command(self, custom_command, value):
        """Customize a command used to retrieve properties.

        Parameters
        ----------
        custom_command : str
            The name of the command that will be customized; it must be in `constants.CUSTOMIZABLE_COMMANDS`
        value : str, None
            The custom ADB command that will be used, or ``None`` if the custom command should be deleted

        """
        if custom_command in constants.CUSTOMIZABLE_COMMANDS:
            if value is not None:
                self._custom_commands[custom_command] = value
            elif custom_command in self._custom_commands:
                del self._custom_commands[custom_command]

    def _cmd_audio_state(self):
        """Get the command used to retrieve the current audio state for this device.

        Returns
        -------
        str
            The device-specific ADB shell command used to determine the current audio state

        """
        if constants.CUSTOM_AUDIO_STATE in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_AUDIO_STATE]

        # Is this an Android 11 device?
        if self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV and self.device_properties.get("sw_version", "") == "11":
            return constants.CMD_AUDIO_STATE11
        return constants.CMD_AUDIO_STATE

    def _cmd_current_app(self):
        """Get the command used to retrieve the current app for this device.

        Returns
        -------
        str
            The device-specific ADB shell command used to determine the current app

        """
        if constants.CUSTOM_CURRENT_APP in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_CURRENT_APP]

        # Is this a Google Chromecast Android TV?
        if (
            self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV
            and "Google" in self.device_properties.get("manufacturer", "")
            and "Chromecast" in self.device_properties.get("model", "")
        ):
            return constants.CMD_CURRENT_APP_GOOGLE_TV

        # Is this an Android 11 device?
        if self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV and self.device_properties.get("sw_version", "") == "11":
            return constants.CMD_CURRENT_APP11

        return constants.CMD_CURRENT_APP

    def _cmd_current_app_media_session_state(self):
        """Get the command used to retrieve the current app and media session state for this device.

        Returns
        -------
        str
            The device-specific ADB shell command used to determine the current app and media session state

        """
        if constants.CUSTOM_CURRENT_APP_MEDIA_SESSION_STATE in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_CURRENT_APP_MEDIA_SESSION_STATE]

        # Is this a Google Chromecast Android TV?
        if (
            self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV
            and "Google" in self.device_properties.get("manufacturer", "")
            and "Chromecast" in self.device_properties.get("model", "")
        ):
            return constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE_GOOGLE_TV

        # Is this an Android 11 device?
        if self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV and self.device_properties.get("sw_version", "") == "11":
            return constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE11

        return constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE

    def _cmd_hdmi_input(self):
        """Get the command used to retrieve the current HDMI input for this device.

        Returns
        -------
        str
            The device-specific ADB shell command used to determine the current HDMI input

        """
        if constants.CUSTOM_HDMI_INPUT in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_HDMI_INPUT]

        # Is this an Android 11 device?
        if self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV and self.device_properties.get("sw_version", "") == "11":
            return constants.CMD_HDMI_INPUT11

        return constants.CMD_HDMI_INPUT

    def _cmd_launch_app(self, app):
        """Get the command to launch the specified app for this device.

        Parameters
        ----------
        app : str
            The app that will be launched

        Returns
        -------
        str
            The device-specific command to launch the app

        """
        if constants.CUSTOM_LAUNCH_APP in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_LAUNCH_APP].format(app)

        # Is this a Google Chromecast Android TV?
        if (
            self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV
            and "Google" in self.device_properties.get("manufacturer", "")
            and "Chromecast" in self.device_properties.get("model", "")
        ):
            return constants.CMD_LAUNCH_APP_GOOGLE_TV.format(app)

        if self.DEVICE_ENUM == constants.DeviceEnum.FIRETV:
            return constants.CMD_LAUNCH_APP_FIRETV.format(app)

        # Is this an Android 11 device?
        if self.DEVICE_ENUM == constants.DeviceEnum.ANDROIDTV and self.device_properties.get("sw_version", "") == "11":
            return constants.CMD_LAUNCH_APP11.format(app)

        return constants.CMD_LAUNCH_APP.format(app)

    def _cmd_running_apps(self):
        """Get the command used to retrieve the running apps for this device.

        Returns
        -------
        str
            The device-specific ADB shell command used to determine the running apps

        """
        if constants.CUSTOM_RUNNING_APPS in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_RUNNING_APPS]

        if self.DEVICE_ENUM == constants.DeviceEnum.FIRETV:
            return constants.CMD_RUNNING_APPS_FIRETV

        return constants.CMD_RUNNING_APPS_ANDROIDTV

    def _cmd_turn_off(self):
        """Get the command used to turn off this device.

        Returns
        -------
        str
            The device-specific ADB shell command used to turn off the device

        """
        if constants.CUSTOM_TURN_OFF in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_TURN_OFF]

        if self.DEVICE_ENUM == constants.DeviceEnum.FIRETV:
            return constants.CMD_TURN_OFF_FIRETV

        return constants.CMD_TURN_OFF_ANDROIDTV

    def _cmd_turn_on(self):
        """Get the command used to turn on this device.

        Returns
        -------
        str
            The device-specific ADB shell command used to turn on the device

        """
        if constants.CUSTOM_TURN_ON in self._custom_commands:
            return self._custom_commands[constants.CUSTOM_TURN_ON]

        if self.DEVICE_ENUM == constants.DeviceEnum.FIRETV:
            return constants.CMD_TURN_ON_FIRETV

        return constants.CMD_TURN_ON_ANDROIDTV

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

    @staticmethod
    def _remove_adb_shell_prefix(cmd):
        """Remove the 'adb shell ' prefix from ``cmd``, if present.

        Parameters
        ----------
        cmd : str
            The ADB shell command

        Returns
        -------
        str
            ``cmd`` with the 'adb shell ' prefix removed, if it was present

        """
        return cmd[len("adb shell ") :] if cmd.startswith("adb shell ") else cmd

    # ======================================================================= #
    #                                                                         #
    #                        Home Assistant device info                       #
    #                                                                         #
    # ======================================================================= #
    def _parse_device_properties(self, properties):
        """Return a dictionary of device properties.

        Parameters
        ----------
        properties : str, None
            The output of the ADB command that retrieves the device properties

        This method fills in the ``device_properties`` attribute, which is a dictionary with keys
        ``'serialno'``, ``'manufacturer'``, ``'model'``, and ``'sw_version'``

        """
        _LOGGER.debug("%s:%d `get_device_properties` response: %s", self.host, self.port, properties)

        if not properties:
            self.device_properties = {}
            return

        lines = properties.strip().splitlines()
        if len(lines) != 4:
            self.device_properties = {}
            return

        manufacturer, model, serialno, version = lines

        if not serialno.strip():
            _LOGGER.warning("Could not obtain serialno for %s:%d, got: '%s'", self.host, self.port, serialno)
            serialno = None

        self.device_properties = {
            "manufacturer": manufacturer,
            "model": model,
            "serialno": serialno,
            "sw_version": version,
        }

    @staticmethod
    def _parse_mac_address(mac_response):
        """Parse a MAC address from the ADB shell response.

        Parameters
        ----------
        mac_response : str, None
            The response from the MAC address ADB shell command

        Returns
        -------
        str, None
            The parsed MAC address, or ``None`` if it could not be determined

        """
        if not mac_response:
            return None

        mac_matches = re.findall(constants.MAC_REGEX_PATTERN, mac_response)
        if mac_matches:
            return mac_matches[0]

        return None

    # ======================================================================= #
    #                                                                         #
    #                         Custom state detection                          #
    #                                                                         #
    # ======================================================================= #
    def _custom_state_detection(
        self, current_app=None, media_session_state=None, wake_lock_size=None, audio_state=None
    ):
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
            if rule == "media_session_state":
                if media_session_state == 2:
                    return constants.STATE_PAUSED
                if media_session_state == 3:
                    return constants.STATE_PLAYING
                if media_session_state is not None:
                    return constants.STATE_IDLE

            # Use the `audio_state` property
            if rule == "audio_state" and audio_state in constants.VALID_STATES:
                return audio_state

            # Check conditions and if they are true, return the specified state
            if isinstance(rule, dict):
                for state, conditions in rule.items():
                    if state in constants.VALID_STATES and self._conditions_are_true(
                        conditions, media_session_state, wake_lock_size, audio_state
                    ):
                        return state

        return None

    @staticmethod
    def _conditions_are_true(conditions, media_session_state=None, wake_lock_size=None, audio_state=None):
        """Check whether the conditions in ``conditions`` are true.

        Parameters
        ----------
        conditions : dict
            A dictionary of conditions to be checked (see the ``state_detection_rules`` parameter in :class:`~androidtv.basetv.basetv.BaseTV`)
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
            if key == "media_session_state":
                if media_session_state is None or media_session_state != val:
                    return False

            elif key == "wake_lock_size":
                if wake_lock_size is None or wake_lock_size != val:
                    return False

            elif key == "audio_state":
                if audio_state is None or audio_state != val:
                    return False

            # key is invalid
            else:
                return False

        return True

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

        matches = re.findall(constants.DEVICE_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0]

        return None

    @staticmethod
    def _audio_state(audio_state_response):
        """Parse the :meth:`audio_state` property from the ADB shell output.

        Parameters
        ----------
        audio_state_response : str, None
            The output from the ADB command `androidtv.basetv.basetv.BaseTV._cmd_audio_state``

        Returns
        -------
        str, None
            The audio state, or ``None`` if it could not be determined

        """
        if not audio_state_response:
            return None
        if audio_state_response == "1":
            return constants.STATE_PAUSED
        if audio_state_response == "2":
            return constants.STATE_PLAYING
        return constants.STATE_IDLE

    @staticmethod
    def _current_app(current_app_response):
        """Get the current app from the output of the command `androidtv.basetv.basetv.BaseTV._cmd_current_app`.

        Parameters
        ----------
        current_app_response : str, None
            The output from the ADB command `androidtv.basetv.basetv.BaseTV._cmd_current_app`

        Returns
        -------
        str, None
            The current app, or ``None`` if it could not be determined

        """
        if not current_app_response or "=" in current_app_response or "{" in current_app_response:
            return None

        return current_app_response

    def _current_app_media_session_state(self, current_app_media_session_state_response):
        """Get the current app and the media session state properties from the output of `androidtv.basetv.basetv.BaseTV._cmd_current_app_media_session_state`.

        Parameters
        ----------
        current_app_media_session_state_response : str, None
            The output of `androidtv.basetv.basetv.BaseTV._cmd_current_app_media_session_state`

        Returns
        -------
        current_app : str, None
            The current app, or ``None`` if it could not be determined
        media_session_state : int, None
            The state from the output of the ADB shell command, or ``None`` if it could not be determined

        """
        if not current_app_media_session_state_response:
            return None, None

        lines = current_app_media_session_state_response.splitlines()

        current_app = self._current_app(lines[0].strip())

        if len(lines) > 1:
            matches = constants.REGEX_MEDIA_SESSION_STATE.search(current_app_media_session_state_response)
            if matches:
                return current_app, int(matches.group("state"))

        return current_app, None

    @staticmethod
    def _get_hdmi_input(hdmi_response):
        """Get the HDMI input from the from the ADB shell output`.

        Parameters
        ----------
        hdmi_response : str, None
            The output from the ADB command `androidtv.basetv.basetv.BaseTV._cmd_hdmi_input``

        Returns
        -------
        str, None
            The HDMI input, or ``None`` if it could not be determined

        """
        return hdmi_response.strip() if hdmi_response and hdmi_response.strip() else None

    @staticmethod
    def _get_installed_apps(installed_apps_response):
        """Get the installed apps from the output of :py:const:`androidtv.constants.CMD_INSTALLED_APPS`.

        Parameters
        ----------
        installed_apps_response : str, None
            The output of :py:const:`androidtv.constants.CMD_INSTALLED_APPS`

        Returns
        -------
        list, None
            A list of the installed apps, or ``None`` if it could not be determined

        """
        if installed_apps_response is not None:
            return [
                line.strip().rsplit("package:", 1)[-1] for line in installed_apps_response.splitlines() if line.strip()
            ]

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
            return matches[0] == "true"

        return None

    @staticmethod
    def _parse_stream_music(stream_music_raw):
        """Parse the output of the command :py:const:`androidtv.constants.CMD_STREAM_MUSIC`.

        Parameters
        ----------
        stream_music_raw : str, None
            The output of the command :py:const:`androidtv.constants.CMD_STREAM_MUSIC`

        Returns
        -------
        str, None
            The ``STREAM_MUSIC`` block from the output of :py:const:`androidtv.constants.CMD_STREAM_MUSIC`, or ``None`` if it could not be determined

        """
        if not stream_music_raw:
            return None

        matches = re.findall(constants.STREAM_MUSIC_REGEX_PATTERN, stream_music_raw, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0]

        return None

    @staticmethod
    def _running_apps(running_apps_response):
        """Get the running apps from the output of :py:const:`androidtv.constants.CMD_RUNNING_APPS`.

        Parameters
        ----------
        running_apps_response : str, None
            The output of :py:const:`androidtv.constants.CMD_RUNNING_APPS`

        Returns
        -------
        list, None
            A list of the running apps, or ``None`` if it could not be determined

        """
        if running_apps_response:
            return [line.strip().rsplit(" ", 1)[-1] for line in running_apps_response.splitlines() if line.strip()]

        return None

    @staticmethod
    def _screen_on_awake_wake_lock_size(output):
        """Check if the screen is on and the device is awake, and get the wake lock size.

        Parameters
        ----------
        output : str, None
            The output from :py:const:`androidtv.constants.CMD_SCREEN_ON_AWAKE_WAKE_LOCK_SIZE`

        Returns
        -------
        bool, None
            Whether or not the device is on, or ``None`` if it could not be determined
        bool, None
            Whether or not the device is awake (screensaver is not running), or ``None`` if it could not be determined
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        if output is None:
            return None, None, None

        if output == "":
            return False, False, None

        screen_on = output[0] == "1"
        awake = None if len(output) < 2 else output[1] == "1"
        wake_lock_size = None if len(output) < 3 else BaseTV._wake_lock_size(output[2:])

        return screen_on, awake, wake_lock_size

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

        if not audio_output_device:
            return None

        volume_matches = re.findall(
            audio_output_device + constants.VOLUME_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE
        )
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
        """Get the size of the current wake lock from the output of :py:const:`androidtv.constants.CMD_WAKE_LOCK_SIZE`.

        Parameters
        ----------
        wake_lock_size_response : str, None
            The output of :py:const:`androidtv.constants.CMD_WAKE_LOCK_SIZE`

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        if wake_lock_size_response:
            wake_lock_size_matches = constants.REGEX_WAKE_LOCK_SIZE.search(wake_lock_size_response)
            if wake_lock_size_matches:
                return int(wake_lock_size_matches.group("size"))

        return None

    @staticmethod
    def _parse_getevent_line(line):
        """Parse a line of the output received in ``learn_sendevent``.

        Parameters
        ----------
        line : str
            A line of output from ``learn_sendevent``

        Returns
        -------
        str
            The properly formatted ``sendevent`` command

        """
        device_name, event_info = line.split(":", 1)
        integers = [int(x, 16) for x in event_info.strip().split()[:3]]
        return "sendevent {} {} {} {}".format(device_name, *integers)


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

        * Check that ``rule`` is in :py:const:`~androidtv.constants.VALID_STATES` or :py:const:`~androidtv.constants.VALID_STATE_PROPERTIES`

    * If ``rule`` is a dictionary:

        * Check that each key is in :py:const:`~androidtv.constants.VALID_STATES`
        * Check that each value is a dictionary

            * Check that each key is in :py:const:`~androidtv.constants.VALID_PROPERTIES`
            * Check that each value is of the right type, according to :py:const:`~androidtv.constants.VALID_PROPERTIES_TYPES`

    See :class:`~androidtv.basetv.basetv.BaseTV` for more info about the ``state_detection_rules`` parameter.

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
                raise exc(
                    "Invalid rule '{0}' is not in {1}".format(
                        rule, constants.VALID_STATE_PROPERTIES + constants.VALID_STATES
                    )
                )

        # If a rule is a dictionary, check that it is valid
        else:
            for state, conditions in rule.items():
                # The keys of the dictionary must be valid states
                if state not in constants.VALID_STATES:
                    raise exc("'{0}' is not a valid state for the 'state_detection_rules' parameter".format(state))

                # The values of the dictionary must be dictionaries
                if not isinstance(conditions, dict):
                    raise exc(
                        "Expected a map for entry '{0}' in 'state_detection_rules', got {1}".format(
                            state, type(conditions).__name__
                        )
                    )

                for prop, value in conditions.items():
                    # The keys of the dictionary must be valid properties that can be checked
                    if prop not in constants.VALID_PROPERTIES:
                        raise exc("Invalid property '{0}' is not in {1}".format(prop, constants.VALID_PROPERTIES))

                    # Make sure the value is of the right type
                    if not isinstance(value, constants.VALID_PROPERTIES_TYPES[prop]):
                        raise exc(
                            "Conditional value for property '{0}' must be of type {1}, not {2}".format(
                                prop, constants.VALID_PROPERTIES_TYPES[prop].__name__, type(value).__name__
                            )
                        )

    return rules
