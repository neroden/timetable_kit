# greyhound/__init__.py
# Init file for greyhound subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.greyhound subpackage."""

# The class for inheritance
from .agency import AgencyGreyhound

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# Function returning AgencyGTFSFiles object
# which explains where to find the GTFS & which can also download it
from .get_gtfs import get_gtfs_files
