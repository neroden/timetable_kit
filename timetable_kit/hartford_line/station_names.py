# hartford_line/station_names.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style Amtrak station names as HTML or text.

This diverges from the Amtrak implementation because we need to be much more compact,
and we need different connecting service info.
"""

import sys  # for sys.exit

# Map from station codes to connecting service names (matching those in timetable_kit.connecting_services)
from .connecting_services_data import connecting_services_dict

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html

# These are used to select how to do the prettyprinting
from timetable_kit.amtrak.json_stations import get_station_name
from timetable_kit.amtrak.special_data import is_standard_major_station


# This is the different one.
def station_name_to_html(station_name: str, major=False, show_connections=True) -> str:
    """
    Produce pretty station name for HTML -- potentially multiline, and complex.

    Hartford Line timetables are very compressed, and must do station names differently.
    We leave out the state.

    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable HTML version
    If "major", then make the station name bigger and bolder
    If "show_connections" (default True) then add links for connecting services (complex!)
    """

    if " - " in station_name:
        (city_state_name, second_part) = station_name.split(" - ", 1)
        (facility_name, suffix) = second_part.split(" (", 1)
        (station_code, _) = suffix.split(")", 1)
    else:
        facility_name = None
        (city_state_name, suffix) = station_name.split(" (", 1)
        (station_code, _) = suffix.split(")", 1)

    (city_name, state_name) = city_state_name.split(", ", 1)
    # Remove the comma, join with a space
    city_state_name = " ".join([city_name, state_name])

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

    # Only do facility names for a few stations
    if facility_name and facility_name not in ["Amtrak Station", "Amtrak/MBTA Station"]:
        # Put the facility name on its own line for Hartford Line
        br_for_facility_name = "<br>"
        if station_code == "NYP":
            # On Hartford Line timetable, we have no room.
            # facility_name == "Moynihan Train Hall"
            # Explain that this is Penn Station
            # We have the room because we're taking an extra line for connecting services
            facility_name = "Penn Station"
        if station_code == "STS":
            # On Hartford Line timetable, we have no room.
            # facility_name = "State Street Station"
            facility_name = "State Street"
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
        # station_code had better be correct, since we're going to look it up
        # stations with no entry in the dict are treated the same as
        # stations which have an empty list of connecting services
        connecting_services = connecting_services_dict.get(station_code, [])
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
            enhanced_facility_name,  # Has its own space or <br> before it
            " ",
            enhanced_station_code,  # Looks better after the facility name for Hartford Line
            connection_logos_html,  # Has spaces or <br> before it as needed
        ]
    )
    return fancy_name


# This is a complete duplicate of the Amtrak version. :sigh: Refactoring would be nice.
def get_station_name_pretty(
    station_code: str, doing_multiline_text=False, doing_html=False
) -> str:
    if doing_html:
        # Note here that show_connections is on by default.
        # There is no mechanism for turning it off.
        prettyprint_station_name = station_name_to_html
    else:
        # We're not really doing this.
        print("Hartford Line only has HTML output implemented.")
        sys.exit(1)

    raw_station_name = get_station_name(station_code)
    major = is_standard_major_station(station_code)
    cooked_station_name = prettyprint_station_name(raw_station_name, major)

    return cooked_station_name
