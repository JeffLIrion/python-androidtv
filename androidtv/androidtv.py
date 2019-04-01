"""Communicate with an Android TV device via ADB over a network.

ADB Debugging must be enabled.
"""


from .basetv import BaseTV
from . import constants


class AndroidTV(BaseTV):
    """Representation of an Android TV device."""

    DEVICE_CLASS = 'androidtv'

    def __init__(self, host, adbkey='', adb_server_ip='', adb_server_port=5037):
        """Initialize an ``AndroidTV`` object.

        Parameters
        ----------
        host : str
            The address of the device in the format ``<ip address>:<host>``
        adbkey : str
            The path to the ``adbkey`` file for ADB authentication; the file ``adbkey.pub`` must be in the same directory
        adb_server_ip : str
            The IP address of the ADB server
        adb_server_port : int
            The port for the ADB server

        """
        BaseTV.__init__(self, host, adbkey, adb_server_ip, adb_server_port)

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    def start_intent(self, uri):
        """Start an intent on the device.

        Parameters
        ----------
        uri : str
            The intent that will be sent is ``am start -a android.intent.action.VIEW -d <uri>``

        """
        self.adb_shell("am start -a android.intent.action.VIEW -d {}".format(uri))

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def update(self):
        """Get the info needed for a Home Assistant update.

        Returns
        -------
        state : str
            The state of the device
        current_app : str
            The current running app
        device : str
            The current playback device
        is_volume_muted : bool
            Whether or not the volume is muted
        volume_level : float
            The volume level (between 0 and 1)

        """
        # Get the properties needed for the update
        screen_on, awake, wake_lock_size, media_session_state, current_app, audio_state, device, is_volume_muted, volume = self.get_properties(lazy=True)

        # Get the volume (between 0 and 1)
        volume_level = self._volume_level(volume)

        # Check if device is off
        if not screen_on or current_app == 'off':
            state = constants.STATE_OFF

        # Check if screen saver is on
        elif not awake:
            state = constants.STATE_IDLE

        # Get the state
        # TODO: determine the state differently based on the current app

        # VLC
        elif current_app == constants.APP_VLC:
            if media_session_state == 2:
                state = constants.STATE_PAUSED
            elif media_session_state == 3:
                state = constants.STATE_PLAYING
            else:
                state = constants.STATE_STANDBY

        # Get the state from `media_session_state`
        elif media_session_state:
            if media_session_state == 2:
                state = constants.STATE_PAUSED
            elif media_session_state == 3:
                state = constants.STATE_PLAYING
            else:
                state = constants.STATE_STANDBY

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
                state = constants.STATE_STANDBY

        return state, current_app, device, is_volume_muted, volume_level

    # ======================================================================= #
    #                                                                         #
    #                               properties                                #
    #                                                                         #
    # ======================================================================= #
    def get_properties(self, lazy=False):
        """Get the properties needed for Home Assistant updates.

        Parameters
        ----------
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        screen_on : bool, None
            Whether or not the device is on, or ``None`` if it was not determined
        awake : bool, None
            Whether or not the device is awake (screensaver is not running), or ``None`` if it was not determined
        wake_lock_size : int, None
            The size of the current wake lock, or ``None`` if it was not determined
        media_session_state : int, None
            The state from the output of ``dumpsys media_session``, or ``None`` if it was not determined
        current_app : dict, None
            The current app property, or ``None`` if it was not determined
        audio_state : str, None
            The audio state, as determined from "dumpsys audio", or ``None`` if it was not determined
        device : str, None
            The current playback device, or ``None`` if it was not determined
        is_volume_muted : bool, None
            Whether or not the volume is muted, or ``None`` if it was not determined
        volume : int, None
            The absolute volume level, or ``None`` if it was not determined

        """
        output = self.adb_shell(constants.CMD_SCREEN_ON + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                constants.CMD_AWAKE + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                constants.CMD_WAKE_LOCK_SIZE + " && (" +
                                constants.CMD_MEDIA_SESSION_STATE + " || echo) && " +
                                constants.CMD_CURRENT_APP + " && " +
                                "dumpsys audio")

        # ADB command was unsuccessful
        if output is None:
            return None, None, None, None, None, None, None, None, None

        # `screen_on` property
        if not output:
            return False, False, -1, None, None, None, None, None, None
        screen_on = output[0] == '1'

        # `awake` property
        if len(output) < 2:
            return screen_on, False, -1, None, None, None, None, None, None
        awake = output[1] == '1'

        lines = output.strip().splitlines()

        # `wake_lock_size` property
        if len(lines[0]) < 3:
            return screen_on, awake, -1, None, None, None, None, None, None
        wake_lock_size = self._wake_lock_size(lines[0])

        # `media_session_state` property
        if len(lines) < 2:
            return screen_on, awake, -1, None, None, None, None, None, None
        media_session_state = self._media_session_state(lines[1])

        # `current_app` property
        if len(lines) < 3:
            return screen_on, awake, wake_lock_size, media_session_state, None, None, None, None, None
        current_app = self._current_app(lines[2])

        # "dumpsys audio" output
        if len(lines) < 4:
            return screen_on, awake, wake_lock_size, media_session_state, current_app, None, None, None, None

        # reconstruct the output of `adb shell dumpsys audio`
        dumpsys_audio = "\n".join(lines[3:])

        # `audio_state` property
        audio_state = self._audio_state(dumpsys_audio)

        # the "STREAM_MUSIC" block from `adb shell dumpsys audio`
        stream_music = self._get_stream_music(dumpsys_audio)

        # `device` property
        device = self._device(stream_music)

        # `volume` property
        volume = self._volume(stream_music, device)

        # `is_volume_muted` property
        is_volume_muted = self._is_volume_muted(stream_music)

        return screen_on, awake, wake_lock_size, media_session_state, current_app, audio_state, device, is_volume_muted, volume

    def get_properties_dict(self, lazy=True):
        """Get the properties needed for Home Assistant updates and return them as a dictionary.

        Parameters
        ----------
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        dict
            A dictionary with keys ``'screen_on'``, ``'awake'``, ``'wake_lock_size'``, ``'media_session_state'``,
            ``'current_app'``, ``'audio_state'``, ``'device'``, ``'is_volume_muted'``, and ``'volume'``

        """
        screen_on, awake, wake_lock_size, media_session_state, current_app, audio_state, device, is_volume_muted, volume = self.get_properties(lazy=lazy)

        return {'screen_on': screen_on,
                'awake': awake,
                'wake_lock_size': wake_lock_size,
                'media_session_state': media_session_state,
                'current_app': current_app,
                'audio_state': audio_state,
                'device': device,
                'is_volume_muted': is_volume_muted,
                'volume': volume}

    # ======================================================================= #
    #                                                                         #
    #                           turn on/off methods                           #
    #                                                                         #
    # ======================================================================= #
    def turn_on(self):
        """Send ``POWER`` action if the device is off."""
        self.adb_shell(constants.CMD_SCREEN_ON + " || input keyevent {0}".format(constants.KEY_POWER))

    def turn_off(self):
        """Send ``POWER`` action if the device is not off."""
        self.adb_shell(constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_POWER))
