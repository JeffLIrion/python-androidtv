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

        # commands that can vary based on the device
        self._cmd_get_properties_lazy_running_apps = ""
        self._cmd_get_properties_lazy_no_running_apps = ""
        self._cmd_get_properties_not_lazy_running_apps = ""
        self._cmd_get_properties_not_lazy_no_running_apps = ""
        self._cmd_current_app = ""
        self._cmd_launch_app = ""

        # make sure the rules are valid
        if self._state_detection_rules:
            for app_id, rules in self._state_detection_rules.items():
                if not isinstance(app_id, str):
                    raise TypeError("{0} is of type {1}, not str".format(app_id, type(app_id).__name__))
                state_detection_rules_validator(rules)

        # the max volume level (determined when first getting the volume level)
        self.max_volume = None

    def _fill_in_commands(self):
        """Fill in commands that are specific to the device.

        This is implemented in the `BaseAndroidTV` and `BaseFireTV` classes.

        """

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
        ``'wifimac'``, ``'ethmac'``, ``'serialno'``, ``'manufacturer'``, ``'model'``, and ``'sw_version'``

        """
        _LOGGER.debug("%s:%d `get_device_properties` response: %s", self.host, self.port, properties)

        if not properties:
            self.device_properties = {}
            return

        lines = properties.strip().splitlines()
        if len(lines) != 6:
            self.device_properties = {}
            return

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

        self.device_properties = {
            "manufacturer": manufacturer,
            "model": model,
            "serialno": serialno,
            "sw_version": version,
            "wifimac": wifimac,
            "ethmac": ethmac,
        }

        self._fill_in_commands()

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
        """Parse the :meth:`audio_state` property from the output of the command :py:const:`androidtv.constants.CMD_AUDIO_STATE`.

        Parameters
        ----------
        audio_state_response : str, None
            The output of the command :py:const:`androidtv.constants.CMD_AUDIO_STATE`

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
        """Get the current app from the output of the command :py:const:`androidtv.constants.CMD_CURRENT_APP`.

        Parameters
        ----------
        current_app_response : str, None
            The output from the ADB command :py:const:`androidtv.constants.CMD_CURRENT_APP`

        Returns
        -------
        str, None
            The current app, or ``None`` if it could not be determined

        """
        if not current_app_response or "=" in current_app_response or "{" in current_app_response:
            return None

        return current_app_response

    def _current_app_media_session_state(self, media_session_state_response):
        """Get the current app and the media session state properties from the output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE_FULL`.

        Parameters
        ----------
        media_session_state_response : str, None
            The output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE_FULL`

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

        current_app = self._current_app(lines[0].strip())

        if len(lines) > 1:
            media_session_state = self._media_session_state(lines[1], current_app)
        else:
            media_session_state = None

        return current_app, media_session_state

    @staticmethod
    def _get_hdmi_input(hdmi_response):
        """Get the HDMI input from the output of :py:const:`androidtv.constants.CMD_HDMI_INPUT`.

        Parameters
        ----------
        hdmi_response : str, None
            The output of :py:const:`androidtv.constants.CMD_HDMI_INPUT`

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
    def _media_session_state(media_session_state_response, current_app):
        """Get the state from the output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE`.

        Parameters
        ----------
        media_session_state_response : str, None
            The output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE`
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
            return int(matches.group("state"))

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
            if isinstance(running_apps_response, list):
                return [line.strip().rsplit(" ", 1)[-1] for line in running_apps_response if line.strip()]
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
        bool
            Whether or not the device is on
        bool
            Whether or not the device is awake (screensaver is not running)
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        if not output:
            return False, False, None

        if output == "1":
            return True, False, None

        if output == "11":
            return True, True, None

        return True, True, BaseTV._wake_lock_size(output[2:])

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
                self.max_volume = 15.0

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
