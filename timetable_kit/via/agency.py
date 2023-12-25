# via/agency.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.via.agency module.

This holds a class for "AgencyVIA" intended to be used as a singleton.
"""
from typing import Tuple

from timetable_kit.feed_enhanced import FeedEnhanced
from timetable_kit.generic_agency import Agency

# For generic reassembly functions
import timetable_kit.text_assembly as text_assembly

# for patch_feed
import timetable_kit.via.gtfs_patches as gtfs_patches

# For checked baggage, sleeper trains, major stations list
import timetable_kit.via.special_data as special_data

# All the rest are for get_station_name_pretty
from timetable_kit.debug import set_debug_level, debug_print

# Map from station codes to connecting service names
# This is stashed in a class variable
from timetable_kit.via.connecting_services_data import connecting_services_dict

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html

# For get_route_name
import timetable_kit.via.route_names as route_names

# For getting the province for a given stop code
from timetable_kit.via.province_data import stop_code_to_province


class AgencyVIA(Agency):
    """VIA-specific code for interpreting specs and GTFS feeds."""

    _agency_names = ["VIA Rail"]
    _agency_websites = ["ViaRail.ca"]
    _agency_published_gtfs_urls = [
        "https://www.transit.land/feeds/f-f-viarail~traindecharlevoix"
    ]

    def __init__(self) -> None:
        super().__init__()
        # Initialized from connecting_services_data.py
        self._connecting_services_dict = connecting_services_dict

    def patch_feed(self, feed: FeedEnhanced) -> FeedEnhanced:
        """Apply VIA-specific patches to a feed.

        Returns the patched feed. Does not alter data in the Agency object.
        """
        # This is defined in its own file in the VIA subpackage.
        return gtfs_patches.patch_feed(feed)

    def station_has_checked_baggage(self, station_code: str) -> bool:
        """Does this station have checked baggage service?"""
        return special_data.station_has_checked_baggage(station_code)

    def train_has_checked_baggage(self, tsn: str) -> bool:
        """Does this train have checked baggage service?"""
        return special_data.train_has_checked_baggage(tsn)

    def is_sleeper_train(self, tsn: str) -> bool:
        """Does this train have sleeper cars?"""
        return special_data.is_sleeper_train(tsn)

    def is_connecting_service(self, tsn: str) -> bool:
        """Should this be marked as a connecting service in the timetable?"""
        # VIA has two connecting services in its GTFS, but
        # *they don't have tsns* and so we'd need to patch the feed.
        # FIXME later.  For now, return false.
        return False

    def connecting_bus_key_sentence(self, doing_html=True) -> str:
        """Sentence to put in the symbol key for connecting bus services."""
        return "Connecting Bus Service (can be booked through VIA Rail)"

    def add_via_disclaimer(self, doing_html=True) -> bool:
        """Should we add the VIA disclaimer?

        This is boolean because the disclaimer is multiline and needs Jinja macros.
        """
        return True

    def agency_css_class(self) -> str:
        """Name of a CSS class for agency-specific styling."""
        return "via-special-css"

    def get_route_name(self, today_feed: FeedEnhanced, route_id: str) -> str:
        """Given today_feed and a route_id, produce a suitalbe name for a column
        subheading.

        The implementation is VIA-specific.
        """
        return route_names.get_route_name(today_feed, route_id)

    def is_standard_major_station(self, station_code: str) -> bool:
        """Is this a "major" station which should be boldfaced and capitalized?"""
        return special_data.is_standard_major_station(station_code)

    def disassemble_station_name(self, stop_name_raw: str) -> Tuple[str, str | None]:
        """Separates suffixes like "GO Station" from VIA station names, as "facility
        name".

        Returns the tuple (stop_name, facility name)

        Also renames certain "troublemaker" stations (Niagara Falls).
        """
        # Default to no facility name.
        facility_name = None
        # Several stations have (EXO) in parentheses: one has (exo).  Get rid of this.
        # Some have GO Bus or GO as suffixes.  Get rid of this.
        # Clarify the confusing Niagara Falls situation.
        if stop_name_raw.endswith(" (EXO)"):
            stop_name_clean = stop_name_raw.removesuffix(" (EXO)")
            facility_name = "EXO station"
        elif stop_name_raw.endswith(" (exo)"):
            stop_name_clean = stop_name_raw.removesuffix(" (exo)")
            facility_name = "EXO station"
        elif stop_name_raw.endswith(" GO Bus"):
            stop_name_clean = stop_name_raw.removesuffix(" GO Bus")
            facility_name = "GO Bus station"
        elif stop_name_raw.endswith(" GO"):
            stop_name_clean = stop_name_raw.removesuffix(" GO")
            facility_name = "GO station"
        elif stop_name_raw.endswith(" Bus"):
            stop_name_clean = stop_name_raw.removesuffix(" Bus")
            facility_name = "Bus station"
        elif stop_name_raw == "Niagara Falls Station":
            # stop_name_clean = "Niagara Falls, NY"
            # We patch in the state later
            stop_name_clean = "Niagara Falls"
        elif stop_name_raw == "Niagara Falls":
            # stop_name_clean = "Niagara Falls, ON"
            # We patch in the province later
            stop_name_clean = "Niagara Falls"
        else:
            stop_name_clean = stop_name_raw
        return (stop_name_clean, facility_name)

    def break_long_city_state_name(self, raw_city_state_name: str) -> str:
        """Add HTML <br> to certain city names which are too long."""
        match raw_city_state_name:
            case "Thicket Portage, MB" | "Atikameg Lake, MB" | "The Pas, MB":
                # Makes the Churchill timetable too wide.
                # In the case of The Pas, it fits but looks ugly with the
                # KRC connecting indicators.
                city_state_name = raw_city_state_name + "<br>"
            case _:
                city_state_name = raw_city_state_name
        return city_state_name

    def replace_facility_names(
        self, station_code: str, facility_name: str | None
    ) -> str | None:
        """Remove or add certain facility names; leave others intact."""
        # Only called when generating HTML (consider fixing this?)
        match station_code:
            case "SFOY":
                # Sainte-Foy: explain where the station is
                facility_name = "for Quebéc City"
            case "QBEC":
                # Quebec: Distinguish from other Quebec City stations
                facility_name = "Gare du Palais"
            case "MTRL":
                # Montreal: There are two train stations here (it's not Lucien L'Allier)
                facility_name = "Central Station"
            case "ANJO" | "SAUV":
                # Anjou, Sauvé
                # On the Senneterre timetable,
                # "EXO station" blows out a line which we need for Montreal
                facility_name = None
            case "OTTW":
                # Ottawa: Make it clear which LRT station this goes with
                facility_name = "Tremblay"
            case "TRTO":
                # Toronto: Just for clarity
                facility_name = "Union Station"
            case "VCVR":
                # Vancouver: There are two train stations here (it's not Waterfront)
                facility_name = "Pacific Central Station"
        return facility_name

    def get_station_name_pretty(
        self, station_code: str, doing_multiline_text=False, doing_html=True
    ) -> str:
        """Given a VIA stop_code, return a suitable pretty-printed station name for
        plaintext, multiline text, or HTML."""
        # First, get the raw station name: Memoized
        stop_name_raw = self.stop_code_to_stop_name(station_code)
        # Is it major?
        major = self.is_standard_major_station(station_code)

        # Disassemble the station name into city_name and facility name.
        (city_name, facility_name) = self.disassemble_station_name(stop_name_raw)

        # We actually want to append the province to every station.
        # VIA doesn't provide that information but we can supply it.
        province = stop_code_to_province(station_code)
        if province:
            city_name = ", ".join([city_name, province])

        # Call the appropriate reassembly routine.
        if doing_html:
            return self.disassembled_station_name_to_html(
                city_name, facility_name, station_code, major
            )
        elif doing_multiline_text:
            reassemble = text_assembly.station_name_to_multiline_text
            return reassemble(city_name, facility_name, station_code, major)
        else:
            reassemble = text_assembly.station_name_to_single_line_text
            return reassemble(city_name, facility_name, station_code, major)


# Establish the singleton
_singleton = AgencyVIA()


def get_singleton():
    """Get singleton for VIA."""
    global _singleton
    return _singleton
