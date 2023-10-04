# amtrak/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.amtrak.agency module

This holds a class for "AgencyAmtrak" intended to be used as a singleton.
"""
from __future__ import annotations

from timetable_kit.generic_agency import Agency

# for patch_feed
import timetable_kit.amtrak.gtfs_patches as gtfs_patches

# for patch_add_wheelchair_boarding
import timetable_kit.amtrak.access as access

# for sleeper trains, which trains have checked baggage, major stations, etc
import timetable_kit.amtrak.special_data as special_data

# for whether stations have checked baggage
import timetable_kit.amtrak.baggage as baggage

# for get_station_name
import timetable_kit.amtrak.json_stations as json_stations

# for get_station_name_pretty (subroutines)
import timetable_kit.amtrak.station_names as station_names
import timetable_kit.text_assembly as text_assembly

# Map from station codes to connecting service names
# This is stashed in a class variable
from timetable_kit.amtrak.connecting_services_data import connecting_services_dict

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html

# for get_route_name
import timetable_kit.amtrak.route_names as route_names


class AgencyAmtrak(Agency):
    """Amtrak-specific code for interpreting specs and GTFS feeds"""

    _agency_names = ["Amtrak"]
    _agency_websites = ["Amtrak.com"]
    _agency_published_gtfs_urls = [
        "https://www.transit.land/feeds/f-9-amtrak~amtrakcalifornia~amtrakcharteredvehicle"
    ]
    # Initialized from connecting_services_data.py
    _connecting_services_dict = connecting_services_dict

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

    def station_has_checked_baggage(self, station_code: str) -> bool:
        """
        Does this station have checked baggage service?
        """
        return baggage.station_has_checked_baggage(station_code)

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

    def is_high_speed_train(self, tsn: str) -> bool:
        """
        Should this train be marked as high-speed in the timetable?
        """
        return special_data.is_high_speed_train(tsn)

    def is_connecting_service(self, tsn: str) -> bool:
        """
        Should this be marked as a connecting service in the timetable?
        """
        # This is not the ideal implementation.
        # This should be implemented by checking the agency.txt file,
        # and seeing which trains are run by different agencies.
        # However, we have a working implementation based on tsns.
        return special_data.is_connecting_service(tsn)

    def connecting_bus_key_sentence(self, doing_html=True) -> str:
        """
        Sentence to put in the symbol key for connecting bus services
        """
        return "Connecting Bus Service (can be booked through Amtrak)"

    def agency_css_class(self) -> str:
        """
        Name of a CSS class for agency-specific styling
        """
        return "amtrak-special-css"

    def get_route_name(self, today_feed: FeedEnhanced, route_id: str) -> str:
        """
        Given today_feed and a route_id, produce a suitalbe name for a column subheading.
        The implementation is Amtrak-specific.
        """
        return route_names.get_route_name(today_feed, route_id)

    def stop_code_to_stop_name(self, stop_code: str) -> str:
        """
        Use Amtrak JSON data.
        """
        return json_stations.get_station_name(stop_code)

    def disassemble_station_name(self, station_name: str):
        """
        Disassemble an Amtrak station name in one of these two forms:
        Champaign-Urbana, IL (CHM)
        New Orleans, LA - Union Passenger Terminal (NOL)
        into (city_state_name, facility_name, station_code).
        Return a tuple.
        """
        if " - " in station_name:
            (city_state_name, second_part) = station_name.split(" - ", 1)
            (facility_name, suffix) = second_part.split(" (", 1)
            (station_code, _) = suffix.split(")", 1)
        else:
            facility_name = None
            (city_state_name, suffix) = station_name.split(" (", 1)
            (station_code, _) = suffix.split(")", 1)
        return (city_state_name, facility_name, station_code)

    def is_standard_major_station(self, station_code: str) -> bool:
        """
        Is this a "major" station which should be boldfaced and capitalized?
        """
        return special_data.is_standard_major_station(station_code)

    def get_station_name_pretty(
        self, station_code: str, doing_multiline_text=False, doing_html=True
    ) -> str:
        """
        Pretty-print a station name.
        """
        # Get the raw station name (from JSON)
        station_name = self.stop_code_to_stop_name(station_code)
        # Disassemble it.
        (city_state_name, facility_name, station_code) = self.disassemble_station_name(
            station_name
        )

        # Get the major station information.
        major = self.is_standard_major_station(station_code)

        # Call the appropriate reassembly routine.
        if doing_html:
            return self.disassembled_station_name_to_html(
                city_state_name, facility_name, station_code, major
            )
        elif doing_multiline_text:
            reassemble = text_assembly.station_name_to_multiline_text
            return reassemble(city_state_name, facility_name, station_code, major)
        else:
            reassemble = text_assembly.station_name_to_single_line_text
            return reassemble(city_state_name, facility_name, station_code, major)

    def break_long_city_state_name(self, raw_city_state_name: str) -> str:
        """
        Add HTML <br> to certain city names which are too long.
        """
        match raw_city_state_name:
            case "Grand Canyon Village, AZ":
                city_state_name = "Grand Canyon<br>Village, AZ"
            case "Essex Junction-Burlington, VT":
                city_state_name = "Essex Junction<br>-Burlington, VT"
            case "Lompoc-Surf, CA -Amtrak Station":
                city_state_name = "Lompoc-Surf, CA"
            # You would think you'd want to do St. Paul-Minneapolis,...
            # but there's plenty of horizontal space in the EB timetable
            # and no vertical space
            case _:
                city_state_name = raw_city_state_name
        return city_state_name

    def replace_facility_names(self, station_code: str, facility_name: str) -> str:
        """
        Replace certain facility names; leave others intact.
        """
        match station_code:
            case "PHL":
                # facility_name == "William H. Gray III 30th St. Station"
                # Sorry, Mr. Gray, your name is too long
                facility_name = "30th St. Station"
            case "NYP":
                # facility_name == "Moynihan Train Hall"
                # Explain that this is Penn Station
                # We have the room for the long version
                # because we're taking an extra line for connecting services
                facility_name = "Moynihan Train Hall at Penn Station"
        return facility_name

    def stations_to_put_facility_on_first_line(self) -> list[str]:
        """
        Stations where the facility name should be in the same line as the station.
        """
        # Save lines on some timetables by putting the facility code on the same line as the station
        # This is needed at Boston for the Richmond timetable
        # Consider at Toronto for the sheer number of connecting services on the next line
        return ["BOS", "BBY"]

    def stations_with_many_connections(self) -> list[str]:
        """
        Return a list of station codes which should get an extra line for connections.
        """
        # NYP has a long facility name and a lot of connections
        # SLC has connections with very long lines
        # On the Pacific Surfliner:
        # SNC (San Juan Capistrano), OSD (Oceanside)
        # have excessively wide connection logos
        # Grab an extra line in these cases
        # TWO (Toronto) has a lot of connections,
        # but Empire Service timetables have more width than length available
        return ["NYP", "SLC", "SNC", "OSD"]

    def stations_with_connections_on_first_line(self) -> list[str]:
        """
        List of station codes where the connections should be on the first line rather than the second.
        """
        # San Diego Old Town has a short station name and a long facility name,
        # but also several long connecting services.  So put connections on line one,
        # before the facility name line.
        # Same with Anaheim.
        # Currently disabled because we aren't making the Pacific Surfliner timetable,
        # and it doesn't matter for the Coast Starlight timetable.
        return []
        # return ["ANA", "OLT"]

    def disassembled_station_name_to_html(
        self,
        city_state_name: str,
        facility_name: Optional[str],
        station_code: str,
        major=False,
        show_connections=True,
    ) -> str:
        """
        Given a disassembled station name, produce suitable HTML.

        If "major", then make the station name bigger and bolder
        If "show_connections" (default True) then add links for connecting services (complex!)
        """

        # Add <br> to certain extra-long city & state names
        city_state_name = self.break_long_city_state_name(city_state_name)

        # Add styling for major stations
        if major:
            enhanced_city_state_name = "".join(
                ["<span class=major-station >", city_state_name, "</span>"]
            )
        else:
            enhanced_city_state_name = "".join(
                ["<span class=minor-station >", city_state_name, "</span>"]
            )

        # Add the station code in smaller print
        enhanced_station_code = "".join(
            ["<span class=station-footnotes>(", station_code, ")</span>"]
        )

        # Certain stations need special treatment on the facility names.
        facility_name = self.replace_facility_names(station_code, facility_name)

        # It looks stupid to see "- Amtrak Station."
        # I know it's there to distinguish from bus stops, but come on.
        # Let's assume it's the Amtrak station unless otherwise specified.
        # Also saves critical vertical space on Empire Builder timetable.
        #
        # Also eliminate Providence's "Amtrak/MBTA Station";
        # saves critical space on NEC timetables, and we're indicating the MBTA connection
        # in another way anyway.
        if facility_name and facility_name not in [
            "Amtrak Station",
            "Amtrak/MBTA Station",
        ]:
            # By default, put the facility name on its own line
            br_for_facility_name = "<br>"
            if station_code in self.stations_to_put_facility_on_first_line():
                br_for_facility_name = " "
            enhanced_facility_name = "".join(
                [
                    br_for_facility_name,
                    "<span class=station-footnotes>",
                    " - ",
                    facility_name,
                    "</span>",
                ]
            )
        else:
            enhanced_facility_name = ""

        # Connections.  Hoo boy.  Default to nothing.
        connection_logos_html = ""
        if show_connections:
            # Grab an extra line for certain stations with LOTS of connections
            if station_code in self.stations_with_many_connections():
                connection_logos_html += "<br>"
            # station_code had better be correct, since we're going to look it up
            # stations with no entry in the dict are treated the same as
            # stations which have an empty list of connecting services
            connecting_services = self._connecting_services_dict.get(station_code, [])
            for connecting_service in connecting_services:
                # Note, this is "" if the agency is not found (but a debug error will print)
                # Otherwise it's a complete HTML code for the agency & its icon
                this_logo_html = get_connecting_service_logo_html(connecting_service)
                if this_logo_html:
                    # Add a space before the logo... if it exists at all
                    connection_logos_html += " "
                    connection_logos_html += this_logo_html
            # Initial implementation tucks all connecting services on the same line.
            # This seems to be working.

        fancy_name = "".join(
            [
                enhanced_city_state_name,
                " ",
                enhanced_station_code,
                enhanced_facility_name,  # Has its own space or <br> before it
                connection_logos_html,  # Has spaces or <br> before it as needed
            ]
        )
        # For some stations, there's more room on the first line than the second for connections.
        if station_code in self.stations_with_connections_on_first_line():
            fancy_name = "".join(
                [
                    enhanced_city_state_name,
                    " ",
                    enhanced_station_code,
                    connection_logos_html,  # Has spaces or <br> before it as needed
                    enhanced_facility_name,  # Has its own space or <br> before it
                ]
            )
        return fancy_name


# Establish the singleton
_singleton = AgencyAmtrak()


def get_singleton():
    """Get singleton for Amtrak"""
    global _singleton
    return _singleton
