# tt_errors.py
# Part of timetable_kit
# Copyright 2021 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

class GTFSError(ValueError):
    """Exception for unexpected data in the GTFS feed."""
    pass
