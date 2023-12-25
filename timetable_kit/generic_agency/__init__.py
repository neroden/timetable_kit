# generic_agency/__init__.py
# Init file for generic agency subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.generic_agency subpackage.

Functions for a generic agency.
"""


# The Agency class type, for others to inherit from
from .agency import Agency

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# These may require special handling
gtfs_zip_local_path = None
gtfs_unzipped_local_path = None
