# maple_leaf/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.maple_leaf.agency module

This holds a class for "AgencyMapleLeaf" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.generic_agency import Agency


class AgencyMapleLeaf(Agency):
    """Maple Leaf-specific code for interpreting specs and GTFS feeds"""

    def __init__(
        self: AgencyMapleLeaf,
    ) -> None:
        super().__init__()


# Establish the singleton
_singleton = AgencyMapleLeaf()


def get_singleton():
    """Get singleton for Maple Leaf"""
    global _singleton
    return _singleton
