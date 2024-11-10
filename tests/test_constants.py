import inspect
import os
import shlex
import subprocess
import sys
import unittest

sys.path.insert(0, "..")

from androidtv import constants

from .generate_test_constants import get_cmds


class TestConstants(unittest.TestCase):
    def setUp(self):
        self._cmds = []
        self._cmd_names = {}

    def assertCommand(self, value, expected_value):
        self.assertEqual(value, expected_value)
        self._cmds.append(self._cmd_names[value])

    @staticmethod
    def _exec(command):
        process = os.popen(command)
        output = process.read().strip()
        process.close()
        return output

    @staticmethod
    def _parse_current_app(dumpsys_output):
        return TestConstants._exec(
            'CURRENT_APP="' + dumpsys_output + '" && ' + constants.CMD_PARSE_CURRENT_APP + " && echo $CURRENT_APP"
        )

    @staticmethod
    def _hdmi_input(dumpsys_output):
        return TestConstants._exec(
            constants.CMD_HDMI_INPUT.replace("dumpsys activity starter", 'echo "' + dumpsys_output + '"')
        )

    def test_apps(self):
        """Test that the values (i.e., app names) in the ``APPS`` dict are unique."""
        apps_reversed = {val: key for key, val in constants.APPS.items()}
        self.assertEqual(len(constants.APPS), len(apps_reversed))

    def test_constants(self):
        """Test ADB shell commands.

        The contents of this test can be generated via the script tests/generate_test_constants.py.

        This is basically a form of version control for constants.

        """
        self.maxDiff = None

        # Generate a dictionary where the keys are the `CMD_*` strings and the values are their variable names
        cmds = get_cmds()
        self._cmd_names = {val: key for key, val in cmds.items()}

        # Check that each `CMD_*` is unique
        self.assertEqual(len(cmds), len(self._cmd_names))

        # CMD_AUDIO_STATE
        self.assertCommand(
            constants.CMD_AUDIO_STATE,
            r"dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')",
        )

        # CMD_AUDIO_STATE11
        self.assertCommand(
            constants.CMD_AUDIO_STATE11,
            r"CURRENT_AUDIO_STATE=$(dumpsys audio | sed -r -n '/[0-9]{2}-[0-9]{2}.*player piid:.*(state|event):(started|paused|stopped).*$/h; ${x;p;}') && echo $CURRENT_AUDIO_STATE | grep -q paused && echo -e '1\c' || { echo $CURRENT_AUDIO_STATE | grep -q started && echo '2\c' || echo '0\c' ; }",
        )

        # CMD_AWAKE
        self.assertCommand(constants.CMD_AWAKE, r"dumpsys power | grep mWakefulness | grep -q Awake")

        # CMD_CURRENT_APP
        self.assertCommand(
            constants.CMD_CURRENT_APP,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp') && CURRENT_APP=${CURRENT_APP#*ActivityRecord{* * } && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP%\}*} && echo $CURRENT_APP",
        )

        # CMD_CURRENT_APP11
        self.assertCommand(
            constants.CMD_CURRENT_APP11,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mInputMethod(Input)?Target') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP",
        )

        # CMD_CURRENT_APP12
        self.assertCommand(
            constants.CMD_CURRENT_APP12,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp|mObscuringWindow') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP",
        )

        # CMD_CURRENT_APP13
        self.assertCommand(
            constants.CMD_CURRENT_APP13,
            r"CURRENT_APP=$(dumpsys window windows | grep -E -m 1 'imeLayeringTarget|imeInputTarget|imeControlTarget') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP",
        )
        # CMD_CURRENT_APP_ASKEY_STI6130
        self.assertCommand(
            constants.CMD_CURRENT_APP_ASKEY_STI6130,
            r"CURRENT_APP=$(dumpsys window windows | grep -E -m 1 'imeLayeringTarget|imeInputTarget|imeControlTarget') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP ",
        )

        # CMD_CURRENT_APP_GOOGLE_TV
        self.assertCommand(
            constants.CMD_CURRENT_APP_GOOGLE_TV,
            r"CURRENT_APP=$(dumpsys activity a . | grep mResumedActivity) && CURRENT_APP=${CURRENT_APP#*ActivityRecord{* * } && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP%\}*} && echo $CURRENT_APP",
        )

        # CMD_CURRENT_APP_MEDIA_SESSION_STATE
        self.assertCommand(
            constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp') && CURRENT_APP=${CURRENT_APP#*ActivityRecord{* * } && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP%\}*} && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'",
        )

        # CMD_CURRENT_APP_MEDIA_SESSION_STATE11
        self.assertCommand(
            constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE11,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mInputMethod(Input)?Target') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'",
        )

        # CMD_CURRENT_APP_MEDIA_SESSION_STATE12
        self.assertCommand(
            constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE12,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp|mObscuringWindow') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'",
        )

        # CMD_CURRENT_APP_MEDIA_SESSION_STATE13
        self.assertCommand(
            constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE13,
            r"CURRENT_APP=$(dumpsys window windows | grep -E -m 1 'imeLayeringTarget|imeInputTarget|imeControlTarget') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'",
        )
        # CMD_CURRENT_APP_MEDIA_SESSION_STATE_ASKEY_STI6130
        self.assertCommand(
            constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE_ASKEY_STI6130,
            r"CURRENT_APP=$(dumpsys window windows | grep -E -m 1 'imeLayeringTarget|imeInputTarget|imeControlTarget') && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP##* } && echo $CURRENT_APP  && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'",
        )

        # CMD_CURRENT_APP_MEDIA_SESSION_STATE_GOOGLE_TV
        self.assertCommand(
            constants.CMD_CURRENT_APP_MEDIA_SESSION_STATE_GOOGLE_TV,
            r"CURRENT_APP=$(dumpsys activity a . | grep mResumedActivity) && CURRENT_APP=${CURRENT_APP#*ActivityRecord{* * } && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && CURRENT_APP=${CURRENT_APP%\}*} && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'",
        )

        # CMD_DEVICE_PROPERTIES
        self.assertCommand(
            constants.CMD_DEVICE_PROPERTIES,
            r"getprop ro.product.manufacturer && getprop ro.product.model && getprop ro.serialno && getprop ro.build.version.release && getprop ro.product.vendor.device",
        )

        # CMD_HDMI_INPUT
        self.assertCommand(
            constants.CMD_HDMI_INPUT,
            r"dumpsys activity starter | grep -E -o '(ExternalTv|HDMI)InputService/HW[0-9]' -m 1 | grep -o 'HW[0-9]'",
        )

        # CMD_HDMI_INPUT11
        self.assertCommand(
            constants.CMD_HDMI_INPUT11,
            r"(HDMI=$(dumpsys tv_input | grep 'ResourceClientProfile {.*}' | grep -o -E '(hdmi_port=[0-9]|TV)') && { echo ${HDMI/hdmi_port=/HW} | cut -d' ' -f1 ; }) || dumpsys activity starter | grep -E -o '(ExternalTv|HDMI)InputService/HW[0-9]' -m 1 | grep -o 'HW[0-9]'",
        )

        # CMD_INSTALLED_APPS
        self.assertCommand(constants.CMD_INSTALLED_APPS, r"pm list packages")

        # CMD_LAUNCH_APP
        self.assertCommand(
            constants.CMD_LAUNCH_APP,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp') && CURRENT_APP=${{CURRENT_APP#*ActivityRecord{{* * }} && CURRENT_APP=${{CURRENT_APP#*{{* * }} && CURRENT_APP=${{CURRENT_APP%%/*}} && CURRENT_APP=${{CURRENT_APP%\}}*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LEANBACK_LAUNCHER --pct-syskeys 0 1; fi",
        )

        # CMD_LAUNCH_APP11
        self.assertCommand(
            constants.CMD_LAUNCH_APP11,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mInputMethod(Input)?Target') && CURRENT_APP=${{CURRENT_APP%%/*}} && CURRENT_APP=${{CURRENT_APP##* }} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LEANBACK_LAUNCHER --pct-syskeys 0 1; fi",
        )

        # CMD_LAUNCH_APP12
        self.assertCommand(
            constants.CMD_LAUNCH_APP12,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp|mObscuringWindow') && CURRENT_APP=${{CURRENT_APP%%/*}} && CURRENT_APP=${{CURRENT_APP##* }} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LEANBACK_LAUNCHER --pct-syskeys 0 1; fi",
        )

        # CMD_LAUNCH_APP13
        self.assertCommand(
            constants.CMD_LAUNCH_APP13,
            r"CURRENT_APP=$(dumpsys window windows | grep -E -m 1 'imeLayeringTarget|imeInputTarget|imeControlTarget') && CURRENT_APP=${{CURRENT_APP%%/*}} && CURRENT_APP=${{CURRENT_APP##* }} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LEANBACK_LAUNCHER --pct-syskeys 0 1; fi",
        )

        # CMD_LAUNCH_APP_FIRETV
        self.assertCommand(
            constants.CMD_LAUNCH_APP_FIRETV,
            r"CURRENT_APP=$(dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp') && CURRENT_APP=${{CURRENT_APP#*ActivityRecord{{* * }} && CURRENT_APP=${{CURRENT_APP#*{{* * }} && CURRENT_APP=${{CURRENT_APP%%/*}} && CURRENT_APP=${{CURRENT_APP%\}}*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LAUNCHER --pct-syskeys 0 1; fi",
        )

        # CMD_LAUNCH_APP_GOOGLE_TV
        self.assertCommand(
            constants.CMD_LAUNCH_APP_GOOGLE_TV,
            r"CURRENT_APP=$(dumpsys activity a . | grep mResumedActivity) && CURRENT_APP=${{CURRENT_APP#*ActivityRecord{{* * }} && CURRENT_APP=${{CURRENT_APP#*{{* * }} && CURRENT_APP=${{CURRENT_APP%%/*}} && CURRENT_APP=${{CURRENT_APP%\}}*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LEANBACK_LAUNCHER --pct-syskeys 0 1; fi",
        )

        # CMD_MAC_ETH0
        self.assertCommand(constants.CMD_MAC_ETH0, r"ip addr show eth0 | grep -m 1 ether")

        # CMD_MAC_WLAN0
        self.assertCommand(constants.CMD_MAC_WLAN0, r"ip addr show wlan0 | grep -m 1 ether")

        # CMD_MANUFACTURER
        self.assertCommand(constants.CMD_MANUFACTURER, r"getprop ro.product.manufacturer")

        # CMD_MEDIA_SESSION_STATE
        self.assertCommand(
            constants.CMD_MEDIA_SESSION_STATE,
            r"dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'",
        )

        # CMD_MODEL
        self.assertCommand(constants.CMD_MODEL, r"getprop ro.product.model")

        # CMD_PRODUCT_ID
        self.assertCommand(constants.CMD_PRODUCT_ID, r"getprop ro.product.vendor.device")

        # CMD_RUNNING_APPS
        self.assertCommand(constants.CMD_RUNNING_APPS, r"ps -A | grep u0_a")

        # CMD_SCREEN_ON
        self.assertCommand(
            constants.CMD_SCREEN_ON,
            r"(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true' || dumpsys display | grep -q 'mScreenState=ON')",
        )

        # CMD_SCREEN_ON_AWAKE_WAKE_LOCK_SIZE
        self.assertCommand(
            constants.CMD_SCREEN_ON_AWAKE_WAKE_LOCK_SIZE,
            r"(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true' || dumpsys display | grep -q 'mScreenState=ON') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep Locks | grep 'size='",
        )

        # CMD_SERIALNO
        self.assertCommand(constants.CMD_SERIALNO, r"getprop ro.serialno")

        # CMD_STREAM_MUSIC
        self.assertCommand(constants.CMD_STREAM_MUSIC, r"dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        # CMD_TURN_OFF_ANDROIDTV
        self.assertCommand(
            constants.CMD_TURN_OFF_ANDROIDTV,
            r"(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true' || dumpsys display | grep -q 'mScreenState=ON') && input keyevent 26",
        )

        # CMD_TURN_OFF_FIRETV
        self.assertCommand(
            constants.CMD_TURN_OFF_FIRETV,
            r"(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true' || dumpsys display | grep -q 'mScreenState=ON') && input keyevent 223",
        )

        # CMD_TURN_ON_ANDROIDTV
        self.assertCommand(
            constants.CMD_TURN_ON_ANDROIDTV,
            r"(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true' || dumpsys display | grep -q 'mScreenState=ON') || input keyevent 26",
        )

        # CMD_TURN_ON_FIRETV
        self.assertCommand(
            constants.CMD_TURN_ON_FIRETV,
            r"(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true' || dumpsys display | grep -q 'mScreenState=ON') || (input keyevent 26 && input keyevent 3)",
        )

        # CMD_VERSION
        self.assertCommand(constants.CMD_VERSION, r"getprop ro.build.version.release")

        # CMD_VOLUME_SET_COMMAND
        self.assertCommand(constants.CMD_VOLUME_SET_COMMAND, r"media volume --show --stream 3 --set {}")

        # CMD_VOLUME_SET_COMMAND11
        self.assertCommand(
            constants.CMD_VOLUME_SET_COMMAND11,
            r"cmd media_session volume --show --stream 3 --set {}",
        )

        # CMD_WAKE_LOCK_SIZE
        self.assertCommand(constants.CMD_WAKE_LOCK_SIZE, r"dumpsys power | grep Locks | grep 'size='")

        # Assert that the keys were checked in alphabetical order
        self.assertEqual(self._cmds, sorted(cmds.keys()))

    @unittest.skipIf(sys.version_info.major == 2, "Test requires Python 3")
    def test_no_underscores(self):
        """Test that 'ANDROID_TV', 'BASE_TV', and 'FIRE_TV' do not appear in the code base."""
        cwd = os.path.join(os.path.dirname(__file__), "..")
        for underscore_name in ["ANDROID_TV", "BASE_TV", "FIRE_TV"]:
            with subprocess.Popen(
                shlex.split("git grep -l {} -- androidtv/".format(underscore_name)),
                cwd=cwd,
            ) as p:
                self.assertEqual(p.wait(), 1)

    def test_current_app_extraction_atv_launcher(self):
        dumpsys_output = """
            mCurrentFocus=Window{e74bb23 u0 com.google.android.tvlauncher/com.google.android.tvlauncher.MainActivity}
            mFocusedApp=AppWindowToken{c791eb8 token=Token{a6bad1b ActivityRecord{35dbb2a u0 com.google.android.tvlauncher/.MainActivity t2719}}}
        """
        current_app = self._parse_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_ATV_LAUNCHER)

    def test_current_app_extraction_atv_launcher_google_tv(self):
        dumpsys_output = """
            mResumedActivity: ActivityRecord{35dbb2a u0 com.google.android.tvlauncher/.MainActivity t2719}
        """
        current_app = self._parse_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_ATV_LAUNCHER)

    def test_current_app_extraction_sony_picture_off(self):
        dumpsys_output = """
            mCurrentFocus=Window{c52eaa8 u0 com.sony.dtv.sonysystemservice}
            mFocusedApp=AppWindowToken{11da138 token=Token{19ea99b ActivityRecord{c4d9aa u0 tunein.player/tunein.ui.leanback.ui.activities.TvHomeActivity t2424}}}
        """
        current_app = self._parse_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_TUNEIN)

    def test_current_app_extraction_intent_with_no_activity(self):
        dumpsys_output = """
            mCurrentFocus=Window{c52eaa8 u0 com.sony.dtv.sonysystemservice}
        """
        current_app = self._parse_current_app(dumpsys_output)

        self.assertEqual(current_app, "com.sony.dtv.sonysystemservice")

    def test_current_app_extraction_with_identifier_as_output(self):
        dumpsys_output = constants.APP_NETFLIX
        current_app = self._parse_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_NETFLIX)

    def test_hdmi_input(self):
        dumpsys_output = """
             Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.mediatek.tvinput%2F.hdmi.HDMIInputService%2FHW5 flg=0x10000000 cmp=org.droidtv.playtv/.PlayTvActivity (has extras) }
            mIntent=Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.mediatek.tvinput/.hdmi.HDMIInputService/HW5 flg=0x10000000 cmp=org.droidtv.playtv/.PlayTvActivity (has extras) }
        """
        hdmi_input = self._hdmi_input(dumpsys_output)

        self.assertEqual(hdmi_input, "HW5")

    def test_hdmi_input_sony(self):
        dumpsys_output = """
            ACTIVITY MANAGER ACTIVITIES (dumpsys activity starter)
            ActivityStarter:
              mCurrentUser=0
              mLastStartReason=startActivityAsUser
              mLastStartActivityTimeMs=4 Feb 2021 12:30:29
              mLastStartActivityResult=2
              mLastStartActivityRecord:
               packageName=com.sony.dtv.tvx processName=com.sony.dtv.tvx
               launchedFromUid=10134 launchedFromPackage=com.sony.dtv.tvx userId=0
               app=ProcessRecord{edc6562 3904:com.sony.dtv.tvx/u0a134}
               Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.sony.dtv.tvinput.external%2F.ExternalTvInputService%2FHW2 flg=0x10040000 cmp=com.sony.dtv.tvx/.MainActivity (has extras) }
               frontOfTask=true task=TaskRecord{9eecc8c #2830 A=com.sony.dtv.tvx U=0 StackId=1 sz=1}
               taskAffinity=com.sony.dtv.tvx
               realActivity=com.sony.dtv.tvx/.MainActivity
               baseDir=/system/priv-app/Tvx/Tvx.apk
               dataDir=/data/user/0/com.sony.dtv.tvx
               stateNotNeeded=false componentSpecified=false mActivityType=0
               compat={320dpi always-compat} labelRes=0x7f090048 icon=0x7f02006d theme=0x7f0b01c2
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               taskDescription: iconFilename=null label="null" primaryColor=ff8c0000
                backgroundColor=ff303030
                statusBarColor=ff000000
                navigationBarColor=ff000000
               launchFailed=false launchCount=0 lastLaunchTime=-1h46m13s561ms
               haveState=false icicle=null
               state=RESUMED stopped=false delayedResume=false finishing=false
               keysPaused=false inHistory=true visible=true sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_REMOVED
               fullscreen=true noDisplay=false immersive=false launchMode=3
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=APPLICATION_ACTIVITY_TYPE
               waitingVisible=false nowVisible=true lastVisibleTime=-8s281ms
               connections=[ConnectionRecord{c68246 u0 CR com.sony.dtv.osdplanevisibilitymanager/.OsdEnabler:@cf54e21}]
               resizeMode=RESIZE_MODE_RESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
               supportsPictureInPicture=true
               supportsPictureInPictureWhilePausing: true
              mLastHomeActivityStartResult=0
              mLastHomeActivityStartRecord:
               packageName=com.google.android.tvlauncher processName=com.google.android.tvlauncher
               launchedFromUid=0 launchedFromPackage=null userId=0
               app=ProcessRecord{b28e70e 4013:com.google.android.tvlauncher/u0a162}
               Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10800100 cmp=com.google.android.tvlauncher/.MainActivity }
               frontOfTask=true task=TaskRecord{1142677 #2719 A=.TvLauncher U=0 StackId=0 sz=1}
               taskAffinity=.TvLauncher
               realActivity=com.google.android.tvlauncher/.MainActivity
               baseDir=/data/app/com.google.android.tvlauncher-yGwF-XP6Zf5hV0DbQ9Z4gA==/base.apk
               dataDir=/data/user/0/com.google.android.tvlauncher
               stateNotNeeded=true componentSpecified=false mActivityType=1
               compat={320dpi always-compat} labelRes=0x7f12002b icon=0x7f0f0000 theme=0x7f130007
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               taskDescription: iconFilename=null label="null" primaryColor=ff37474f
                backgroundColor=ff303030
                statusBarColor=ff263238
                navigationBarColor=ff000000
               launchFailed=false launchCount=0 lastLaunchTime=-11h32m28s448ms
               haveState=true icicle=Bundle[mParcelledData.dataSize=1272]
               state=STOPPED stopped=true delayedResume=false finishing=false
               keysPaused=false inHistory=true visible=false sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_REMOVED
               fullscreen=true noDisplay=false immersive=false launchMode=2
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=HOME_ACTIVITY_TYPE
               waitingVisible=false nowVisible=false lastVisibleTime=-16s965ms
               resizeMode=RESIZE_MODE_UNRESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
              mStartActivity:
               packageName=com.sony.dtv.tvx processName=com.sony.dtv.tvx
               launchedFromUid=10134 launchedFromPackage=com.sony.dtv.tvx userId=0
               app=null
               Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.sony.dtv.tvinput.external%2F.ExternalTvInputService%2FHW2 flg=0x10440000 cmp=com.sony.dtv.tvx/.MainActivity (has extras) }
               frontOfTask=false task=TaskRecord{9eecc8c #2830 A=com.sony.dtv.tvx U=0 StackId=1 sz=1}
               taskAffinity=com.sony.dtv.tvx
               realActivity=com.sony.dtv.tvx/.MainActivity
               baseDir=/system/priv-app/Tvx/Tvx.apk
               dataDir=/data/user/0/com.sony.dtv.tvx
               stateNotNeeded=false componentSpecified=false mActivityType=0
               compat=null labelRes=0x7f090048 icon=0x7f02006d theme=0x7f0b01c2
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/?}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               launchFailed=false launchCount=0 lastLaunchTime=0
               haveState=true icicle=null
               state=INITIALIZING stopped=false delayedResume=false finishing=false
               keysPaused=false inHistory=false visible=false sleeping=false idle=false mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
               fullscreen=true noDisplay=false immersive=false launchMode=3
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=APPLICATION_ACTIVITY_TYPE
               resizeMode=RESIZE_MODE_RESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
               supportsPictureInPicture=true
               supportsPictureInPictureWhilePausing: false
              mIntent=Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.sony.dtv.tvinput.external/.ExternalTvInputService/HW2 flg=0x10440000 cmp=com.sony.dtv.tvx/.MainActivity (has extras) }
              mLaunchSingleTop=false mLaunchSingleInstance=true mLaunchSingleTask=false mLaunchFlags=0x10040000 mDoResume=true mAddingToTask=false
        """
        hdmi_input = self._hdmi_input(dumpsys_output)

        self.assertEqual(hdmi_input, "HW2")

    def test_hdmi_input_sony_netflix(self):
        dumpsys_output = """
            ACTIVITY MANAGER ACTIVITIES (dumpsys activity starter)
            ActivityStarter:
              mCurrentUser=0
              mLastStartReason=startActivityAsUser
              mLastStartActivityTimeMs=6 Feb 2021 22:34:59
              mLastStartActivityResult=2
              mLastStartActivityRecord:
               packageName=com.netflix.ninja processName=com.netflix.ninja
               launchedFromUid=10162 launchedFromPackage=com.google.android.tvlauncher userId=0
               app=ProcessRecord{8005dce 16003:com.netflix.ninja/u0a143}
               Intent { act=android.intent.action.VIEW dat=http://www.netflix.com/home flg=0x10000020 pkg=com.netflix.ninja cmp=com.netflix.ninja/.MainActivity bnds=[140,476][300,636] (has extras) }
               frontOfTask=true task=TaskRecord{5c24cd8 #2727 A=com.netflix.ninja U=0 StackId=1 sz=1}
               taskAffinity=com.netflix.ninja
               realActivity=com.netflix.ninja/.MainActivity
               baseDir=/data/app/com.netflix.ninja-BRRRO8oABNAvcXQxHb4oBA==/base.apk
               dataDir=/data/user/0/com.netflix.ninja
               stateNotNeeded=false componentSpecified=true mActivityType=0
               compat={320dpi always-compat} labelRes=0x7f0e001c icon=0x7f070175 theme=0x7f0f0139
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               taskDescription: iconFilename=null label="null" primaryColor=ff000000
                backgroundColor=ff000000
                statusBarColor=ff000000
                navigationBarColor=ff000000
               launchFailed=false launchCount=0 lastLaunchTime=-1d2h24m34s18ms
               haveState=false icicle=null
               state=RESUMED stopped=false delayedResume=false finishing=false
               keysPaused=false inHistory=true visible=true sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_REMOVED
               fullscreen=true noDisplay=false immersive=false launchMode=2
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=APPLICATION_ACTIVITY_TYPE
               waitingVisible=false nowVisible=true lastVisibleTime=-25s492ms
               connections=[ConnectionRecord{64e94 u0 CR com.netflix.ninja/.NetflixService:@a0a82e7}, ConnectionRecord{91d022a u0 com.google.android.apps.mediashell/.MediaShellCastReceiverService:@2400f15}]
               resizeMode=RESIZE_MODE_UNRESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
              mLastHomeActivityStartResult=0
              mLastHomeActivityStartRecord:
               packageName=com.google.android.tvlauncher processName=com.google.android.tvlauncher
               launchedFromUid=0 launchedFromPackage=null userId=0
               app=ProcessRecord{8d5fa46 22638:com.google.android.tvlauncher/u0a162}
               Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10800100 cmp=com.google.android.tvlauncher/.MainActivity }
               frontOfTask=true task=TaskRecord{1142677 #2719 A=.TvLauncher U=0 StackId=0 sz=1}
               taskAffinity=.TvLauncher
               realActivity=com.google.android.tvlauncher/.MainActivity
               baseDir=/data/app/com.google.android.tvlauncher-yGwF-XP6Zf5hV0DbQ9Z4gA==/base.apk
               dataDir=/data/user/0/com.google.android.tvlauncher
               stateNotNeeded=true componentSpecified=false mActivityType=1
               compat={320dpi always-compat} labelRes=0x7f12002b icon=0x7f0f0000 theme=0x7f130007
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               taskDescription: iconFilename=null label="null" primaryColor=ff37474f
                backgroundColor=ff303030
                statusBarColor=ff263238
                navigationBarColor=ff000000
               launchFailed=false launchCount=0 lastLaunchTime=-4m48s633ms
               haveState=true icicle=Bundle[mParcelledData.dataSize=1216]
               state=STOPPED stopped=true delayedResume=false finishing=false
               keysPaused=false inHistory=true visible=false sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_REMOVED
               fullscreen=true noDisplay=false immersive=false launchMode=2
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=HOME_ACTIVITY_TYPE
               waitingVisible=false nowVisible=false lastVisibleTime=-4m46s108ms
               resizeMode=RESIZE_MODE_UNRESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
              mStartActivity:
               packageName=com.netflix.ninja processName=com.netflix.ninja
               launchedFromUid=10143 launchedFromPackage=com.netflix.ninja userId=0
               app=null
               Intent { flg=0x10420000 cmp=com.netflix.ninja/.MainActivity (has extras) }
               frontOfTask=false task=TaskRecord{5c24cd8 #2727 A=com.netflix.ninja U=0 StackId=1 sz=1}
               taskAffinity=com.netflix.ninja
               realActivity=com.netflix.ninja/.MainActivity
               baseDir=/data/app/com.netflix.ninja-BRRRO8oABNAvcXQxHb4oBA==/base.apk
               dataDir=/data/user/0/com.netflix.ninja
               stateNotNeeded=false componentSpecified=true mActivityType=0
               compat=null labelRes=0x7f0e001c icon=0x7f070175 theme=0x7f0f0139
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/?}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               launchFailed=false launchCount=0 lastLaunchTime=0
               haveState=true icicle=null
               state=INITIALIZING stopped=false delayedResume=false finishing=false
               keysPaused=false inHistory=false visible=false sleeping=false idle=false mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
               fullscreen=true noDisplay=false immersive=false launchMode=2
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=APPLICATION_ACTIVITY_TYPE
               resizeMode=RESIZE_MODE_UNRESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
              mIntent=Intent { flg=0x10420000 cmp=com.netflix.ninja/.MainActivity (has extras) }
              mLaunchSingleTop=false mLaunchSingleInstance=false mLaunchSingleTask=true mLaunchFlags=0x10020000 mDoResume=true mAddingToTask=false
        """
        hdmi_input = self._hdmi_input(dumpsys_output)

        self.assertEqual(hdmi_input, "")

    def test_hdmi_input_sony_non_hardware_definition(self):
        dumpsys_output = """
            ACTIVITY MANAGER ACTIVITIES (dumpsys activity starter)
            ActivityStarter:
              mCurrentUser=0
              mLastStartReason=startActivityAsUser
              mLastStartActivityTimeMs=6 Feb 2021 22:30:46
              mLastStartActivityResult=2
              mLastStartActivityRecord:
               packageName=com.sony.dtv.tvx processName=com.sony.dtv.tvx
               launchedFromUid=10134 launchedFromPackage=com.sony.dtv.tvx userId=0
               app=ProcessRecord{edc6562 3904:com.sony.dtv.tvx/u0a134}
               Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.sony.dtv.tvinput.external%2F.ExternalTvInputService%2FHW2 flg=0x10040000 cmp=com.sony.dtv.tvx/.MainActivity (has extras) }
               frontOfTask=true task=TaskRecord{9eecc8c #2830 A=com.sony.dtv.tvx U=0 StackId=1 sz=1}
               taskAffinity=com.sony.dtv.tvx
               realActivity=com.sony.dtv.tvx/.MainActivity
               baseDir=/system/priv-app/Tvx/Tvx.apk
               dataDir=/data/user/0/com.sony.dtv.tvx
               stateNotNeeded=false componentSpecified=false mActivityType=0
               compat={320dpi always-compat} labelRes=0x7f090048 icon=0x7f02006d theme=0x7f0b01c2
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               taskDescription: iconFilename=null label="null" primaryColor=ff8c0000
                backgroundColor=ff303030
                statusBarColor=ff000000
                navigationBarColor=ff000000
               launchFailed=false launchCount=0 lastLaunchTime=-2d11h49m7s584ms
               haveState=false icicle=null
               state=RESUMED stopped=false delayedResume=false finishing=false
               keysPaused=false inHistory=true visible=true sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_REMOVED
               fullscreen=true noDisplay=false immersive=false launchMode=3
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=APPLICATION_ACTIVITY_TYPE
               waitingVisible=false nowVisible=true lastVisibleTime=-2m50s467ms
               connections=[ConnectionRecord{fee4c3e u0 CR com.sony.dtv.osdplanevisibilitymanager/.OsdEnabler:@246a4f9}]
               resizeMode=RESIZE_MODE_RESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
               supportsPictureInPicture=true
               supportsPictureInPictureWhilePausing: true
              mLastHomeActivityStartResult=0
              mLastHomeActivityStartRecord:
               packageName=com.google.android.tvlauncher processName=com.google.android.tvlauncher
               launchedFromUid=0 launchedFromPackage=null userId=0
               app=ProcessRecord{8d5fa46 22638:com.google.android.tvlauncher/u0a162}
               Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10800100 cmp=com.google.android.tvlauncher/.MainActivity }
               frontOfTask=true task=TaskRecord{1142677 #2719 A=.TvLauncher U=0 StackId=0 sz=1}
               taskAffinity=.TvLauncher
               realActivity=com.google.android.tvlauncher/.MainActivity
               baseDir=/data/app/com.google.android.tvlauncher-yGwF-XP6Zf5hV0DbQ9Z4gA==/base.apk
               dataDir=/data/user/0/com.google.android.tvlauncher
               stateNotNeeded=true componentSpecified=false mActivityType=1
               compat={320dpi always-compat} labelRes=0x7f12002b icon=0x7f0f0000 theme=0x7f130007
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               taskDescription: iconFilename=null label="null" primaryColor=ff37474f
                backgroundColor=ff303030
                statusBarColor=ff263238
                navigationBarColor=ff000000
               launchFailed=false launchCount=0 lastLaunchTime=-3m0s967ms
               haveState=true icicle=Bundle[mParcelledData.dataSize=1216]
               state=STOPPED stopped=true delayedResume=false finishing=false
               keysPaused=false inHistory=true visible=false sleeping=false idle=true mStartingWindowState=STARTING_WINDOW_SHOWN
               fullscreen=true noDisplay=false immersive=false launchMode=2
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=HOME_ACTIVITY_TYPE
               waitingVisible=false nowVisible=false lastVisibleTime=-2m58s442ms
               resizeMode=RESIZE_MODE_UNRESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
              mStartActivity:
               packageName=com.sony.dtv.tvx processName=com.sony.dtv.tvx
               launchedFromUid=10134 launchedFromPackage=com.sony.dtv.tvx userId=0
               app=null
               Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.sony.dtv.tvinput.external%2F.ExternalTvInputService%2FHDMI100004 flg=0x10400000 cmp=com.sony.dtv.tvx/.MainActivity (has extras) }
               frontOfTask=false task=TaskRecord{9eecc8c #2830 A=com.sony.dtv.tvx U=0 StackId=1 sz=1}
               taskAffinity=com.sony.dtv.tvx
               realActivity=com.sony.dtv.tvx/.MainActivity
               baseDir=/system/priv-app/Tvx/Tvx.apk
               dataDir=/data/user/0/com.sony.dtv.tvx
               stateNotNeeded=false componentSpecified=false mActivityType=0
               compat=null labelRes=0x7f090048 icon=0x7f02006d theme=0x7f0b01c2
               mLastReportedConfigurations:
                mGlobalConfig={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
                mOverrideConfig={0.0 ?mcc?mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/?}
               CurrentConfiguration={1.0 ?mcc?mnc [en_GB] ldltr sw540dp w960dp h540dp 320dpi lrg long hdr land television -touch -keyb/v/h dpad/v appBounds=Rect(0, 0 - 1920, 1080) s.3}
               launchFailed=false launchCount=0 lastLaunchTime=0
               haveState=true icicle=null
               state=INITIALIZING stopped=false delayedResume=false finishing=false
               keysPaused=false inHistory=false visible=false sleeping=false idle=false mStartingWindowState=STARTING_WINDOW_NOT_SHOWN
               fullscreen=true noDisplay=false immersive=false launchMode=3
               frozenBeforeDestroy=false forceNewConfig=false
               mActivityType=APPLICATION_ACTIVITY_TYPE
               resizeMode=RESIZE_MODE_RESIZEABLE
               mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
               supportsPictureInPicture=true
               supportsPictureInPictureWhilePausing: false
              mIntent=Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.sony.dtv.tvinput.external/.ExternalTvInputService/HDMI100004 flg=0x10400000 cmp=com.sony.dtv.tvx/.MainActivity (has extras) }
              mLaunchSingleTop=false mLaunchSingleInstance=true mLaunchSingleTask=false mLaunchFlags=0x10000000 mDoResume=true mAddingToTask=false
        """
        hdmi_input = self._hdmi_input(dumpsys_output)

        self.assertEqual(hdmi_input, "")

    def test_apps_alphabetized(self):
        constants_str = inspect.getsource(constants)
        last_app = ""
        for line in constants_str.splitlines():
            if line.startswith("APP_"):
                app = line.split()[0]
                self.assertEqual(app, app.upper())
                self.assertEqual(sorted([last_app, app])[0], last_app)
                last_app = app

        apps_dict_lines = []
        for line in constants_str.splitlines():
            if line.startswith("APPS = {"):
                apps_dict_lines.append(line[len("APPS = {") :].strip())
            elif apps_dict_lines:
                apps_dict_lines.append(line.strip())
                if line.strip().endswith("}"):
                    break

        apps_dict_lines_sorted = sorted(apps_dict_lines)
        self.assertListEqual(apps_dict_lines, apps_dict_lines_sorted)


if __name__ == "__main__":
    unittest.main()
