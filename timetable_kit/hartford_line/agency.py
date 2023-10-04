# hartford_line/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.maple_leaf.agency module

This holds a class for "AgencyHartfordLine" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.amtrak import AgencyAmtrak

# Map from station codes to connecting service names
# This is stashed in a class variable
from timetable_kit.hartford_line.connecting_services_data import (
    connecting_services_dict,
)


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

    def break_long_city_state_name(self, raw_city_state_name: str) -> str:
        """
        Hartford Line timetable has no spare width.  Remove the comma between city and state.
        """
        (city_name, state_name) = raw_city_state_name.split(", ", 1)
        # Remove the comma, join with a space
        city_state_name = " ".join([city_name, state_name])
        return city_state_name

    def replace_facility_names(self, station_code:str, facility_name:str) -> str:
        """
        Replace certain facility names; leave others intact.
        """
        match station_code:
            case "NYP":
                # facility_name == "Moynihan Train Hall"
                # Explain that this is Penn Station
                # No room for train hall reference
                facility_name = "Penn Station"
            case "STS":
                # facility_name == "State Street Station"
                # No room
                facility_name="State Street"

    def stations_with_many_connections(self) -> list[str]:
        """
        Stations with an extra line for connections.  None for Hartford Line.
        """
        return []


# Establish the singleton
_singleton = AgencyHartfordLine()


def get_singleton():
    """Get singleton for Hartford Line"""
    global _singleton
    return _singleton
