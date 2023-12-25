# via/__init.py__
# Init file for via subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.via module.

VIA-specific functions for timetable_kit.

This defines an interface; Amtrak and others need to provide the same interface.
"""

# The class for inheritance
from .agency import AgencyVIA

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# Where to find the GTFS
from .get_gtfs import (
    gtfs_unzipped_local_path,
)
