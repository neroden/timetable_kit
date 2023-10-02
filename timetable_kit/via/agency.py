# via/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.via.agency module

This holds a class for "AgencyVIA" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.generic_agency import Agency


class AgencyVIA(Agency):
    """VIA-specific code for interpreting specs and GTFS feeds"""

    def __init__(
        self: AgencyVIA,
    ) -> None:
        super().__init__()


# Establish the singleton
_singleton = AgencyVIA()

def get_singleton():
    """Get singleton for VIA"""
    global _singleton
    return _singleton
