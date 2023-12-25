# maple_leaf/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.maple_leaf.agency module

This holds a class for "AgencyMapleLeaf" intended to be used as a singleton.
"""
import timetable_kit.text_assembly as text_assembly

from timetable_kit.amtrak import AgencyAmtrak
from timetable_kit.via import AgencyVIA

# Map from station codes to connecting service names
# This is stashed in a class variable
from timetable_kit.maple_leaf.connecting_services_data import connecting_services_dict

# For getting VIA station codes to print them
from timetable_kit.maple_leaf.station_data import amtrak_code_to_via_code


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

    def __init__(self) -> None:
        super().__init__()
        # Initialized from connecting_services_data.py
        self._connecting_services_dict = connecting_services_dict

    def get_station_name_pretty(
        self, station_code: str, doing_multiline_text=False, doing_html=True
    ) -> str:
        """
        Pretty-print a station name.
        """
        # Get the raw station name (from JSON; Amtrak data contains the VIA stops, even the ones not in Amtrak GTFS)
        station_name = self.stop_code_to_stop_name(station_code)
        # Disassemble it.
        (city_state_name, facility_name) = self.disassemble_station_name(station_name)

        # Special tweak for Maple Leaf: print Amtrak and VIA codes
        via_code = amtrak_code_to_via_code[station_code]
        enhanced_station_code = station_code + " / " + via_code

        # Get the major station information.
        major = self.is_standard_major_station(station_code)

        # Call the appropriate reassembly routine.
        if doing_html:
            return self.disassembled_station_name_to_html(
                city_state_name, facility_name, enhanced_station_code, major
            )
        elif doing_multiline_text:
            reassemble = text_assembly.station_name_to_multiline_text
            return reassemble(
                city_state_name, facility_name, enhanced_station_code, major
            )
        else:
            reassemble = text_assembly.station_name_to_single_line_text
            return reassemble(
                city_state_name, facility_name, enhanced_station_code, major
            )

    def get_all_connecting_services(self, station_list: list[str]) -> list[str]:
        """
        Given a list of station codes, return a list of services which connect
        (with no duplicates)
        """
        # Special tweak for Maple Leaf: connecting services indexed by "Amtrak code / VIA code"
        enhanced_station_list = [
            station_code + " / " + amtrak_code_to_via_code[station_code]
            for station_code in station_list
            if station_code in amtrak_code_to_via_code
        ]
        print("Enhanced station list", enhanced_station_list)
        return super().get_all_connecting_services(enhanced_station_list)


# Establish the singleton
_singleton = AgencyMapleLeaf()


def get_singleton():
    """Get singleton for Maple Leaf"""
    global _singleton
    return _singleton
