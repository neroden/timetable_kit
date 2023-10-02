# hartford_line/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.maple_leaf.agency module

This holds a class for "AgencyHartfordLine" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.generic_agency import Agency


class AgencyHartfordLine(Agency):
    """Hartford Line-specific code for interpreting specs and GTFS feeds"""

    def __init__(
        self: AgencyHartfordLine,
    ) -> None:
        super().__init__()


# Establish the singleton
_singleton = AgencyHartfordLine()


def get_singleton():
    """Get singleton for Hartford Line"""
    global _singleton
    return _singleton
