# hartford_line/__init.py__
# Init file for hartford_line subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.hartford_line module

Hartford-line-specific functions for timetable_kit.

This defines an interface; each agency needs to provide the same interface
"""

# Where to find the GTFS (merged GTFS)
from .merge_gtfs import (
    gtfs_unzipped_local_path,
)

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# Most of the rest of this should be copied from Amtrak

# How to title the routes at the top of the column
from timetable_kit.amtrak.route_names import get_route_name

# For making the key for connecting services (including only those in this timetable)
# This takes a list of stations as an argument
from .connecting_services_data import get_all_connecting_services
