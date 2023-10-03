# via/agency.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
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

# All the rest are for get_station_name_pretty
from timetable_kit.debug import set_debug_level, debug_print

# For subroutines of get_station_name_pretty
import timetable_kit.via.station_names as station_names

# Should the station be boldfaced
from timetable_kit.via.special_data import is_standard_major_station

# Map from station codes to connecting service names
# This is stashed in a class variable
from timetable_kit.via.connecting_services_data import connecting_services_dict

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html


class AgencyVIA(Agency):
    """VIA-specific code for interpreting specs and GTFS feeds"""

    _agency_names = ["VIA Rail"]
    _agency_websites = ["ViaRail.ca"]
    _agency_published_gtfs_urls = [
        "https://www.transit.land/feeds/f-f-viarail~traindecharlevoix"
    ]
    # Initialized from connecting_services_data.py
    _connecting_services_dict = connecting_services_dict

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

    def is_connecting_service(self, tsn: str) -> bool:
        """
        Should this be marked as a connecting service in the timetable?
        """
        # VIA has two connecting services in its GTFS, but
        # *they don't have tsns* and so we'd need to patch the feed.
        # FIXME later.  For now, return false.
        return False

    def connecting_bus_key_sentence(self, doing_html=True) -> str:
        """
        Sentence to put in the symbol key for connecting bus services
        """
        return "Connecting Bus Service (can be booked through VIA Rail)"

    def add_via_disclaimer(self, doing_html=True) -> bool:
        """
        Should we add the VIA disclaimer?

        This is boolean because the disclaimer is multiline and needs Jinja macros.
        """
        return True

    def agency_css_class(self) -> str:
        """
        Name of a CSS class for agency-specific styling
        """
        return "via-special-css"

    def get_station_name_pretty(
        self, station_code: str, doing_multiline_text=False, doing_html=True
    ) -> str:
        """
        Given a VIA stop_code, return a suitable pretty-printed station name
        for plaintext, multiline text, or HTML
        """
        # This is long.

        # First, get the raw station name: Memoized
        stop_name_raw = self.stop_code_to_stop_name(station_code)
        # Is it major?
        major = is_standard_major_station(station_code)

        # Default to no facility name
        facility_name = None

        # Call a subroutine to handle all the special cases
        # for specific named stations (Montreal, Vancouver, Niagara Falls, etc.)
        (stop_name_clean, facility_name) = station_names._fix_name_and_facility(
            stop_name_raw, facility_name
        )

        # We actually want to add the province to every station,
        # but VIA doesn't provide that info.  It's too much work.
        # FIXME

        # Uppercase major stations
        if major:
            stop_name_styled = stop_name_clean.upper()
        else:
            stop_name_styled = stop_name_clean

        # Default facility_name_addon to nothing...
        facility_name_addon = ""
        if doing_html:
            # There is some duplication of code between here and the Amtrak module.
            # Hence the misleading use of "city_state_name".  FIXME by pulling out common code
            city_state_name = stop_name_clean

            if major:
                enhanced_city_state_name = "".join(
                    ["<span class=major-station >", city_state_name, "</span>"]
                )
            else:
                enhanced_city_state_name = "".join(
                    ["<span class=minor-station >", city_state_name, "</span>"]
                )

            enhanced_station_code = "".join(
                ["<span class=station-footnotes>(", station_code, ")</span>"]
            )

            if facility_name:
                facility_name_addon = "".join(
                    [
                        "<br>",
                        "<span class=station-footnotes>",
                        " - ",
                        facility_name,
                        "</span>",
                    ]
                )

            connection_logos_html = ""
            connecting_services = connecting_services_dict.get(station_code, [])
            for connecting_service in connecting_services:
                # Note, this is "" if the agency is not found (but a debug error will print)
                # Otherwise it's a complete HTML code for the agency & its icon
                this_logo_html = get_connecting_service_logo_html(connecting_service)
                if this_logo_html:
                    # Add a space before the logo... if it exists at all
                    connection_logos_html += " "
                    connection_logos_html += this_logo_html

            cooked_station_name = "".join(
                [
                    enhanced_city_state_name,
                    " ",
                    enhanced_station_code,
                    facility_name_addon,  # Has its own space or <br> before it
                    connection_logos_html,  # Has spaces or <br> before it as needed
                ]
            )

        elif doing_multiline_text:
            # Multiline text. "Toronto (TRTO)\nSuffix"
            if facility_name:
                facility_name_addon = "\n - " + facility_name
            cooked_station_name = "".join(
                [stop_name_styled, " (", stop_code, ")", facility_name_addon]
            )
        else:
            # Single Line text: "Toronto - Suffix (TRTO)"
            if facility_name:
                facility_name_addon = " - " + facility_name
            cooked_station_name = "".join(
                [stop_name_styled, facility_name_addon, " (", stop_code, ")"]
            )
        return cooked_station_name


# Establish the singleton
_singleton = AgencyVIA()


def get_singleton():
    """Get singleton for VIA"""
    global _singleton
    return _singleton
