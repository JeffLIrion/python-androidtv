"""Communicate with an Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging

from ..basetv.basetv import BaseTV
from .. import constants

_LOGGER = logging.getLogger(__name__)


class BaseFireTV(BaseTV):  # pylint: disable=too-few-public-methods
    """Representation of an Amazon Fire TV device.

    Parameters
    ----------
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
        A dictionary of rules for determining the state (see :class:`~androidtv.basetv.basetv.BaseTV`)

    """

    DEVICE_CLASS = 'firetv'

    def __init__(self, host, port=5555, adbkey='', adb_server_ip='', adb_server_port=5037, state_detection_rules=None):
        BaseTV.__init__(self, None, host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules)

    def _fill_in_commands(self):
        """Fill in commands that are specific to Fire TV devices."""
        self._cmd_get_properties_lazy_running_apps = constants.CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS
        self._cmd_get_properties_lazy_no_running_apps = constants.CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS
        self._cmd_get_properties_not_lazy_running_apps = constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS
        self._cmd_get_properties_not_lazy_no_running_apps = constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS
        self._cmd_current_app = constants.CMD_CURRENT_APP
        self._cmd_launch_app = constants.CMD_LAUNCH_APP

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def _update(self, screen_on, awake, wake_lock_size, current_app, media_session_state, running_apps, hdmi_input):
        """Get the info needed for a Home Assistant update.

        Parameters
        ----------
        screen_on : bool, None
            Whether or not the device is on, or ``None`` if it was not determined
        awake : bool, None
            Whether or not the device is awake (screensaver is not running), or ``None`` if it was not determined
        wake_lock_size : int, None
            The size of the current wake lock, or ``None`` if it was not determined
        current_app : str, None
            The current app property, or ``None`` if it was not determined
        media_session_state : int, None
            The state from the output of ``dumpsys media_session``, or ``None`` if it was not determined
        running_apps : list, None
            A list of the running apps, or ``None`` if it was not determined
        hdmi_input : str, None
            The HDMI input, or ``None`` if it could not be determined

        Returns
        -------
        state : str
            The state of the device
        current_app : str
            The current running app
        running_apps : list
            A list of the running apps if ``get_running_apps`` is True, otherwise the list ``[current_app]``
        hdmi_input : str, None
            The HDMI input, or ``None`` if it could not be determined

        """
        # Check if device is unavailable
        if screen_on is None:
            state = None
            current_app = None
            running_apps = None

        # Check if device is off
        elif not screen_on:
            state = constants.STATE_OFF
            current_app = None
            running_apps = None

        # Check if screen saver is on
        elif not awake:
            state = constants.STATE_STANDBY
            current_app = None
            running_apps = None

        else:
            # Get the running apps
            if not running_apps and current_app:
                running_apps = [current_app]

            # Determine the state using custom rules
            state = self._custom_state_detection(current_app=current_app, media_session_state=media_session_state, wake_lock_size=wake_lock_size)
            if state:
                return state, current_app, running_apps, hdmi_input

            # Determine the state based on the `current_app`
            if current_app in [constants.APP_FIRETV_PACKAGE_LAUNCHER, constants.APP_FIRETV_PACKAGE_SETTINGS, None]:
                state = constants.STATE_IDLE

            # Amazon Video
            elif current_app == constants.APP_AMAZON_VIDEO:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Firefox
            elif current_app == constants.APP_FIREFOX:
                if wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Hulu
            elif current_app == constants.APP_HULU:
                if wake_lock_size == 4:
                    state = constants.STATE_PLAYING
                elif wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                else:
                    state = constants.STATE_IDLE

            # Jellyfin
            elif current_app == constants.APP_JELLYFIN_TV:
                if wake_lock_size == 2:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_PAUSED

            # Netflix
            elif current_app == constants.APP_NETFLIX:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Plex
            elif current_app == constants.APP_PLEX:
                if media_session_state == 3:
                    if wake_lock_size == 2:
                        state = constants.STATE_PAUSED
                    else:
                        state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Sport 1
            elif current_app == constants.APP_SPORT1:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Spotify
            elif current_app == constants.APP_SPOTIFY:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Twitch
            elif current_app == constants.APP_TWITCH_FIRETV:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                elif media_session_state == 4:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Waipu TV
            elif current_app == constants.APP_WAIPU_TV:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Get the state from `media_session_state`
            elif media_session_state:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # Get the state from `wake_lock_size`
            else:
                if wake_lock_size == 1:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_PAUSED

        return state, current_app, running_apps, hdmi_input

    # ======================================================================= #
    #                                                                         #
    #                               Properties                                #
    #                                                                         #
    # ======================================================================= #
    def _get_properties(self, output, get_running_apps=True):
        """Get the properties needed for Home Assistant updates.

        This will send one of the following ADB commands:

        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS`

        Parameters
        ----------
        output : str, None
            The output of the ADB command used to retrieve the properties
        get_running_apps : bool
            Whether or not to get the ``running_apps`` property

        Returns
        -------
        screen_on : bool, None
            Whether or not the device is on, or ``None`` if it was not determined
        awake : bool, None
            Whether or not the device is awake (screensaver is not running), or ``None`` if it was not determined
        wake_lock_size : int, None
            The size of the current wake lock, or ``None`` if it was not determined
        current_app : str, None
            The current app property, or ``None`` if it was not determined
        media_session_state : int, None
            The state from the output of ``dumpsys media_session``, or ``None`` if it was not determined
        running_apps : list, None
            A list of the running apps, or ``None`` if it was not determined
        hdmi_input : str, None
            The HDMI input, or ``None`` if it could not be determined

        """
        # ADB command was unsuccessful
        if output is None:
            return None, None, None, None, None, None, None

        # `screen_on` property
        if not output:
            return False, False, -1, None, None, None, None
        screen_on = output[0] == '1'

        # `awake` property
        if len(output) < 2:
            return screen_on, False, -1, None, None, None, None
        awake = output[1] == '1'

        lines = output.strip().splitlines()

        # `wake_lock_size` property
        if len(lines[0]) < 3:
            return screen_on, awake, -1, None, None, None, None
        wake_lock_size = self._wake_lock_size(lines[0])

        # `current_app` property
        if len(lines) < 2:
            return screen_on, awake, wake_lock_size, None, None, None, None
        current_app = self._current_app(lines[1])

        # `media_session_state` property
        if len(lines) < 3:
            return screen_on, awake, wake_lock_size, current_app, None, None, None
        media_session_state = self._media_session_state(lines[2], current_app)

        # HDMI input property
        if len(lines) < 4:
            return screen_on, awake, wake_lock_size, current_app, media_session_state, None, None
        hdmi_input = self._get_hdmi_input(lines[3])

        # `running_apps` property
        if not get_running_apps or len(lines) < 5:
            return screen_on, awake, wake_lock_size, current_app, media_session_state, None, hdmi_input
        running_apps = self._running_apps(lines[4:])

        return screen_on, awake, wake_lock_size, current_app, media_session_state, running_apps, hdmi_input
