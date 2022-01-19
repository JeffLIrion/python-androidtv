"""Helper script for generating the 'test_constants' test in test_constants.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from androidtv import constants

EXCLUSIONS = {
    "CMD_SUCCESS1",
    "CMD_SUCCESS1_FAILURE0",
    "CMD_PARSE_CURRENT_APP",
    "CMD_DEFINE_CURRENT_APP_VARIABLE",
    "CMD_DEFINE_CURRENT_APP_VARIABLE_GOOGLE_TV",
    "CMD_LAUNCH_APP_CONDITION",
}


if __name__ == "__main__":
    for var in sorted(dir(constants)):
        if var.startswith("CMD_") and var not in EXCLUSIONS:
            print("        # {}".format(var))
            print('        self.assertEqual(constants.{}, r"{}")'.format(var, getattr(constants, var)))
            print()
