"""Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

ADB Debugging must be enabled.
"""

from .androidtv import AndroidTV
from .basetv import BaseTV
from .firetv import FireTV


def setup(host, adbkey='', adb_server_ip='', adb_server_port=5037, state_detection_rules=None, device_class='auto'):
    """Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

    Parameters
    ----------
    host : str
        The address of the device in the format ``<ip address>:<host>``
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication
    adb_server_ip : str
        The IP address of the ADB server
    adb_server_port : int
        The port for the ADB server
    state_detection_rules : dict, None
        A dictionary of rules for determining the state (see :class:`~androidtv.basetv.BaseTV`)
    device_class : str
        The type of device: ``'auto'`` (detect whether it is an Android TV or Fire TV device), ``'androidtv'``, or ``'firetv'```

    Returns
    -------
    aftv : AndroidTV, FireTV
        The representation of the device

    """
    if device_class == 'androidtv':
        return AndroidTV(host, adbkey, adb_server_ip, adb_server_port, state_detection_rules)

    if device_class == 'firetv':
        return FireTV(host, adbkey, adb_server_ip, adb_server_port, state_detection_rules)

    if device_class != 'auto':
        raise ValueError("`device_class` must be 'androidtv', 'firetv', or 'auto'.")

    aftv = BaseTV(host, adbkey, adb_server_ip, adb_server_port, state_detection_rules)

    # Fire TV
    if aftv.device_properties.get('manufacturer') == 'Amazon':
        aftv.__class__ = FireTV

    # Android TV
    else:
        aftv.__class__ = AndroidTV

    return aftv
