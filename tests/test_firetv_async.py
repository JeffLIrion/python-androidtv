import sys
import unittest
from unittest.mock import patch


sys.path.insert(0, '..')

from androidtv import constants, ha_state_detection_rules_validator
from androidtv.firetv.firetv_async import FireTVAsync

from . import async_patchers
from .async_wrapper import awaiter


CURRENT_APP_OUTPUT = "com.amazon.tv.launcher"

RUNNING_APPS_OUTPUT = """u0_a18    316   197   1189204 115000 ffffffff 00000000 S com.netflix.ninja
u0_a2     15121 197   998628 24628 ffffffff 00000000 S com.amazon.device.controllermanager"""

RUNNING_APPS_LIST = ['com.netflix.ninja', 'com.amazon.device.controllermanager']

GET_PROPERTIES_OUTPUT1 = ""
GET_PROPERTIES_DICT1 = {'screen_on': False,
                        'awake': False,
                        'wake_lock_size': -1,
                        'current_app': None,
                        'media_session_state': None,
                        'running_apps': None}
STATE1 = (constants.STATE_OFF, None, None)

GET_PROPERTIES_OUTPUT2 = "1"
GET_PROPERTIES_DICT2 = {'screen_on': True,
                        'awake': False,
                        'wake_lock_size': -1,
                        'current_app': None,
                        'media_session_state': None,
                        'running_apps': None}
STATE2 = (constants.STATE_STANDBY, None, None)

GET_PROPERTIES_OUTPUT3 = """11Wake Locks: size=2
com.amazon.tv.launcher

u0_a2     17243 197   998628 24932 ffffffff 00000000 S com.amazon.device.controllermanager
u0_a2     17374 197   995368 20764 ffffffff 00000000 S com.amazon.device.controllermanager:BluetoothReceiver"""
GET_PROPERTIES_DICT3 = {'screen_on': True,
                        'awake': True,
                        'wake_lock_size': 2,
                        'current_app': 'com.amazon.tv.launcher',
                        'media_session_state': None,
                        'running_apps': ['com.amazon.device.controllermanager', 'com.amazon.device.controllermanager:BluetoothReceiver']}
STATE3 = (constants.STATE_IDLE, 'com.amazon.tv.launcher', ['com.amazon.device.controllermanager', 'com.amazon.device.controllermanager:BluetoothReceiver'])

GET_PROPERTIES_OUTPUT3A = GET_PROPERTIES_OUTPUT3[0]
GET_PROPERTIES_OUTPUT3B = GET_PROPERTIES_OUTPUT3[:2]
GET_PROPERTIES_OUTPUT3C = GET_PROPERTIES_OUTPUT3.splitlines()[0]
GET_PROPERTIES_OUTPUT3D = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:2])
GET_PROPERTIES_OUTPUT3E = '\n'.join(GET_PROPERTIES_OUTPUT3.splitlines()[:3])

GET_PROPERTIES_DICT3A = {'screen_on': True,
                         'awake': False,
                         'wake_lock_size': -1,
                         'current_app': None,
                         'media_session_state': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3B = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': -1,
                         'current_app': None,
                         'media_session_state': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3C = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': 2,
                         'current_app': None,
                         'media_session_state': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3D = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': 2,
                         'current_app': 'com.amazon.tv.launcher',
                         'media_session_state': None,
                         'running_apps': None}
GET_PROPERTIES_DICT3E = {'screen_on': True,
                         'awake': True,
                         'wake_lock_size': 2,
                         'current_app': 'com.amazon.tv.launcher',
                         'media_session_state': None,
                         'running_apps': None}

GET_PROPERTIES_OUTPUT4 = """11Wake Locks: size=2
com.amazon.tv.launcher
state=PlaybackState {state=2, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}"""
GET_PROPERTIES_DICT4 = {'screen_on': True,
                        'awake': True,
                        'wake_lock_size': 2,
                        'current_app': 'com.amazon.tv.launcher',
                        'media_session_state': 2,
                        'running_apps': None}

GET_PROPERTIES_OUTPUT5 = """11Wake Locks: size=2
com.amazon.tv.launcher
state=PlaybackState {state=2, position=0, buffered position=0, speed=0.0, updated=65749, actions=240640, custom actions=[], active item id=-1, error=null}
u0_a2     17243 197   998628 24932 ffffffff 00000000 S com.amazon.device.controllermanager
u0_a2     17374 197   995368 20764 ffffffff 00000000 S com.amazon.device.controllermanager:BluetoothReceiver"""
GET_PROPERTIES_DICT5 = {'screen_on': True,
                        'awake': True,
                        'wake_lock_size': 2,
                        'current_app': 'com.amazon.tv.launcher',
                        'media_session_state': 2,
                        'running_apps': ['com.amazon.device.controllermanager', 'com.amazon.device.controllermanager:BluetoothReceiver']}

GET_PROPERTIES_DICT_NONE = {'screen_on': None,
                            'awake': None,
                            'wake_lock_size': None,
                            'media_session_state': None,
                            'current_app': None,
                            'running_apps': None}
STATE_NONE = (None, None, None)

STATE_DETECTION_RULES1 = {'com.amazon.tv.launcher': ['off']}
STATE_DETECTION_RULES2 = {'com.amazon.tv.launcher': ['media_session_state', 'off']}
STATE_DETECTION_RULES3 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 2}}]}
STATE_DETECTION_RULES4 = {'com.amazon.tv.launcher': [{'standby': {'wake_lock_size': 1}}, 'paused']}
STATE_DETECTION_RULES5 = {'com.amazon.tv.launcher': ['audio_state']}


class TestFireTVAsyncPython(unittest.TestCase):
    ADB_ATTR = '_adb'
    PATCH_KEY = 'python'

    @awaiter
    async def setUp(self):
        with async_patchers.PATCH_ADB_DEVICE_TCP, async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('')[self.PATCH_KEY]:
            self.ftv = FireTVAsync('HOST', 5555)
            await self.ftv.adb_connect()

    @awaiter
    async def test_turn_on_off(self):
        """Test that the ``FireTVAsync.turn_on`` and ``FireTVAsync.turn_off`` methods work correctly.

        """
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('')[self.PATCH_KEY]:
            await self.ftv.turn_on()
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " || (input keyevent {0} && input keyevent {1})".format(constants.KEY_POWER, constants.KEY_HOME))

            await self.ftv.turn_off()
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_SLEEP))

    @awaiter
    async def test_send_intent(self):
        """Test that the ``_send_intent`` method works correctly.

        """
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('output\r\nretcode')[self.PATCH_KEY]:
            result = await self.ftv._send_intent("TEST", constants.INTENT_LAUNCH)
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, "monkey -p TEST -c android.intent.category.LAUNCHER 1; echo $?")
            self.assertDictEqual(result, {'output': 'output', 'retcode': 'retcode'})

        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell(None)[self.PATCH_KEY]:
            result = await self.ftv._send_intent("TEST", constants.INTENT_LAUNCH)
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, "monkey -p TEST -c android.intent.category.LAUNCHER 1; echo $?")
            self.assertDictEqual(result, {})

    @awaiter
    async def test_launch_app_stop_app(self):
        """Test that the ``FireTVAsync.launch_app`` and ``FireTVAsync.stop_app`` methods work correctly.

        """
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('')[self.PATCH_KEY]:
            await self.ftv.launch_app("TEST")
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, constants.CMD_LAUNCH_APP.format("TEST"))

            await self.ftv.stop_app("TEST")
            self.assertEqual(getattr(self.ftv._adb, self.ADB_ATTR).shell_cmd, "am force-stop TEST")

    @awaiter
    async def test_running_apps(self):
        """Check that the ``running_apps`` property works correctly.

        """
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            running_apps = await self.ftv.running_apps()
            self.assertIsNone(running_apps, None)

        with async_patchers.patch_shell('')[self.PATCH_KEY]:
            running_apps = await self.ftv.running_apps()
            self.assertIsNone(running_apps, None)

        with async_patchers.patch_shell(RUNNING_APPS_OUTPUT)[self.PATCH_KEY]:
            running_apps = await self.ftv.running_apps()
            self.assertListEqual(running_apps, RUNNING_APPS_LIST)

    @awaiter
    async def test_get_properties(self):
        """Check that ``get_properties()`` works correctly.

        """
        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT_NONE)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT1)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT2)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3A)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3A)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3B)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3B)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3C)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3C)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3D)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3D)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3E)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3E)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3E)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True, get_running_apps=False)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3E)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3E)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=False, get_running_apps=False)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT3E)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT4)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT4)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT4)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True, get_running_apps=False)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT4)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT5)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=True)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT5)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT5)[self.PATCH_KEY]:
            properties = await self.ftv.get_properties_dict(lazy=False)
            self.assertDictEqual(properties, GET_PROPERTIES_DICT5)

    @awaiter
    async def test_update(self):
        """Check that the ``update`` method works correctly.

        """
        with async_patchers.patch_connect(False)[self.PATCH_KEY]:
            await self.ftv.adb_connect()
        state = await self.ftv.update()
        self.assertTupleEqual(state, STATE_NONE)

        with async_patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(await self.ftv.adb_connect())

        with async_patchers.patch_shell(None)[self.PATCH_KEY]:
            state = await self.ftv.update()
            self.assertTupleEqual(state, STATE_NONE)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT1)[self.PATCH_KEY]:
            state = await self.ftv.update()
            self.assertTupleEqual(state, STATE1)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT2)[self.PATCH_KEY]:
            state = await self.ftv.update()
            self.assertTupleEqual(state, STATE2)

        with async_patchers.patch_shell(GET_PROPERTIES_OUTPUT3)[self.PATCH_KEY]:
            state = await self.ftv.update()
            self.assertTupleEqual(state, STATE3)

            self.ftv._state_detection_rules = STATE_DETECTION_RULES1
            state = await self.ftv.update()
            self.assertEqual(state[0], constants.STATE_OFF)

            self.ftv._state_detection_rules = STATE_DETECTION_RULES2
            state = await self.ftv.update()
            self.assertEqual(state[0], constants.STATE_OFF)

            self.ftv._state_detection_rules = STATE_DETECTION_RULES3
            state = await self.ftv.update()
            self.assertEqual(state[0], constants.STATE_STANDBY)

            self.ftv._state_detection_rules = STATE_DETECTION_RULES4
            state = await self.ftv.update()
            self.assertEqual(state[0], constants.STATE_PAUSED)

            self.ftv._state_detection_rules = STATE_DETECTION_RULES5
            state = await self.ftv.update()
            self.assertEqual(state[0], constants.STATE_IDLE)

    async def assertUpdate(self, get_properties, update):
        """Check that the results of the `update` method are as expected.

        """
        with patch('androidtv.firetv.firetv_async.FireTVAsync.get_properties', return_value=get_properties, new_callable=async_patchers.AsyncMock):
            self.assertTupleEqual(await self.ftv.update(), update)

    @awaiter
    async def test_state_detection(self):
        """Check that the state detection works as expected.

        """
        await self.assertUpdate([False, None, -1, None, None, None],
                                (constants.STATE_OFF, None, None))

        await self.assertUpdate([True, False, -1, None, None, None],
                                (constants.STATE_STANDBY, None, None))

        await self.assertUpdate([True, True, 1, "com.amazon.tv.launcher", None, None],
                                (constants.STATE_IDLE, "com.amazon.tv.launcher", ["com.amazon.tv.launcher"]))

        # Amazon Video
        await self.assertUpdate([True, True, 1, constants.APP_AMAZON_VIDEO, 3, [constants.APP_AMAZON_VIDEO]],
                                (constants.STATE_PLAYING, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO]))

        await self.assertUpdate([True, True, 1, constants.APP_AMAZON_VIDEO, 2, [constants.APP_AMAZON_VIDEO]],
                                (constants.STATE_PAUSED, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO]))

        await self.assertUpdate([True, True, 1, constants.APP_AMAZON_VIDEO, 1, [constants.APP_AMAZON_VIDEO]],
                                (constants.STATE_IDLE, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO]))

        # Amazon Video with custom state detection rules
        self.ftv._state_detection_rules = {constants.APP_AMAZON_VIDEO: ['media_session_state']}

        await self.assertUpdate([True, True, 2, constants.APP_AMAZON_VIDEO, 2, [constants.APP_AMAZON_VIDEO]],
                                (constants.STATE_PAUSED, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO]))

        await self.assertUpdate([True, True, 5, constants.APP_AMAZON_VIDEO, 3, [constants.APP_AMAZON_VIDEO]],
                                (constants.STATE_PLAYING, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO]))

        await self.assertUpdate([True, True, 5, constants.APP_AMAZON_VIDEO, 1, [constants.APP_AMAZON_VIDEO]],
                                (constants.STATE_IDLE, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO]))

        self.ftv._state_detection_rules = {constants.APP_AMAZON_VIDEO: [{'standby': {'media_session_state': 2}}]}
        await self.assertUpdate([True, True, 2, constants.APP_AMAZON_VIDEO, None, [constants.APP_AMAZON_VIDEO]],
                                (constants.STATE_IDLE, constants.APP_AMAZON_VIDEO, [constants.APP_AMAZON_VIDEO]))

        # Firefox
        await self.assertUpdate([True, True, 3, constants.APP_FIREFOX, 3, [constants.APP_FIREFOX]],
                                (constants.STATE_PLAYING, constants.APP_FIREFOX, [constants.APP_FIREFOX]))

        await self.assertUpdate([True, True, 1, constants.APP_FIREFOX, 3, [constants.APP_FIREFOX]],
                                (constants.STATE_IDLE, constants.APP_FIREFOX, [constants.APP_FIREFOX]))

        # Hulu
        await self.assertUpdate([True, True, 4, constants.APP_HULU, 3, [constants.APP_HULU]],
                                (constants.STATE_PLAYING, constants.APP_HULU, [constants.APP_HULU]))

        await self.assertUpdate([True, True, 2, constants.APP_HULU, 3, [constants.APP_HULU]],
                                (constants.STATE_PAUSED, constants.APP_HULU, [constants.APP_HULU]))

        await self.assertUpdate([True, True, 1, constants.APP_HULU, 3, [constants.APP_HULU]],
                                (constants.STATE_IDLE, constants.APP_HULU, [constants.APP_HULU]))

        # Jellyfin
        await self.assertUpdate([True, True, 2, constants.APP_JELLYFIN_TV, 3, [constants.APP_JELLYFIN_TV]],
                                (constants.STATE_PLAYING, constants.APP_JELLYFIN_TV, [constants.APP_JELLYFIN_TV]))

        await self.assertUpdate([True, True, 4, constants.APP_JELLYFIN_TV, 3, [constants.APP_JELLYFIN_TV]],
                                (constants.STATE_PAUSED, constants.APP_JELLYFIN_TV, [constants.APP_JELLYFIN_TV]))

        # Netfilx
        await self.assertUpdate([True, True, 1, constants.APP_NETFLIX, 3, [constants.APP_NETFLIX]],
                                (constants.STATE_PLAYING, constants.APP_NETFLIX, [constants.APP_NETFLIX]))

        await self.assertUpdate([True, True, 1, constants.APP_NETFLIX, 2, [constants.APP_NETFLIX]],
                                (constants.STATE_PAUSED, constants.APP_NETFLIX, [constants.APP_NETFLIX]))

        await self.assertUpdate([True, True, 1, constants.APP_NETFLIX, 1, [constants.APP_NETFLIX]],
                                (constants.STATE_IDLE, constants.APP_NETFLIX, [constants.APP_NETFLIX]))

        # Plex
        await self.assertUpdate([True, True, 1, constants.APP_PLEX, 3, [constants.APP_PLEX]],
                                (constants.STATE_PLAYING, constants.APP_PLEX, [constants.APP_PLEX]))

        await self.assertUpdate([True, True, 2, constants.APP_PLEX, 3, [constants.APP_PLEX]],
                                (constants.STATE_PAUSED, constants.APP_PLEX, [constants.APP_PLEX]))

        await self.assertUpdate([True, True, 1, constants.APP_PLEX, 1, [constants.APP_PLEX]],
                                (constants.STATE_IDLE, constants.APP_PLEX, [constants.APP_PLEX]))

        # Sport 1
        await self.assertUpdate([True, True, 3, constants.APP_SPORT1, 3, [constants.APP_SPORT1]],
                                (constants.STATE_PLAYING, constants.APP_SPORT1, [constants.APP_SPORT1]))

        await self.assertUpdate([True, True, 2, constants.APP_SPORT1, 3, [constants.APP_SPORT1]],
                                (constants.STATE_PAUSED, constants.APP_SPORT1, [constants.APP_SPORT1]))

        await self.assertUpdate([True, True, 1, constants.APP_SPORT1, 3, [constants.APP_SPORT1]],
                                (constants.STATE_IDLE, constants.APP_SPORT1, [constants.APP_SPORT1]))

        # Spotify
        await self.assertUpdate([True, True, 1, constants.APP_SPOTIFY, 3, [constants.APP_SPOTIFY]],
                                (constants.STATE_PLAYING, constants.APP_SPOTIFY, [constants.APP_SPOTIFY]))

        await self.assertUpdate([True, True, 1, constants.APP_SPOTIFY, 2, [constants.APP_SPOTIFY]],
                                (constants.STATE_PAUSED, constants.APP_SPOTIFY, [constants.APP_SPOTIFY]))

        await self.assertUpdate([True, True, 1, constants.APP_SPOTIFY, 1, [constants.APP_SPOTIFY]],
                                (constants.STATE_IDLE, constants.APP_SPOTIFY, [constants.APP_SPOTIFY]))

        # Twitch
        await self.assertUpdate([True, True, 2, constants.APP_TWITCH, 3, [constants.APP_TWITCH]],
                                (constants.STATE_PAUSED, constants.APP_TWITCH, [constants.APP_TWITCH]))

        await self.assertUpdate([True, True, 1, constants.APP_TWITCH, 3, [constants.APP_TWITCH]],
                                (constants.STATE_PLAYING, constants.APP_TWITCH, [constants.APP_TWITCH]))

        await self.assertUpdate([True, True, 1, constants.APP_TWITCH, 4, [constants.APP_TWITCH]],
                                (constants.STATE_PLAYING, constants.APP_TWITCH, [constants.APP_TWITCH]))

        await self.assertUpdate([True, True, 1, constants.APP_TWITCH, 1, [constants.APP_TWITCH]],
                                (constants.STATE_IDLE, constants.APP_TWITCH, [constants.APP_TWITCH]))

        # Waipu TV
        await self.assertUpdate([True, True, 3, constants.APP_WAIPU_TV, 1, [constants.APP_WAIPU_TV]],
                                (constants.STATE_PLAYING, constants.APP_WAIPU_TV, [constants.APP_WAIPU_TV]))

        await self.assertUpdate([True, True, 2, constants.APP_WAIPU_TV, 1, [constants.APP_WAIPU_TV]],
                                (constants.STATE_PAUSED, constants.APP_WAIPU_TV, [constants.APP_WAIPU_TV]))

        await self.assertUpdate([True, True, 1, constants.APP_WAIPU_TV, 1, [constants.APP_WAIPU_TV]],
                                (constants.STATE_IDLE, constants.APP_WAIPU_TV, [constants.APP_WAIPU_TV]))

        # Unknown app
        await self.assertUpdate([True, True, 1, 'unknown', 3, ['unknown']],
                                (constants.STATE_PLAYING, 'unknown', ['unknown']))

        await self.assertUpdate([True, True, 1, 'unknown', 2, ['unknown']],
                                (constants.STATE_PAUSED, 'unknown', ['unknown']))

        await self.assertUpdate([True, True, 1, 'unknown', 1, ['unknown']],
                                (constants.STATE_IDLE, 'unknown', ['unknown']))

        await self.assertUpdate([True, True, 1, 'unknown', None, ['unknown']],
                                (constants.STATE_PLAYING, 'unknown', ['unknown']))

        await self.assertUpdate([True, True, 2, 'unknown', None, ['unknown']],
                                (constants.STATE_PAUSED, 'unknown', ['unknown']))


class TestFireTVAsyncServer(TestFireTVAsyncPython):
    ADB_ATTR = '_adb_device'
    PATCH_KEY = 'server'

    @awaiter
    async def setUp(self):
        with async_patchers.patch_connect(True)[self.PATCH_KEY], async_patchers.patch_shell('')[self.PATCH_KEY]:
            self.ftv = FireTVAsync('HOST', 5555, adb_server_ip='ADB_SERVER_IP')
            await self.ftv.adb_connect()


if __name__ == "__main__":
    unittest.main()
