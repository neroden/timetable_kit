# amtrak/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.amtrak.agency module

This holds a class for "AgencyAmtrak" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.generic_agency import Agency
import timetable_kit.amtrak.gtfs_patches as gtfs_patches  # for patch_feed
import timetable_kit.amtrak.access as access  # for patch_add_wheelchair_boarding


class AgencyAmtrak(Agency):
    """Amtrak-specific code for interpreting specs and GTFS feeds"""

    def __init__(
        self: AgencyAmtrak,
    ) -> None:
        super().__init__()

    def stop_code_to_stop_id(self, stop_code: str) -> str:
        # Identity function for Amtrak
        return stop_code

    def stop_id_to_stop_code(self, stop_id: str) -> str:
        # Identity function for Amtrak
        return stop_id

    def patch_feed(self, feed: FeedEnhanced) -> FeedEnhanced:
        """
        Apply Amtrak-specific patches to a feed.
        Returns the patched feed.
        Does not alter data in the Agency object.
        Do this before init_from_feed.
        """
        # This is defined in its own file in the Amtrak subpackage.
        return gtfs_patches.patch_feed(feed)

    def patch_feed_wheelchair_access_only(self, feed: FeedEnhanced) -> FeedEnhanced:
        """
        Apply only the patches to add wheelchair boarding information for Amtrak;
        return a patched feed.

        Does not alter the data in the agency object.
        Do this before init_from_feed.
        """
        new_feed = feed.copy()
        access.patch_add_wheelchair_boarding(new_feed)  # Alters in place
        return new_feed

    def unofficial_disclaimer() -> str:
        """Returns a string for a disclaimer about this not being an official product"""
        return "This timetable is not an official Amtrak product."


# Establish the singleton
_singleton = AgencyAmtrak()


def get_singleton():
    """Get singleton for Amtrak"""
    global _singleton
    return _singleton
