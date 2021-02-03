import os
import sys
import unittest

sys.path.insert(0, '..')

from androidtv import constants


class TestConstants(unittest.TestCase):
    @staticmethod
    def _extract_current_app(dumpsys_output):
        process = os.popen('CURRENT_APP="' + dumpsys_output + '" && ' + constants.VAR_CURRENT_APP_EXTRACTION + ' && echo $CURRENT_APP')
        current_app = process.read().strip()
        process.close()
        return current_app

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


if __name__ == "__main__":
    unittest.main()
