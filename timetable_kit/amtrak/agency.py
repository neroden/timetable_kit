# amtrak/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.amtrak.agency module

This holds a class for "AgencyAmtrak" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.generic_agency import Agency


class AgencyAmtrak(Agency):
    """Amtrak-specific code for interpreting specs and GTFS feeds"""

    def __init__(
        self: AgencyAmtrak,
    ) -> None:
        super().__init__()


# Establish the singleton
_singleton = AgencyAmtrak()


def get_singleton():
    """Get singleton for Amtrak"""
    global _singleton
    return _singleton
