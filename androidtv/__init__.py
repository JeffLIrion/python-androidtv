"""Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

ADB Debugging must be enabled.
"""

from .androidtv.androidtv_sync import AndroidTVSync
from .basetv.basetv import state_detection_rules_validator
from .basetv.basetv_sync import BaseTVSync
from .constants import DEFAULT_AUTH_TIMEOUT_S, DEFAULT_TRANSPORT_TIMEOUT_S
from .firetv.firetv_sync import FireTVSync


__version__ = "0.0.64"


def setup(
    host,
    port=5555,
    adbkey="",
    adb_server_ip="",
    adb_server_port=5037,
    state_detection_rules=None,
    device_class="auto",
    auth_timeout_s=DEFAULT_AUTH_TIMEOUT_S,
    signer=None,
    transport_timeout_s=DEFAULT_TRANSPORT_TIMEOUT_S,
):
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
        The signer for the ADB keys, as loaded by :meth:`androidtv.adb_manager.adb_manager_sync.ADBPythonSync.load_adbkey`
    transport_timeout_s : float
        Transport timeout (in seconds)

    Returns
    -------
    AndroidTVSync, FireTVSync
        The representation of the device

    """
    if device_class == "androidtv":
        atv = AndroidTVSync(host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)
        atv.adb_connect(auth_timeout_s=auth_timeout_s, transport_timeout_s=transport_timeout_s)
        atv.get_device_properties()
        atv.get_installed_apps()
        return atv

    if device_class == "firetv":
        ftv = FireTVSync(host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)
        ftv.adb_connect(auth_timeout_s=auth_timeout_s, transport_timeout_s=transport_timeout_s)
        ftv.get_device_properties()
        ftv.get_installed_apps()
        return ftv

    if device_class != "auto":
        raise ValueError("`device_class` must be 'androidtv', 'firetv', or 'auto'.")

    aftv = BaseTVSync(host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, signer)

    # establish the ADB connection
    aftv.adb_connect(auth_timeout_s=auth_timeout_s, transport_timeout_s=transport_timeout_s)

    # get device properties
    aftv.device_properties = aftv.get_device_properties()

    # get the installed apps
    aftv.get_installed_apps()

    # Fire TV
    if aftv.device_properties.get("manufacturer") == "Amazon":
        return FireTVSync.from_base(aftv)

    # Android TV
    return AndroidTVSync.from_base(aftv)


def ha_state_detection_rules_validator(exc):
    """Validate the rules (i.e., the ``state_detection_rules`` value) for a given app ID (i.e., a key in ``state_detection_rules``).

    See :class:`~androidtv.basetv.basetv.BaseTV` for more info about the ``state_detection_rules`` parameter.

    Parameters
    ----------
    exc : Exception
        The exception that will be raised if a rule is invalid

    Returns
    -------
    wrapped_state_detection_rules_validator : function
        A function that is the same as :func:`~androidtv.basetv.state_detection_rules_validator`, but with the ``exc`` argument provided

    """

    def wrapped_state_detection_rules_validator(rules):
        """Run :func:`~androidtv.basetv.state_detection_rules_validator` using the ``exc`` parameter from the parent function."""
        return state_detection_rules_validator(rules, exc)

    return wrapped_state_detection_rules_validator
