# hartford_line/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.maple_leaf.agency module

This holds a class for "AgencyHartfordLine" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.amtrak import AgencyAmtrak

# For our version of get_station_name_pretty
import timetable_kit.hartford_line.station_names as station_names

# Map from station codes to connecting service names
# This is stashed in a class variable
from timetable_kit.hartford_line.connecting_services_data import connecting_services_dict


class AgencyHartfordLine(AgencyAmtrak):
    """Hartford Line-specific code for interpreting specs and GTFS feeds"""

    _agency_names = ["CTRail Hartford Line", "Amtrak"]
    _agency_websites = ["HartfordLine.com", AgencyAmtrak._agency_websites[0]]
    _agency_published_gtfs_urls = [
        "https://www.cttransit.com/about/developers",
        AgencyAmtrak._agency_published_gtfs_urls[0],
    ]
    # Initialized from connecting_services_data.py
    _connecting_services_dict = connecting_services_dict

    def __init__(
        self: AgencyHartfordLine,
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
_singleton = AgencyHartfordLine()


def get_singleton():
    """Get singleton for Hartford Line"""
    global _singleton
    return _singleton
