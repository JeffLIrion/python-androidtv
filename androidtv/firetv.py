"""Communicate with an Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


from .basetv import BaseTV
from . import constants


# Apps
APP_PACKAGE_LAUNCHER = "com.amazon.tv.launcher"
APP_PACKAGE_SETTINGS = "com.amazon.tv.settings"

# Intents
INTENT_LAUNCH = "android.intent.category.LAUNCHER"
INTENT_HOME = "android.intent.category.HOME"


class FireTV(BaseTV):
    """Representation of an Amazon Fire TV device."""

    DEVICE_CLASS = 'firetv'

    def __init__(self, host, adbkey='', adb_server_ip='', adb_server_port=5037):
        """Initialize a ``FireTV`` object.

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
    def _send_intent(self, pkg, intent, count=1):
        """Send an intent to the device.

        Parameters
        ----------
        pkg : str
            The command that will be sent is ``monkey -p <intent> -c <pkg> <count>; echo $?``
        intent : str
            The command that will be sent is ``monkey -p <intent> -c <pkg> <count>; echo $?``
        count : int, str
            The command that will be sent is ``monkey -p <intent> -c <pkg> <count>; echo $?``

        Returns
        -------
        dict
            A dictionary with keys ``'output'`` and ``'retcode'``, if they could be determined; otherwise, an empty dictionary

        """
        cmd = 'monkey -p {} -c {} {}; echo $?'.format(pkg, intent, count)

        # adb shell outputs in weird format, so we cut it into lines,
        # separate the retcode and return info to the user
        res = self.adb_shell(cmd)
        if res is None:
            return {}

        res = res.strip().split("\r\n")
        retcode = res[-1]
        output = "\n".join(res[:-1])

        return {"output": output, "retcode": retcode}

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def update(self, get_running_apps=True):
        """Get the info needed for a Home Assistant update.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the ``running_apps`` property

        Returns
        -------
        state : str
            The state of the device
        current_app : str
            The current running app
        running_apps : list
            A list of the running apps if ``get_running_apps`` is True, otherwise the list ``[current_app]``

        """
        # Get the properties needed for the update
        screen_on, awake, wake_lock_size, media_session_state, current_app, running_apps = self.get_properties(get_running_apps=get_running_apps, lazy=True)

        # Check if device is off
        if not screen_on:
            state = constants.STATE_OFF
            current_app = None
            running_apps = None

        # Check if screen saver is on
        elif not awake:
            state = constants.STATE_IDLE
            current_app = None
            running_apps = None

        else:
            # Get the running apps
            if running_apps is None and current_app:
                running_apps = [current_app]

            # Get the state
            # TODO: determine the state differently based on the `current_app`.
            if current_app in [APP_PACKAGE_LAUNCHER, APP_PACKAGE_SETTINGS]:
                state = constants.STATE_STANDBY

            # Amazon Video
            elif current_app == constants.APP_AMAZON_VIDEO:
                if wake_lock_size == 5:
                    state = constants.STATE_PLAYING
                else:
                    # wake_lock_size == 2
                    state = constants.STATE_PAUSED

            # Netflix
            elif current_app == constants.APP_NETFLIX:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Jellyfin
            elif current_app == constants.APP_JELLYFIN_TV:
                if wake_lock_size == 2:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_PAUSED

            # Spotify
            elif current_app == constants.APP_SPOTIFY:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Waipu TV
            elif current_app == constants.APP_WAIPU_TV:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Firefox
            elif current_app == constants.APP_FIREFOX:
                if wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Sport 1
            elif current_app == constants.APP_SPORT1:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Twitch
            elif current_app == constants.APP_TWITCH:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                elif media_session_state == 4:
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

            # Get the state from `wake_lock_size`
            else:
                if wake_lock_size == 1:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_PAUSED

        return state, current_app, running_apps

    # ======================================================================= #
    #                                                                         #
    #                              App methods                                #
    #                                                                         #
    # ======================================================================= #
    def launch_app(self, app):
        """Launch an app.

        Parameters
        ----------
        app : str
            The ID of the app that will be launched

        Returns
        -------
        dict
            A dictionary with keys ``'output'`` and ``'retcode'``, if they could be determined; otherwise, an empty dictionary

        """
        return self._send_intent(app, INTENT_LAUNCH)

    def stop_app(self, app):
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
        return self.adb_shell("am force-stop {0}".format(app))

    # ======================================================================= #
    #                                                                         #
    #                               properties                                #
    #                                                                         #
    # ======================================================================= #
    def get_properties(self, get_running_apps=True, lazy=False):
        """Get the properties needed for Home Assistant updates.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the ``running_apps`` property
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
        running_apps : list, None
            A list of the running apps, or ``None`` if it was not determined

        """
        if get_running_apps:
            output = self.adb_shell(constants.CMD_SCREEN_ON + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                    constants.CMD_AWAKE + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                    constants.CMD_WAKE_LOCK_SIZE + " && (" +
                                    constants.CMD_MEDIA_SESSION_STATE + " || echo) && " +
                                    constants.CMD_CURRENT_APP + " && " +
                                    constants.CMD_RUNNING_APPS)
        else:
            output = self.adb_shell(constants.CMD_SCREEN_ON + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                    constants.CMD_AWAKE + (constants.CMD_SUCCESS1 if lazy else constants.CMD_SUCCESS1_FAILURE0) + " && " +
                                    constants.CMD_WAKE_LOCK_SIZE + " && (" +
                                    constants.CMD_MEDIA_SESSION_STATE + " || echo) && " +
                                    constants.CMD_CURRENT_APP)

        # ADB command was unsuccessful
        if output is None:
            return None, None, None, None, None, None

        # `screen_on` property
        if not output:
            return False, False, -1, None, None, None
        screen_on = output[0] == '1'

        # `awake` property
        if len(output) < 2:
            return screen_on, False, -1, None, None, None
        awake = output[1] == '1'

        lines = output.strip().splitlines()

        # `wake_lock_size` property
        if len(lines[0]) < 3:
            return screen_on, awake, -1, None, None, None
        wake_lock_size = self._wake_lock_size(lines[0])

        # `media_session_state` property
        if len(lines) < 2:
            return screen_on, awake, wake_lock_size, None, None, None
        media_session_state = self._media_session_state(lines[1])

        # `current_app` property
        if len(lines) < 3:
            return screen_on, awake, wake_lock_size, media_session_state, None, None
        current_app = self._current_app(lines[2])

        # `running_apps` property
        if not get_running_apps or len(lines) < 4:
            return screen_on, awake, wake_lock_size, media_session_state, current_app, None
        running_apps = self._running_apps(lines[3:])

        return screen_on, awake, wake_lock_size, media_session_state, current_app, running_apps

    def get_properties_dict(self, get_running_apps=True, lazy=True):
        """Get the properties needed for Home Assistant updates and return them as a dictionary.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the ``running_apps`` property
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        dict
             A dictionary with keys ``'screen_on'``, ``'awake'``, ``'wake_lock_size'``, ``'media_session_state'``,
             ``'current_app'``, and ``'running_apps'``

        """
        screen_on, awake, wake_lock_size, media_session_state, current_app, running_apps = self.get_properties(get_running_apps=get_running_apps, lazy=lazy)

        return {'screen_on': screen_on,
                'awake': awake,
                'wake_lock_size': wake_lock_size,
                'media_session_state': media_session_state,
                'current_app': current_app,
                'running_apps': running_apps}

    # ======================================================================= #
    #                                                                         #
    #                           turn on/off methods                           #
    #                                                                         #
    # ======================================================================= #
    def turn_on(self):
        """Send ``POWER`` and ``HOME`` actions if the device is off."""
        self.adb_shell(constants.CMD_SCREEN_ON + " || (input keyevent {0} && input keyevent {1})".format(constants.KEY_POWER, constants.KEY_HOME))

    def turn_off(self):
        """Send ``SLEEP`` action if the device is not off."""
        self.adb_shell(constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_SLEEP))
