"""Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

ADB Debugging must be enabled.
"""

from .androidtv.androidtv_async import AndroidTVAsync
from .basetv.basetv_async import BaseTVAsync
from .constants import DEFAULT_AUTH_TIMEOUT_S
from .firetv.firetv_async import FireTVAsync


async def setup(host, port=5555, adbkey='', adb_server_ip='', adb_server_port=5037, state_detection_rules=None, device_class='auto', auth_timeout_s=DEFAULT_AUTH_TIMEOUT_S, signer=None):
    """Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

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
    device_class : str
        The type of device: ``'auto'`` (detect whether it is an Android TV or Fire TV device), ``'androidtv'``, or ``'firetv'```
    auth_timeout_s : float
        Authentication timeout (in seconds)
    signer : PythonRSASigner, None
        The signer for the ADB keys, as loaded by :meth:`androidtv.adb_manager.adb_manager_async.ADBPythonAsync.load_adbkey`

    Returns
    -------
    AndroidTVAsync, FireTVAsync
        The representation of the device

    """
    if device_class == 'androidtv':
        atv = AndroidTVAsync(host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)
        await atv.adb_connect(auth_timeout_s=auth_timeout_s)
        await atv.get_device_properties()
        await atv.get_installed_apps()
        return atv

    if device_class == 'firetv':
        ftv = FireTVAsync(host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)
        await ftv.adb_connect(auth_timeout_s=auth_timeout_s)
        await ftv.get_device_properties()
        await ftv.get_installed_apps()
        return ftv

    if device_class != 'auto':
        raise ValueError("`device_class` must be 'androidtv', 'firetv', or 'auto'.")

    aftv = BaseTVAsync(host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)

    # establish the ADB connection
    await aftv.adb_connect(auth_timeout_s=auth_timeout_s)

    # get device properties
    await aftv.get_device_properties()

    # get the installed apps
    await aftv.get_installed_apps()

    # Fire TV
    if aftv.device_properties.get('manufacturer') == 'Amazon':
        aftv.__class__ = FireTVAsync

    # Android TV
    else:
        aftv.__class__ = AndroidTVAsync

    # Fill in commands that are specific to the device
    aftv._fill_in_commands()  # pylint: disable=protected-access

    return aftv
