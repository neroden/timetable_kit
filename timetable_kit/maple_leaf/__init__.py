# maple_leaf/__init.py__
# Init file for maple_leaf subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.maple_leaf module.

Maple Leaf specific functions for timetable_kit.

This defines an interface; each agency needs to provide the same interface
"""

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# Function returning AgencyGTFSFiles object
# which explains where to find the GTFS & which can also download it
from .get_gtfs import get_gtfs_files
