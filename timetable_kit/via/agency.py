# via/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.via.agency module

This holds a class for "AgencyVIA" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.feed_enhanced import FeedEnhanced
from timetable_kit.generic_agency import Agency
import timetable_kit.via.gtfs_patches as gtfs_patches  # for patch_feed


class AgencyVIA(Agency):
    """VIA-specific code for interpreting specs and GTFS feeds"""

    def __init__(
        self: AgencyVIA,
    ) -> None:
        super().__init__()

    def patch_feed(self, feed: FeedEnhanced) -> FeedEnhanced:
        """
        Apply VIA-specific patches to a feed.
        Returns the patched feed.
        Does not alter data in the Agency object.
        """
        # This is defined in its own file in the VIA subpackage.
        return gtfs_patches.patch_feed(feed)


# Establish the singleton
_singleton = AgencyVIA()


def get_singleton():
    """Get singleton for VIA"""
    global _singleton
    return _singleton
