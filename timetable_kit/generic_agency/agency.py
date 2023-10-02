# generic_agency/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.generic_agency.agency module

This holds a class for "Agency" intended to be used as a singleton.
It has an interface; Amtrak and others need to provide the same interface.
This should be made easier by class inheritance.
"""
from __future__ import annotations

# Intended to be used both directly and by subclasses
class Agency:
    """Agency-specific code for interpreting specs and GTFS feeds for a generic agency"""

    def __init__(
        self: Agency,
    ) -> None:
        pass

# Establish the singleton
_singleton = Agency()

def get_singleton():
    """Get singleton for generic agency"""
    global _singleton
    return _singleton
