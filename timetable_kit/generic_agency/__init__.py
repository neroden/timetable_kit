# generic_agency/__init__.py
# Init file for generic agency subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.generic_agency subpackage.

Functions for a generic agency.
"""


# The Agency class type, for others to inherit from
from .agency import Agency, AgencySingletonGetter

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton
from ..errors import InputError


# Object explaining where to find the GTFS & which can also download it
# This is a dummy for generic_agency
def get_gtfs_files():
    """Retrieve the AgencyGTFSFiles object for the agency

    For generic_agency, throws an error since this can't be done.
    """
    raise InputError(
        "Generic agency doesn't have default GTFS -- specify GTFS at command line"
    )
