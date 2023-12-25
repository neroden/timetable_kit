# convenience_types.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Types used for extra type-checking."""

# Do this after working our way through the codebase to fix all calls
# from typing import NewType

# Do this for now
from typing import TypeAlias

# This must be a date in YYYYMMDD format
# type GTFSDate = NewType("GTFSDate", str)
GTFSDate: TypeAlias = str

# This must be one of the GTFS_DAYS listed in feed_enhanced.py
# type GTFSDay = NewType("GTFSDay", str)
GTFSDay: TypeAlias = str
