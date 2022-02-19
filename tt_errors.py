# tt_errors.py
# Part of timetable_kit
# Copyright 2021 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

class GTFSError(ValueError):
    """Exception for unexpected data in the GTFS feed."""
    pass

class NoStopError(GTFSError):
    """Exception when a train doesn't stop at a station.  Frequently caught."""

class TwoStopsError(GTFSError):
    """Exception when a train stops at a station twice.  Frequently caught."""

class InputError(ValueError):
    """Exception for unexpected data passed in by the user."""
    pass
