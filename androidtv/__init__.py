"""Connect to a device and determine whether it's an Android TV or an Amazon Fire TV.

ADB Debugging must be enabled.
"""

from .androidtv import AndroidTV
from .basetv import BaseTV
from .firetv import FireTV


def setup(host, adbkey='', adb_server_ip='', adb_server_port=5037, device_class='auto'):
    """Docstring

    """
    if device_class == 'androidtv':
        return AndroidTV(host, adbkey, adb_server_ip, adb_server_port)

    if device_class == 'firetv':
        return FireTV(host, adbkey, adb_server_ip, adb_server_port)

    if device_class != 'auto':
        raise ValueError("`device_class` must be 'androidtv', 'firetv', or 'auto'.")

    aftv = BaseTV(host, adbkey, adb_server_ip, adb_server_port)

    # Fire TV
    if aftv.manufacturer == 'Amazon':
        aftv.__class__ = FireTV

    # Android TV
    else:
        aftv.__class__ = AndroidTV
        if aftv._available:
            aftv.device_properties = aftv.get_device_properties()

    return aftv
