"""Helper script for generating the 'test_constants' test in test_constants.py."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from androidtv import constants

EXCLUSIONS = {
    "CMD_SUCCESS1",
    "CMD_SUCCESS1_FAILURE0",
    "CMD_PARSE_CURRENT_APP",
    "CMD_PARSE_CURRENT_APP11",
    "CMD_DEFINE_CURRENT_APP_VARIABLE",
    "CMD_DEFINE_CURRENT_APP_VARIABLE11",
    "CMD_DEFINE_CURRENT_APP_VARIABLE_GOOGLE_TV",
    "CMD_LAUNCH_APP_CONDITION",
    "CMD_LAUNCH_APP_CONDITION_FIRETV",
}


def get_cmds():
    """Get the ``CMD_*`` constants.

    Returns
    -------
    dict[str: str]
        A dictionary where the keys are the names of the constants and the keys are their values

    """
    return {var: getattr(constants, var) for var in dir(constants) if var.startswith("CMD_") and var not in EXCLUSIONS}


if __name__ == "__main__":
    for name, value in sorted(get_cmds().items(), key=lambda x: x[0]):
        print("        # {}".format(name))
        print('        self.assertCommand(constants.{}, r"{}")'.format(name, value))
        print()
