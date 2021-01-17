"""Communicate with an Android TV or Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging

from .basetv import BaseTV
from .. import constants
from ..adb_manager.adb_manager_async import ADBPythonAsync, ADBServerAsync

_LOGGER = logging.getLogger(__name__)


class BaseTVAsync(BaseTV):
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
    signer : PythonRSASigner, None
        The signer for the ADB keys, as loaded by :meth:`androidtv.adb_manager.adb_manager_async.ADBPythonAsync.load_adbkey`

    """

    def __init__(self, host, port=5555, adbkey='', adb_server_ip='', adb_server_port=5037, state_detection_rules=None, signer=None):
        # the handler for ADB commands
        if not adb_server_ip:
            # python-adb
            adb = ADBPythonAsync(host, port, adbkey, signer)
        else:
            # pure-python-adb
            adb = ADBServerAsync(host, port, adb_server_ip, adb_server_port)

        BaseTV.__init__(self, adb, host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules)

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    async def adb_shell(self, cmd):
        """Send an ADB command.

        This calls :py:meth:`androidtv.adb_manager.adb_manager_async.ADBPythonAsync.shell` or :py:meth:`androidtv.adb_manager.adb_manager_async.ADBServerAsync.shell`,
        depending on whether the Python ADB implementation or an ADB server is used for communicating with the device.

        Parameters
        ----------
        cmd : str
            The ADB command to be sent

        Returns
        -------
        str, None
            The response from the device, if there is a response

        """
        return await self._adb.shell(self._remove_adb_shell_prefix(cmd))

    async def adb_pull(self, local_path, device_path):
        """Pull a file from the device.

        This calls :py:meth:`androidtv.adb_manager.adb_manager_async.ADBPythonAsync.pull` or :py:meth:`androidtv.adb_manager.adb_manager_async.ADBServerAsync.pull`,
        depending on whether the Python ADB implementation or an ADB server is used for communicating with the device.

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

        This calls :py:meth:`androidtv.adb_manager.adb_manager_async.ADBPythonAsync.push` or :py:meth:`androidtv.adb_manager.adb_manager_async.ADBServerAsync.push`,
        depending on whether the Python ADB implementation or an ADB server is used for communicating with the device.

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

        This calls :py:meth:`androidtv.adb_manager.adb_manager_async.ADBPythonAsync.screencap` or :py:meth:`androidtv.adb_manager.adb_manager_async.ADBServerAsync.screencap`,
        depending on whether the Python ADB implementation or an ADB server is used for communicating with the device.

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
        if isinstance(self._adb, ADBPythonAsync):
            return await self._adb.connect(always_log_errors, auth_timeout_s)
        return await self._adb.connect(always_log_errors)

    async def adb_close(self):
        """Close the ADB connection.

        This only works for the Python ADB implementation (see :meth:`androidtv.adb_manager.adb_manager_async.ADBPython.close`).
        For the ADB server approach, this doesn't do anything (see :meth:`androidtv.adb_manager.adb_manager_async.ADBServer.close`).

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

        self._parse_device_properties(properties)
        return self.device_properties

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
            The audio state, as determined from the ADB shell command :py:const:`androidtv.constants.CMD_AUDIO_STATE`, or ``None`` if it could not be determined

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
        current_app_response = await self._adb.shell(self._cmd_current_app)

        return self._current_app(current_app_response)

    async def get_hdmi_input(self):
        """Get the HDMI input from the output of :py:const:`androidtv.constants.CMD_HDMI_INPUT`.

        Returns
        -------
        str, None
            The HDMI input, or ``None`` if it could not be determined

        """
        return self._get_hdmi_input(await self._adb.shell(constants.CMD_HDMI_INPUT))

    async def get_installed_apps(self):
        """Return a list of installed applications.

        Returns
        -------
        list, None
            A list of the installed apps, or ``None`` if it could not be determined

        """
        installed_apps_response = await self._adb.shell(constants.CMD_INSTALLED_APPS)
        self.installed_apps = self._get_installed_apps(installed_apps_response)
        return self.installed_apps

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
    async def _get_stream_music(self, stream_music_raw=None):
        """Get the ``STREAM_MUSIC`` block from the output of the command :py:const:`androidtv.constants.CMD_STREAM_MUSIC`.

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
            stream_music_raw = await self._adb.shell(constants.CMD_STREAM_MUSIC)

        return self._parse_stream_music(stream_music_raw)

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
        await self._adb.shell(self._cmd_launch_app.format(app))

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
    #                          Miscellaneous methods                          #
    #                                                                         #
    # ======================================================================= #
    async def learn_sendevent(self, timeout_s=8):
        """Capture an event (e.g., a button press) via ``getevent`` and convert it into ``sendevent`` commands.

        For more info, see:

        * http://ktnr74.blogspot.com/2013/06/emulating-touchscreen-interaction-with.html?m=1
        * https://qatesttech.wordpress.com/2012/06/21/turning-the-output-from-getevent-into-something-something-that-can-be-used/

        Parameters
        ----------
        timeout_s : int
            The timeout in seconds to wait for events

        Returns
        -------
        str
            The events converted to ``sendevent`` commands

        """
        getevent = await self._adb.shell("( getevent ) & pid=$!; ( sleep {} && kill -HUP $pid ) 2>/dev/null & watcher=$!; if wait $pid 2>/dev/null; then echo 'your command finished'; kill -HUP -P $watcher; wait $watcher; else echo 'your command was interrupted'; fi".format(timeout_s))

        return " && ".join([self._parse_getevent_line(line) for line in getevent.splitlines() if line.startswith("/") and ":" in line])
