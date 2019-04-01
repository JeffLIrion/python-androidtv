ADB Setup
=========

This package works by sending ADB commands to your Android TV / Fire TV device.  There are two ways to accomplish this.  


1. ADB Server
-------------

``androidtv`` can use a running ADB server to send ADB commands (credit: `pure-python-adb <https://github.com/Swind/pure-python-adb/tree/master/adb>`_).  More info about ADB can be found here: `Android Debug Bridge (adb) <https://developer.android.com/studio/command-line/adb.html>`_.  There are 3 main ways to setup an ADB server.  

.. note:: The ADB server must be connected to your device(s) before starting Home Assistant.  Otherwise, the components will not be setup.


1a) Hass.io ADB Addon
*********************

For Hass.io users, this is the easiest option.  Information about the addon can be found here: `Community Hass.io Add-ons: Android Debug Bridge <https://github.com/hassio-addons/addon-adb/blob/master/README.md>`_.  The configuration for the addon will look like:

.. code-block:: json

   {
     "log_level": "info",
     "devices": [
       "192.168.0.111",
       "192.168.0.222"
     ],
     "reconnect_timeout": 90,
     "keys_path": "/config/.android"
   }


Your Home Assistant configuration will look like:

.. code-block:: yaml

   media_player:
   - platform: androidtv
     name: Android TV 1
     host: 192.168.0.111
     adb_server_ip: 127.0.0.1

   media_player:
   - platform: androidtv
     name: Android TV 2
     host: 192.168.0.222
     adb_server_ip: 127.0.0.1


1b) Docker Container
********************

Since Home Assistant isn't able to start the connection with the Android device directly, the ADB Server must do it instead. The ADB Server **must already be connected** to the Android device when Home Assistant attempts to access the ADB Server, or else Home Assistant will be unable to set up the Android device.

A modified script provided on the Home Assistant forums (`source <https://community.home-assistant.io/t/native-support-for-fire-tv/64448/300>`_) demonstrates an example startup script for a Docker container that will automatically attempt, and continue to connect to a device when run:

.. code-block:: sh
   :caption: **startup.sh**

   #!/bin/sh

   # for a single device, use: DEVICES=("192.168.0.111")
   DEVICES=("192.168.0.111" "192.168.0.222")

   echo "Starting up ADB..."

   while true; do
     adb -a server nodaemon > /dev/null 2>&1
     sleep 10
   done &

   echo "Server started. Waiting for 30 seconds..."
   sleep 30

   echo "Connecting to devices."
   for device in ${DEVICES[@]}; do
      adb connect $device
   done
   echo "Done."

   while true; do
     for device in ${DEVICES[@]}; do
       adb connect $device > /dev/null 2>&1
     done
     sleep 60
   done


Assuming the address of the ADB server is 192.168.0.101, your Home Assistant configuration will look like:

.. code-block:: yaml

   media_player:
   - platform: androidtv
     name: Android TV 1
     host: 192.168.0.111
     adb_server_ip: 192.168.0.101

   media_player:
   - platform: androidtv
     name: Android TV 2
     host: 192.168.0.222
     adb_server_ip: 192.168.0.101


1c) Linux Service
*****************

TODO

Your Home Assistant configuration will look like:

.. code-block:: yaml

   media_player:
   - platform: androidtv
     name: Android TV 1
     host: 192.168.0.111
     adb_server_ip: 127.0.0.1

   media_player:
   - platform: androidtv
     name: Android TV 2
     host: 192.168.0.222
     adb_server_ip: 127.0.0.1


2. Python ADB Implementation
----------------------------

The second way that ``androidtv`` can communicate with devices is using the Python ADB implementation (credit: `python-adb <https://github.com/google/python-adb>`_).  

If your device requires ADB authentication, you will need to follow the instructions in the "ADB Authentication" section below. Once you have an authenticated key, this approach does not require any additional setup or addons. However, users with newer devices may find that the ADB connection is unstable. For a Fire TV device, you can try setting the ``get_sources`` configuration option to ``false``. If the problem cannot be resolved, you should use the ADB server option.

Assuming you have 2 devices that require authentication, your configuration will look like this (update the ``adbkey`` path accordingly):

.. code-block:: yaml

   media_player:
   - platform: androidtv
     name: Android TV 1
     host: 192.168.0.111
     adbkey: "/config/.android/adbkey"

   media_player:
   - platform: androidtv
     name: Android TV 2
     host: 192.168.0.222
     adbkey: "/config/.android/adbkey"


ADB Authentication
******************

If you get a “Device authentication required, no keys available” error when trying to set up your Android TV or Fire TV, then you’ll need to create an adbkey and add its path to your configuration. Follow the instructions on this page to connect to your device from your computer: `Connecting to Fire TV Through adb <https://developer.amazon.com/zh/docs/fire-tv/connecting-adb-to-device.html>`_.

.. note:: In the dialog appearing on your Android TV / Fire TV, you must check the box that says “always allow connections from this device.” ADB authentication in Home Assistant will only work using a trusted key.

Once you’ve successfully connected to your Android TV / Fire TV via the command ``adb connect <ipaddress>``, the file ``adbkey`` will be created on your computer. The default location for this file is (from `https://developer.android.com/studio/command-line/adb <https://developer.android.com/studio/command-line/adb>`_):

* Linux and Mac: ``$HOME/.android``
* Windows: ``%userprofile%\.android``

Copy the ``adbkey`` file to your Home Assistant folder and add the path to your configuration.
