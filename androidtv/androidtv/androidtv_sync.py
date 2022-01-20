"""Communicate with an Android TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging

from .base_androidtv import BaseAndroidTV
from ..basetv.basetv_sync import BaseTVSync

_LOGGER = logging.getLogger(__name__)


class AndroidTVSync(BaseTVSync, BaseAndroidTV):
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
    signer : PythonRSASigner, None
        The signer for the ADB keys, as loaded by :meth:`androidtv.adb_manager.adb_manager_sync.ADBPythonSync.load_adbkey`

    """

    def __init__(
        self,
        host,
        port=5555,
        adbkey="",
        adb_server_ip="",
        adb_server_port=5037,
        state_detection_rules=None,
        signer=None,
    ):  # pylint: disable=super-init-not-called
        BaseTVSync.__init__(self, host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)

    @classmethod
    def from_base(cls, base_tv):
        """Construct an `AndroidTVSync` object from a `BaseTVSync` object.

        Parameters
        ----------
        base_tv : BaseTVSync
            The object that will be converted to an `AndroidTVSync` object

        Returns
        -------
        atv : AndroidTVSync
            The constructed `AndroidTVSync` object

        """
        # pylint: disable=protected-access
        atv = cls(
            base_tv.host,
            base_tv.port,
            base_tv.adbkey,
            base_tv.adb_server_ip,
            base_tv.adb_server_port,
            base_tv._state_detection_rules,
        )
        atv._adb = base_tv._adb
        atv.device_properties = base_tv.device_properties
        atv.installed_apps = base_tv.installed_apps
        atv.max_volume = base_tv.max_volume
        return atv

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def update(self, get_running_apps=True, lazy=True):
        """Get the info needed for a Home Assistant update.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :meth:`~androidtv.androidtv.androidtv_sync.AndroidTVSync.running_apps` property
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

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
        # Get the properties needed for the update
        (
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
        ) = self.get_properties(get_running_apps=get_running_apps, lazy=lazy)

        return self._update(
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
        )

    # ======================================================================= #
    #                                                                         #
    #                               Properties                                #
    #                                                                         #
    # ======================================================================= #
    def get_properties(self, get_running_apps=True, lazy=False):
        """Get the properties needed for Home Assistant updates.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :meth:`~androidtv.androidtv.androidtv_sync.AndroidTVSync.running_apps` property
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
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

        """
        screen_on, awake, wake_lock_size = self.screen_on_awake_wake_lock_size()

        if lazy and not (screen_on and awake):
            return screen_on, awake, None, wake_lock_size, None, None, None, None, None, None, None

        audio_state = self.audio_state()
        current_app, media_session_state = self.current_app_media_session_state()
        audio_output_device, is_volume_muted, volume, _ = self.stream_music_properties()

        if get_running_apps:
            running_apps = self.running_apps()
        else:
            running_apps = [current_app] if current_app else None

        hdmi_input = self.get_hdmi_input()

        return (
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
        )

    def get_properties_dict(self, get_running_apps=True, lazy=True):
        """Get the properties needed for Home Assistant updates and return them as a dictionary.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :meth:`~androidtv.androidtv.androidtv_sync.AndroidTVSync.running_apps` property
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        dict
            A dictionary with keys ``'screen_on'``, ``'awake'``, ``'wake_lock_size'``, ``'current_app'``,
            ``'media_session_state'``, ``'audio_state'``, ``'audio_output_device'``, ``'is_volume_muted'``, ``'volume'``, ``'running_apps'``, and ``'hdmi_input'``

        """
        (
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
        ) = self.get_properties(get_running_apps=get_running_apps, lazy=lazy)

        return {
            "screen_on": screen_on,
            "awake": awake,
            "audio_state": audio_state,
            "wake_lock_size": wake_lock_size,
            "current_app": current_app,
            "media_session_state": media_session_state,
            "audio_output_device": audio_output_device,
            "is_volume_muted": is_volume_muted,
            "volume": volume,
            "running_apps": running_apps,
            "hdmi_input": hdmi_input,
        }
