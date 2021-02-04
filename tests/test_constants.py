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
    def _search_hdmi_input(dumpsys_output):
        return TestConstants._exec('echo "' + dumpsys_output + '"' + constants.CMD_HDMI_INPUT_SEARCH)

    def test_apps(self):
        """Test that the values (i.e., app names) in the ``APPS`` dict are unique.
        """
        apps_reversed = {val: key for key, val in constants.APPS.items()}
        self.assertEqual(len(constants.APPS), len(apps_reversed))

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

    def test_hdmi_input_search(self):
        dumpsys_output = """
             Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.mediatek.tvinput%2F.hdmi.HDMIInputService%2FHW5 flg=0x10000000 cmp=org.droidtv.playtv/.PlayTvActivity (has extras) }
            mIntent=Intent { act=android.intent.action.VIEW dat=content://android.media.tv/passthrough/com.mediatek.tvinput/.hdmi.HDMIInputService/HW5 flg=0x10000000 cmp=org.droidtv.playtv/.PlayTvActivity (has extras) }
        """
        hdmi_input = self._search_hdmi_input(dumpsys_output)

        self.assertEqual(hdmi_input, 'HW5')

    def test_hdmi_input_search_sony(self):
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
        hdmi_input = self._search_hdmi_input(dumpsys_output)

        self.assertEqual(hdmi_input, 'HW2')


if __name__ == "__main__":
    unittest.main()
