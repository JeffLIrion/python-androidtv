"""Communicate with an Android TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import re

from .basetv import BaseTV
from . import constants


# Regular expression patterns
BLOCK_REGEX_PATTERN = "STREAM_MUSIC(.*?)- STREAM"
DEVICE_REGEX_PATTERN = r"Devices: (.*?)\W"
MUTED_REGEX_PATTERN = r"Muted: (.*?)\W"
VOLUME_REGEX_PATTERN = r"\): (\d{1,})"
MAX_VOLUME_REGEX_PATTERN = r"Max: (\d{1,})"

# ADB shell commands for getting the `screen_on`, `awake`, `wake_lock`, `audio_state`, and `current_app` properties
CMD_AUDIO_STATE = r"dumpsys audio | grep -q paused && echo -e '1\c' || (dumpsys audio | grep -q started && echo '2\c' || echo '0\c')"


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

        # the max volume level (determined when first getting the volume level)
        self.max_volume = None

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
        screen_on, awake, wake_lock_size, media_session_state, _current_app, audio_state, device, is_volume_muted, volume = self.get_properties(lazy=True)

        # Get the current app
        if isinstance(_current_app, dict) and 'package' in _current_app:
            current_app = _current_app['package']
        else:
            current_app = None

        # Get the volume (between 0 and 1)
        if volume is not None:
            volume_level = volume / self.max_volume
        else:
            volume_level = None

        # Check if device is off
        if not screen_on or current_app == 'off':
            state = constants.STATE_OFF

        # Check if screen saver is on
        elif not awake:
            state = constants.STATE_IDLE

        # Get the state
        # TODO: determine the state differently based on the current app
        elif audio_state != constants.STATE_IDLE:
            state = audio_state

        # VLC
        elif current_app == constants.APP_VLC:
            if media_session_state == 2:
                state = constants.STATE_PAUSED
            elif media_session_state == 3:
                state = constants.STATE_PLAYING
            else:
                state = constants.STATE_STANDBY

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
    @property
    def audio_state(self):
        """Check if audio is playing, paused, or idle.

        Returns
        -------
        str, None
            The audio state, as determined from the ADB shell command ``dumpsys audio``, or ``None`` if it could not be determined

        """
        output = self.adb_shell(CMD_AUDIO_STATE)
        if output is None:
            return None
        if output == '1':
            return constants.STATE_PAUSED
        if output == '2':
            return constants.STATE_PLAYING
        return constants.STATE_IDLE

    @property
    def device(self):
        """Get the current playback device.

        Returns
        -------
        str, None
            The current playback device, or ``None`` if it could not be determined

        """
        output = self.adb_shell("dumpsys audio")
        if not output:
            return None

        stream_block = re.findall(BLOCK_REGEX_PATTERN, output, re.DOTALL | re.MULTILINE)[0]
        return re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]

    @property
    def is_volume_muted(self):
        """Whether or not the volume is muted.

        Returns
        -------
        bool, None
            Whether or not the volume is muted, or ``None`` if it could not be determined

        """
        output = self.adb_shell("dumpsys audio")
        if not output:
            return None

        stream_block = re.findall(BLOCK_REGEX_PATTERN, output, re.DOTALL | re.MULTILINE)[0]
        return re.findall(MUTED_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0] == 'true'

    @property
    def volume(self):
        """Get the absolute volume level.

        Returns
        -------
        int, None
            The absolute volume level, or ``None`` if it could not be determined

        """
        output = self.adb_shell("dumpsys audio")
        if not output:
            return None

        stream_block = re.findall(BLOCK_REGEX_PATTERN, output, re.DOTALL | re.MULTILINE)[0]
        device = re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]
        volume = re.findall(device + VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]

        if not self.max_volume:
            matches = re.findall(MAX_VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
            if matches:
                self.max_volume = float(matches[0])
            else:
                self.max_volume = 15.

        return int(volume)

    @property
    def volume_level(self):
        """Get the relative volume level.

        Returns
        -------
        float, None
            The volume level (between 0 and 1), or ``None`` if it could not be determined

        """
        volume = self.volume

        if volume is not None:
            return volume / self.max_volume
        return None

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
        wake_lock_size = int(lines[0].split("=")[1].strip())

        # `media_session_state` property
        if len(lines) < 2:
            return screen_on, awake, -1, None, None, None, None, None, None

        matches = constants.REGEX_MEDIA_SESSION_STATE.search(lines[1])
        if matches:
            media_session_state = int(matches.group('state'))
        else:
            media_session_state = None

        # `current_app` property
        if len(lines) < 3:
            return screen_on, awake, wake_lock_size, media_session_state, None, None, None, None, None

        matches = constants.REGEX_WINDOW.search(lines[2])
        if matches:
            # case 1: current app was successfully found
            (pkg, activity) = matches.group("package", "activity")
            current_app = {"package": pkg, "activity": activity}
        else:
            # case 2: current app could not be found
            current_app = None

        # "dumpsys audio" output
        if len(lines) < 4:
            return screen_on, awake, wake_lock_size, media_session_state, current_app, None, None, None, None

        audio_output = "\n".join(lines[3:])

        # `audio_state` property
        if 'started' in audio_output:
            audio_state = constants.STATE_PLAYING
        elif 'paused' in audio_output:
            audio_state = constants.STATE_PAUSED
        else:
            audio_state = constants.STATE_IDLE

        matches = re.findall(BLOCK_REGEX_PATTERN, audio_output, re.DOTALL | re.MULTILINE)
        if not matches:
            return screen_on, awake, wake_lock_size, media_session_state, current_app, audio_state, None, None, None
        stream_block = matches[0]

        # `device` property
        matches = re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
        if matches:
            device = matches[0]

            # `self.max_volume` attribute
            if not self.max_volume:
                matches_max_volume = re.findall(MAX_VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
                if matches_max_volume:
                    self.max_volume = float(matches_max_volume[0])
                else:
                    self.max_volume = 15.

            # `volume` property
            matches_volume = re.findall(device + VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
            if matches_volume:
                volume = int(matches_volume[0])
            else:
                volume = None

        else:
            device = None
            volume = None

        # `is_volume_muted` property
        matches = re.findall(MUTED_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
        if matches:
            is_volume_muted = matches[0] == 'true'
        else:
            is_volume_muted = None

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

    # ======================================================================= #
    #                                                                         #
    #                              volume methods                             #
    #                                                                         #
    # ======================================================================= #
    def volume_set(self, volume_level, current_volume_level=None):
        """Set the volume to the desired level.

        Parameters
        ----------
        volume_level : float
            The new volume level (between 0 and 1)
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float
            The new volume level (between 0 and 1)

        """
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = min(max(round(self.max_volume * current_volume_level), 0.), self.max_volume)

        new_volume = min(max(round(self.max_volume * volume_level), 0.), self.max_volume)

        # Case 1: the new volume is the same as the current volume
        if new_volume == current_volume:
            return new_volume / self.max_volume

        # Case 2: the new volume is less than the current volume
        if new_volume < current_volume:
            cmd = " && ".join(["input keyevent {0}".format(constants.KEY_VOLUME_DOWN)] * int(current_volume - new_volume))

        # Case 3: the new volume is greater than the current volume
        else:
            cmd = " && ".join(["input keyevent {0}".format(constants.KEY_VOLUME_UP)] * int(new_volume - current_volume))

        # send the volume down/up commands
        self.adb_shell(cmd)

        # return the new volume level
        return new_volume / self.max_volume

    def volume_up(self, current_volume_level=None):
        """Send volume up action.

        Parameters
        ----------
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float
            The new volume level (between 0 and 1)

        """
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = round(self.max_volume * current_volume_level)

        if current_volume == self.max_volume:
            return 1.0

        # send the volume up command
        self._key(constants.KEY_VOLUME_UP)

        # return the new volume level
        return (current_volume + 1) / self.max_volume

    def volume_down(self, current_volume_level=None):
        """Send volume down action.

        Parameters
        ----------
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float
            The new volume level (between 0 and 1)

        """
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = round(self.max_volume * current_volume_level)

        if current_volume == 0:
            return 0.0

        # send the volume down command
        self._key(constants.KEY_VOLUME_DOWN)

        # return the new volume level
        return (current_volume - 1) / self.max_volume
