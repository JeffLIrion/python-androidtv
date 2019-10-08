python-androidtv
================

.. image:: https://travis-ci.com/JeffLIrion/python-androidtv.svg?branch=master
   :target: https://travis-ci.com/JeffLIrion/python-androidtv
   :alt: Build Status
.. image:: https://coveralls.io/repos/github/JeffLIrion/python-androidtv/badge.svg
   :target: https://coveralls.io/github/JeffLIrion/python-androidtv
   :alt: Coverage Status

Documentation for this package can be found at `https://androidtv.readthedocs.io <https://androidtv.readthedocs.io>`_.

``androidtv`` is a Python 3 package that provides state information and control of Android TV and Fire TV devices via ADB.  This package is used by the `Android TV <https://www.home-assistant.io/components/androidtv/>`_ integration in Home Assistant.


Installation
------------

Be sure you install into a Python 3.x environment.

.. code-block:: bash

   pip install androidtv


ADB Intents and Commands
------------------------

A collection of useful intents and commands can be found `here <https://gist.github.com/mcfrojd/9e6875e1db5c089b1e3ddeb7dba0f304>`_ (credit: mcfrojd).

Acknowledgments
---------------

This is based on `python-firetv <https://github.com/happyleavesaoc/python-firetv>`_ by happyleavesaoc and the `androidtv component for Home Assistant <https://github.com/a1ex4/home-assistant/blob/androidtv/homeassistant/components/media_player/androidtv.py>`_ by a1ex4, and it depends on the Python packages `adb-shell <https://github.com/JeffLIrion/adb_shell>`_ (which is based on `python-adb <https://github.com/google/python-adb>`_) and `pure-python-adb <https://github.com/Swind/pure-python-adb>`_.
