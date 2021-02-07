import sys
import unittest

sys.path.insert(0, '..')

from androidtv import constants


class TestConstants(unittest.TestCase):
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

        # CMD_CURRENT_APP
        self.assertEqual(constants.CMD_CURRENT_APP, "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP")

        # CMD_CURRENT_APP_GOOGLE_TV
        self.assertEqual(constants.CMD_CURRENT_APP_GOOGLE_TV, "CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP")

        # CMD_LAUNCH_APP
        self.assertEqual(constants.CMD_LAUNCH_APP, "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${{CURRENT_APP#*{{* * }} && CURRENT_APP=${{CURRENT_APP%%/*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LAUNCHER --pct-syskeys 0 1; fi")

        # CMD_LAUNCH_APP_GOOGLE_TV
        self.assertEqual(constants.CMD_LAUNCH_APP_GOOGLE_TV, "CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${{CURRENT_APP%%/*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c android.intent.category.LAUNCHER --pct-syskeys 0 1; fi")

        # CMD_MEDIA_SESSION_STATE_FULL
        self.assertEqual(constants.CMD_MEDIA_SESSION_STATE_FULL, "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'")

        # CMD_ANDROIDTV_PROPERTIES_LAZY_RUNNING_APPS
        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        # CMD_ANDROIDTV_PROPERTIES_LAZY_NO_RUNNING_APPS
        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        # CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_RUNNING_APPS
        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        # CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS
        self.assertEqual(constants.CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        # CMD_GOOGLE_TV_PROPERTIES_LAZY_RUNNING_APPS
        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        # CMD_GOOGLE_TV_PROPERTIES_LAZY_NO_RUNNING_APPS
        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        # CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_RUNNING_APPS
        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11 && ps -A | grep u0_a")

        # CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS
        self.assertEqual(constants.CMD_GOOGLE_TV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && (dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')) && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys activity a . | grep -E 'mResumedActivity' | cut -d ' ' -f 8) && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && dumpsys audio | grep '\- STREAM_MUSIC:' -A 11")

        # CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS
        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && ps | grep u0_a")

        # CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS
        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo)")

        # CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS
        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo) && ps | grep u0_a")

        # CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS
        self.assertEqual(constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS, "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true') && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep mWakefulness | grep -q Awake && echo -e '1\c' || echo -e '0\c' && dumpsys power | grep Locks | grep 'size=' && CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP && (dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {' || echo) && (dumpsys activity starter | grep -o 'HDMIInputService\/HW[0-9]' -m 1 | grep -o 'HW[0-9]' || echo)")


if __name__ == "__main__":
    unittest.main()
