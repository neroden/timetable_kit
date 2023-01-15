# runtime_config.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
This file exists to hold data which is set at runtime, but is the same across a single run of
timetable.py.  This data needs to be shared by multiple modules so it needs to be "low-level".

This data includes the critical choice of which agency's subpackage to use.
"""

from timetable_kit.debug import debug_print

# The agencies we might need to import
import timetable_kit.amtrak
import timetable_kit.via

# These will get set elsewhere, later, by initialization code.
agency_name = None
agency_package = None


def set_agency(agency: str):
    """
    Set the agency subpackage to use to get agency-specific data (e.g. generic, amtrak, via).

    Called by initialization code
    """

    global agency_name
    global agency_package

    match agency:
        case "generic":
            print("Unimplemented")
            sys.exit(1)
        case "amtrak":
            debug_print(1, "Using Amtrak data")
            agency_name = "Amtrak"
            agency_package = timetable_kit.amtrak
        case "hartford":
            print("Unimplemented")
            sys.exit(1)
        case "via":
            debug_print(1, "Using VIA Rail data")
            agency_name = "VIA Rail"
            agency_package = timetable_kit.via
            sys.exit(1)
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
