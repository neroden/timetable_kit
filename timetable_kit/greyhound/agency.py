# greyhound/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.greyhound.agency module

This holds a class for "AgencyGreyhound" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.feed_enhanced import FeedEnhanced
from timetable_kit.generic_agency import Agency

# for patch_feed
import timetable_kit.greyhound.gtfs_patches as gtfs_patches


class AgencyGreyhound(Agency):
    """Greyhound-specific code for interpreting specs and GTFS feeds"""

    _agency_names = ["Greyhound"]  # Also FlixBus?
    _agency_websites = ["Greyhound.com"]
    _agency_published_gtfs_urls = ["https://www.transit.land/feeds/f-9-flixbus"]

    def __init__(
        self: AgencyGreyhound,
    ) -> None:
        super().__init__()
        # No connecting service data yet
        # Initialized from connecting_services_data.py
        # self._connecting_services_dict = connecting_services_dict

    def patch_feed(self, feed: FeedEnhanced) -> FeedEnhanced:
        """
        Apply Greyhound-specific patches to a feed.
        Returns the patched feed.
        Does not alter data in the Agency object.
        """
        return gtfs_patches.patch_feed(feed)


# Establish the singleton
_singleton = AgencyGreyhound()


def get_singleton():
    """Get singleton for Greyhound"""
    global _singleton
    return _singleton
