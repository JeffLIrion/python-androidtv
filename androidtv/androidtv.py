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

PROP_REGEX_PATTERN = r".*?\[(.*?)]"
WIFIMAC_PROP_REGEX_PATTERN = "wifimac" + PROP_REGEX_PATTERN
WIFIMAC_REGEX_PATTERN = "ether (.*?) brd"
SERIALNO_REGEX_PATTERN = "serialno" + PROP_REGEX_PATTERN
MANUF_REGEX_PATTERN = "manufacturer" + PROP_REGEX_PATTERN
MODEL_REGEX_PATTERN = "product.model" + PROP_REGEX_PATTERN
VERSION_REGEX_PATTERN = "version.release" + PROP_REGEX_PATTERN

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

        # get device properties
        if self._available:
            self.device_properties = self.get_device_properties()

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
        muted : bool
            Whether or not the volume is muted
        volume : float
            The volume level (between 0 and 1)

        """
        # Get the properties needed for the update
        screen_on, awake, wake_lock_size, _current_app, audio_state, device, muted, volume = self.get_properties(lazy=True)

        # Get the current app
        if isinstance(_current_app, dict) and 'package' in _current_app:
            current_app = _current_app['package']
        else:
            current_app = None

        # Check if device is off
        if not screen_on:
            return constants.STATE_OFF, current_app, device, muted, volume

        # TODO: determine the state differently based on the current app
        if audio_state:
            state = audio_state

        else:
            if not awake:
                state = constants.STATE_IDLE
            elif wake_lock_size == 1:
                state = constants.STATE_PLAYING
            else:
                state = constants.STATE_PAUSED

        return state, current_app, device, muted, volume

    # ======================================================================= #
    #                                                                         #
    #                        Home Assistant device info                       #
    #                                                                         #
    # ======================================================================= #
    def get_device_properties(self):
        """Return a dictionary of device properties.

        Returns
        -------
        props : dict
            A dictionary with keys ``'wifimac'``, ``'serialno'``, ``'manufacturer'``, ``'model'``, and ``'sw_version'``

        """
        properties = self.adb_shell('getprop')

        if 'wifimac' in properties:
            wifimac = re.findall(WIFIMAC_PROP_REGEX_PATTERN, properties)[0]
        else:
            wifi_out = self.adb_shell('ip addr show wlan0')
            wifimac = re.findall(WIFIMAC_REGEX_PATTERN, wifi_out)[0]

        serialno = re.findall(SERIALNO_REGEX_PATTERN, properties)[0]
        manufacturer = re.findall(MANUF_REGEX_PATTERN, properties)[0]
        model = re.findall(MODEL_REGEX_PATTERN, properties)[0]
        version = re.findall(VERSION_REGEX_PATTERN, properties)[0]

        props = {'wifimac': wifimac,
                 'serialno': serialno,
                 'manufacturer': manufacturer,
                 'model': model,
                 'sw_version': version}

        return props

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
    def muted(self):
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
        """Get the volume level.

        Returns
        -------
        float, None
            The volume level (between 0 and 1), or ``None`` if it could not be determined

        """
        output = self.adb_shell("dumpsys audio")
        if not output:
            return None

        stream_block = re.findall(BLOCK_REGEX_PATTERN, output, re.DOTALL | re.MULTILINE)[0]
        device = re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]
        volume_level = re.findall(device + VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)[0]

        return round(1 / 15 * float(volume_level), 2)

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
        current_app : dict, None
            The current app property, or ``None`` if it was not determined
        audio_state : str, None
            The audio state, as determined from "dumpsys audio", or ``None`` if it was not determined
        device : str, None
            The current playback device, or ``None`` if it was not determined
        muted : bool, None
            Whether or not the volume is muted, or ``None`` if it was not determined
        volume : float, None
            The volume level (between 0 and 1), or ``None`` if it was not determined

        """
        output = self.adb_shell(constants.CMD_SCREEN_ON + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                constants.CMD_AWAKE + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                constants.CMD_WAKE_LOCK_SIZE + " && " +
                                constants.CMD_CURRENT_APP + " && " +
                                "dumpsys audio")

        # ADB command was unsuccessful
        if output is None:
            return None, None, None, None, None, None, None, None

        # `screen_on` property
        if not output:
            return False, False, -1, None, None, None, None, None
        screen_on = output[0] == '1'

        # `awake` property
        if len(output) < 2:
            return screen_on, False, -1, None, None, None, None, None
        awake = output[1] == '1'

        lines = output.strip().splitlines()

        # `wake_lock_size` property
        if len(lines[0]) < 3:
            return screen_on, awake, -1, None, None, None, None, None
        wake_lock_size = int(lines[0].split("=")[1].strip())

        # `current_app` property
        if len(lines) < 2:
            return screen_on, awake, wake_lock_size, None, None, None, None, None

        matches = constants.REGEX_WINDOW.search(lines[1])
        if matches:
            # case 1: current app was successfully found
            (pkg, activity) = matches.group("package", "activity")
            current_app = {"package": pkg, "activity": activity}
        else:
            # case 2: current app could not be found
            current_app = None

        # "dumpsys audio" output
        if len(lines) < 3:
            return screen_on, awake, wake_lock_size, current_app, None, None, None, None

        audio_output = "\n".join(lines[2:])

        # `audio_state` property
        if 'started' in audio_output:
            audio_state = constants.STATE_PLAYING
        elif 'paused' in audio_output:
            audio_state = constants.STATE_PAUSED
        else:
            audio_state = constants.STATE_IDLE

        matches = re.findall(BLOCK_REGEX_PATTERN, audio_output, re.DOTALL | re.MULTILINE)
        if not matches:
            return screen_on, awake, wake_lock_size, current_app, audio_state, None, None, None
        stream_block = matches[0]

        # `device` property
        matches = re.findall(DEVICE_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
        if matches:
            device = matches[0]

            # `volume` property
            matches = re.findall(device + VOLUME_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
            if matches:
                volume = round(1 / 15 * float(matches[0]), 2)
            else:
                volume = None

        else:
            device = None
            volume = None

        # `muted` property
        matches = re.findall(MUTED_REGEX_PATTERN, stream_block, re.DOTALL | re.MULTILINE)
        if matches:
            muted = matches[0] == 'true'
        else:
            muted = None

        return screen_on, awake, wake_lock_size, current_app, audio_state, device, muted, volume

    def get_properties_dict(self, lazy=True):
        """Get the properties needed for Home Assistant updates and return them as a dictionary.

        Parameters
        ----------
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        dict
            A dictionary with keys ``'screen_on'``, ``'awake'``, ``'wake_lock_size'``, ``'current_app'``,
            ``'audio_state'``, ``'device'``, ``'muted'``, and ``'volume'``

        """
        screen_on, awake, wake_lock_size, _current_app, audio_state, device, muted, volume = self.get_properties(lazy=lazy)

        return {'screen_on': screen_on,
                'awake': awake,
                'wake_lock_size': wake_lock_size,
                'current_app': _current_app,
                'audio_state': audio_state,
                'device': device,
                'muted': muted,
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
