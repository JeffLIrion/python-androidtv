"""Communicate with an Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging

from .base_firetv import BaseFireTV
from ..basetv.basetv_async import BaseTVAsync
from .. import constants

_LOGGER = logging.getLogger(__name__)


class FireTVAsync(BaseTVAsync, BaseFireTV):
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
    signer : PythonRSASigner, None
        The signer for the ADB keys, as loaded by :meth:`androidtv.adb_manager.adb_manager_async.ADBPythonAsync.load_adbkey`

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
        BaseTVAsync.__init__(self, host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)

        # fill in commands that can vary based on the device
        BaseFireTV._fill_in_commands(self)

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    async def update(self, get_running_apps=True, lazy=True):
        """Get the info needed for a Home Assistant update.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :meth:`~androidtv.firetv.firetv_sync.FireTVSync.running_apps` property
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
        hdmi_input : str, None
            The HDMI input, or ``None`` if it could not be determined

        """
        # Get the properties needed for the update
        (
            screen_on,
            awake,
            wake_lock_size,
            current_app,
            media_session_state,
            running_apps,
            hdmi_input,
        ) = await self.get_properties(get_running_apps=get_running_apps, lazy=lazy)

        return self._update(
            screen_on, awake, wake_lock_size, current_app, media_session_state, running_apps, hdmi_input
        )

    # ======================================================================= #
    #                                                                         #
    #                               Properties                                #
    #                                                                         #
    # ======================================================================= #
    async def get_properties(self, get_running_apps=True, lazy=False):
        """Get the properties needed for Home Assistant updates.

        This will send one of the following ADB commands:

        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS`

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :meth:`~androidtv.firetv.firetv_async.FireTVAsync.running_apps` property
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
        current_app : str, None
            The current app property, or ``None`` if it was not determined
        media_session_state : int, None
            The state from the output of ``dumpsys media_session``, or ``None`` if it was not determined
        running_apps : list, None
            A list of the running apps, or ``None`` if it was not determined
        hdmi_input : str, None
            The HDMI input, or ``None`` if it could not be determined

        """
        if lazy:
            if get_running_apps:
                output = await self._adb.shell(self._cmd_get_properties_lazy_running_apps)
            else:
                output = await self._adb.shell(self._cmd_get_properties_lazy_no_running_apps)
        else:
            if get_running_apps:
                output = await self._adb.shell(self._cmd_get_properties_not_lazy_running_apps)
            else:
                output = await self._adb.shell(self._cmd_get_properties_not_lazy_no_running_apps)
        _LOGGER.debug("Fire TV %s:%d `get_properties` response: %s", self.host, self.port, output)

        return self._get_properties(output, get_running_apps)

    async def get_properties_dict(self, get_running_apps=True, lazy=True):
        """Get the properties needed for Home Assistant updates and return them as a dictionary.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :meth:`~androidtv.firetv.firetv_async.FireTVAsync.running_apps` property
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        dict
             A dictionary with keys ``'screen_on'``, ``'awake'``, ``'wake_lock_size'``, ``'current_app'``,
             ``'media_session_state'``, ``'running_apps'``, and ``'hdmi_input'``

        """
        (
            screen_on,
            awake,
            wake_lock_size,
            current_app,
            media_session_state,
            running_apps,
            hdmi_input,
        ) = await self.get_properties(get_running_apps=get_running_apps, lazy=lazy)

        return {
            "screen_on": screen_on,
            "awake": awake,
            "wake_lock_size": wake_lock_size,
            "current_app": current_app,
            "media_session_state": media_session_state,
            "running_apps": running_apps,
            "hdmi_input": hdmi_input,
        }

    async def running_apps(self):
        """Return a list of running user applications.

        Returns
        -------
        list
            A list of the running apps

        """
        running_apps_response = await self._adb.shell(constants.CMD_RUNNING_APPS_FIRETV)

        return self._running_apps(running_apps_response)

    # ======================================================================= #
    #                                                                         #
    #                           turn on/off methods                           #
    #                                                                         #
    # ======================================================================= #
    async def turn_on(self):
        """Send ``POWER`` and ``HOME`` actions if the device is off."""
        await self._adb.shell(
            constants.CMD_SCREEN_ON
            + " || (input keyevent {0} && input keyevent {1})".format(constants.KEY_POWER, constants.KEY_HOME)
        )

    async def turn_off(self):
        """Send ``SLEEP`` action if the device is not off."""
        await self._adb.shell(constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_SLEEP))
