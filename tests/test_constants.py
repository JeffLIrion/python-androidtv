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
