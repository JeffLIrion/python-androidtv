import os
import sys
import unittest

sys.path.insert(0, '..')

from androidtv import constants


class TestConstants(unittest.TestCase):
    @staticmethod
    def _exec(command):
        process = os.popen(command)
        output = process.read().strip()
        process.close()
        return output

    @staticmethod
    def _extract_current_app(dumpsys_output):
        return TestConstants._exec('CURRENT_APP="' + dumpsys_output + '" && ' + constants.VAR_CURRENT_APP_EXTRACTION + ' && echo $CURRENT_APP')

    @staticmethod
    def _hdmi_input(dumpsys_output):
        return TestConstants._exec(constants.CMD_HDMI_INPUT.replace('dumpsys activity starter', 'echo "' + dumpsys_output + '"'))

    def test_apps(self):
        """Test that the values (i.e., app names) in the ``APPS`` dict are unique.
        """
        apps_reversed = {val: key for key, val in constants.APPS.items()}
        self.assertEqual(len(constants.APPS), len(apps_reversed))

    def test_constants(self):
        """Test ADB shell commands.

        This is basically a form of version control for constants.

        """
        self.maxDiff = None

        self.assertEqual(constants.CMD_CURRENT_APP, "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP")

        self.assertEqual(constants.CMD_CURRENT_APP_GOOGLE_TV, "CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP")

        self.assertEqual(constants.CMD_LAUNCH_APP, "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${{CURRENT_APP#*{{* * }} && CURRENT_APP=${{CURRENT_APP%%/*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LAUNCHER --pct-syskeys 0 1; fi")

        self.assertEqual(constants.CMD_LAUNCH_APP_GOOGLE_TV, "CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${{CURRENT_APP%%/*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LAUNCHER --pct-syskeys 0 1; fi")

        self.assertEqual(constants.CMD_MEDIA_SESSION_STATE_FULL, "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'")

        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && ps | grep u0_a")

        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo)")

        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && ps | grep u0_a")

        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo)")

    def test_current_app_extraction_atv_launcher(self):
        dumpsys_output = """
            mCurrentFocus=Window{e74bb23 u0 com.google.android.tvlauncher/com.google.android.tvlauncher.MainActivity}
            mFocusedApp=AppWindowToken{c791eb8 token=Token{a6bad1b ActivityRecord{35dbb2a u0 com.google.android.tvlauncher/.MainActivity t2719}}}
        """
        current_app = self._extract_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_ATV_LAUNCHER)

    def test_current_app_extraction_atv_launcher_google_tv(self):
        dumpsys_output = """
            mResumedActivity: ActivityRecord{35dbb2a u0 com.google.android.tvlauncher/.MainActivity t2719}
        """
        current_app = self._extract_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_ATV_LAUNCHER)

    def test_current_app_extraction_sony_picture_off(self):
        dumpsys_output = """
            mCurrentFocus=Window{c52eaa8 u0 com.sony.dtv.sonysystemservice}
            mFocusedApp=AppWindowToken{11da138 token=Token{19ea99b ActivityRecord{c4d9aa u0 tunein.player/tunein.ui.leanback.ui.activities.TvHomeActivity t2424}}}
        """
        current_app = self._extract_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_TUNEIN)

    def test_current_app_extraction_intent_with_no_activity(self):
        dumpsys_output = """
            mCurrentFocus=Window{c52eaa8 u0 com.sony.dtv.sonysystemservice}
        """
        current_app = self._extract_current_app(dumpsys_output)

        self.assertEqual(current_app, 'com.sony.dtv.sonysystemservice')

    def test_current_app_extraction_with_identifier_as_output(self):
        dumpsys_output = constants.APP_NETFLIX
        current_app = self._extract_current_app(dumpsys_output)

        self.assertEqual(current_app, constants.APP_NETFLIX)

    def test_hdmi_input(self):
        dumpsys_output = """
             Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.mediatek.tvinput%2F.hdmi.HDMIInputService%2FHW5 flg=0x10000000 cmp=org.droidtv.playtv/.PlayTvActivity (has extras) }
            mIntent=Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.mediatek.tvinput/.hdmi.HDMIInputService/HW5 flg=0x10000000 cmp=org.droidtv.playtv/.PlayTvActivity (has extras) }
        """
        hdmi_input = self._hdmi_input(dumpsys_output)

        self.assertEqual(hdmi_input, 'HW5')

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

        self.assertEqual(hdmi_input, 'HW2')

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

        self.assertEqual(hdmi_input, '')

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

        self.assertEqual(hdmi_input, '')


if __name__ == "__main__":
    unittest.main()
