# hartford_line/__init.py__
# Init file for hartford_line subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.hartford_line module.

Hartford-line-specific functions for timetable_kit.

This defines an interface; each agency needs to provide the same interface
"""

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# Function returning AgencyGTFSFiles object
# which explains where to find the GTFS & which can also download it
from .get_gtfs import get_gtfs_files
