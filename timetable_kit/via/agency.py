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

# for patch_feed
import timetable_kit.via.gtfs_patches as gtfs_patches

# For checked baggage, sleeper trains
import timetable_kit.via.special_data as special_data


class AgencyVIA(Agency):
    """VIA-specific code for interpreting specs and GTFS feeds"""

    _agency_names = ["VIA Rail"]
    _agency_published_gtfs_urls = [
        "https://www.transit.land/feeds/f-f-viarail~traindecharlevoix"
    ]

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

    def station_has_checked_baggage(self, station_code: str) -> bool:
        """
        Does this station have checked baggage service?
        """
        return special_data.station_has_checked_baggage(station_code)

    def train_has_checked_baggage(self, tsn: str) -> bool:
        """
        Does this train have checked baggage service?
        """
        return special_data.train_has_checked_baggage(tsn)

    def is_sleeper_train(self, tsn: str) -> bool:
        """
        Does this train have sleeper cars?
        """
        return special_data.is_sleeper_train(tsn)


# Establish the singleton
_singleton = AgencyVIA()


def get_singleton():
    """Get singleton for VIA"""
    global _singleton
    return _singleton
