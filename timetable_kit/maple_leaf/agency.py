# maple_leaf/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.maple_leaf.agency module

This holds a class for "AgencyMapleLeaf" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.amtrak import AgencyAmtrak
from timetable_kit.via import AgencyVIA

# For get_station_name_pretty, our version
import timetable_kit.maple_leaf.station_names as station_names


# This should mostly be based on Amtrak.
# The inheritance from VIA is to grab the VIA disclaimer.
class AgencyMapleLeaf(AgencyAmtrak, AgencyVIA):
    """Maple Leaf-specific code for interpreting specs and GTFS feeds"""

    _agency_names = ["Amtrak", "VIA Rail"]
    _agency_websites = [
        AgencyAmtrak._agency_websites[0],
        AgencyVIA._agency_websites[0],
    ]
    _agency_published_gtfs_urls = [
        AgencyAmtrak._agency_published_gtfs_urls[0],
        AgencyVIA._agency_published_gtfs_urls[0],
    ]

    def __init__(
        self: AgencyAmtrak,
    ) -> None:
        super().__init__()

    def get_station_name_pretty(
        self, station_code: str, doing_multiline_text=False, doing_html=True
    ) -> str:
        """
        Pretty-print a station name.
        """
        return station_names.get_station_name_pretty(
            station_code,
            doing_multiline_text=doing_multiline_text,
            doing_html=doing_html,
        )


# Establish the singleton
_singleton = AgencyMapleLeaf()


def get_singleton():
    """Get singleton for Maple Leaf"""
    global _singleton
    return _singleton
