# hartford_line/__init.py__
# Init file for hartford_line subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.hartford_line module

Hartford-line-specific functions for timetable_kit.

This defines an interface; each agency needs to provide the same interface
"""

# Where to find the GTFS (merged GTFS)
from .merge_gtfs import gtfs_unzipped_local_path

# Where to find the GTFS (raw gtfs) (used by merge_gtfs)
import timetable_kit.hartford_line.get_gtfs as get_gtfs

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton
