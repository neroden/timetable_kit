# runtime_config.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
This file exists to hold data which is set at runtime, but is the same across a single run of
timetable.py.  This data needs to be shared by multiple modules so it needs to be "low-level".

This data includes the critical choice of which agency's subpackage to use.
"""

from timetable_kit.debug import debug_print

# For sys.exit
import sys

# The agencies we might need to import
import timetable_kit.amtrak
import timetable_kit.via
import timetable_kit.hartford_line

# These will get set elsewhere, later, by initialization code.
agency_name = None
agency_package = None
agency_input_dir = None

def set_agency(agency: str):
    """
    Set the agency subpackage to use to get agency-specific data (e.g. generic, amtrak, via).

    Called by initialization code
    """

    global agency_name
    global agency_package
    global agency_input_dir

    match agency:
        case "generic":
            print("Unimplemented")
            sys.exit(1)
        case "amtrak":
            debug_print(1, "Using Amtrak data")
            agency_name = "Amtrak"
            agency_package = timetable_kit.amtrak
            agency_input_dir = "specs_amtrak"
        case "hartford":
            debug_print(1, "Using Hartford Line data with Amtrak data")
            agency_name = "Hartford Line"
            agency_package = timetable_kit.hartford_line
            agency_input_dir = "specs_hartford"
        case "via":
            debug_print(1, "Using VIA Rail data")
            agency_name = "VIA Rail"
            agency_package = timetable_kit.via
            agency_input_dir = "specs_via"
        case _:
            print("Invalid agency subpackage choice")
            sys.exit(1)


def agency():
    """
    Get the agency subpackage to use to get agency-specific data (e.g. generic, amtrak, via).
    """
    global agency_name
    global agency_package

    debug_print(3, "Retrieving agency_package", agency_package)
    return agency_package
