"""Communicate with an Android TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging

from ..basetv.basetv import BaseTV
from .. import constants

_LOGGER = logging.getLogger(__name__)


class BaseAndroidTV(BaseTV):  # pylint: disable=too-few-public-methods
    """Representation of an Android TV device.

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

    DEVICE_CLASS = "androidtv"
    DEVICE_ENUM = constants.DeviceEnum.ANDROIDTV

    def __init__(self, host, port=5555, adbkey="", adb_server_ip="", adb_server_port=5037, state_detection_rules=None):
        BaseTV.__init__(self, None, host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules)

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def _update(
        self,
        screen_on,
        awake,
        audio_state,
        wake_lock_size,
        current_app,
        media_session_state,
        audio_output_device,
        is_volume_muted,
        volume,
        running_apps,
        hdmi_input,
    ):
        """Get the info needed for a Home Assistant update.

        Parameters
        ----------
        screen_on : bool, None
            Whether or not the device is on, or ``None`` if it was not determined
        awake : bool, None
            Whether or not the device is awake (screensaver is not running), or ``None`` if it was not determined
        audio_state : str, None
            The audio state, as determined from "dumpsys audio", or ``None`` if it was not determined
        wake_lock_size : int, None
            The size of the current wake lock, or ``None`` if it was not determined
        current_app : str, None
            The current app property, or ``None`` if it was not determined
        media_session_state : int, None
            The state from the output of ``dumpsys media_session``, or ``None`` if it was not determined
        audio_output_device : str, None
            The current audio playback device, or ``None`` if it was not determined
        is_volume_muted : bool, None
            Whether or not the volume is muted, or ``None`` if it was not determined
        volume : int, None
            The absolute volume level, or ``None`` if it was not determined
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
        audio_output_device : str
            The current audio playback device
        is_volume_muted : bool
            Whether or not the volume is muted
        volume_level : float
            The volume level (between 0 and 1)
        hdmi_input : str, None
            The HDMI input, or ``None`` if it could not be determined

        """
        # Get the volume (between 0 and 1)
        volume_level = self._volume_level(volume)

        # Check if device is unavailable
        if screen_on is None:
            state = None

        # Check if device is off
        elif not screen_on or current_app == "off":
            state = constants.STATE_OFF

        # Check if screen saver is on
        elif not awake:
            state = constants.STATE_STANDBY

        else:
            # Get the running apps
            if not running_apps and current_app:
                running_apps = [current_app]

            # Determine the state using custom rules
            state = self._custom_state_detection(
                current_app=current_app,
                media_session_state=media_session_state,
                wake_lock_size=wake_lock_size,
                audio_state=audio_state,
            )
            if state:
                return state, current_app, running_apps, audio_output_device, is_volume_muted, volume_level, hdmi_input

            # ATV Launcher
            if current_app in [constants.APP_ATV_LAUNCHER, None]:
                state = constants.STATE_IDLE

            # BELL Fibe
            elif current_app == constants.APP_BELL_FIBE:
                state = audio_state

            # Netflix
            elif current_app == constants.APP_NETFLIX:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # NLZIET
            elif current_app == constants.APP_NLZIET:
                if wake_lock_size == 1:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 2:
                    state = constants.STATE_PLAYING
            # Plex
            elif current_app == constants.APP_PLEX:
                if media_session_state == 3:
                    if wake_lock_size == 1:
                        state = constants.STATE_PAUSED
                    else:
                        state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # TVheadend
            elif current_app == constants.APP_TVHEADEND:
                if wake_lock_size == 5:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 6:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # VLC
            elif current_app == constants.APP_VLC:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

            # VRV
            elif current_app == constants.APP_VRV:
                state = audio_state

            # YouTube
            elif current_app == constants.APP_YOUTUBE:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
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

            # Get the state from `audio_state`
            elif audio_state != constants.STATE_IDLE:
                state = audio_state

            # Get the state from `wake_lock_size`
            else:
                if wake_lock_size == 1:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 2:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_IDLE

        return state, current_app, running_apps, audio_output_device, is_volume_muted, volume_level, hdmi_input
