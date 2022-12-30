# amtrak/station_name_styling.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style Amtrak station names as HTML or text.
"""

# Map from station codes to connecting service names (matching those in timetable_kit.connecting_services)
from timetable_kit.amtrak.connecting_services_data import connecting_services_dict

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html


def amtrak_station_name_to_multiline_text(station_name: str, major=False) -> str:
    """
    Produce pretty Amtrak station name for plaintext -- multi-line.

    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable text version (possibly multiple lines)
    If "major", then make the station name bigger and bolder
    We want to avoid very long lines as they mess up timetable formats
    """
    if " - " in station_name:
        (city_state_name, second_part) = station_name.split(" - ", 1)
        (facility_name, suffix) = second_part.split(" (", 1)
        (station_code, _) = suffix.split(")", 1)
    else:
        facility_name = None
        (city_state_name, suffix) = station_name.split(" (", 1)
        (station_code, _) = suffix.split(")", 1)

    if major:
        enhanced_city_state_name = city_state_name.upper()
    else:
        enhanced_city_state_name = city_state_name

    enhanced_station_code = "".join(["(", station_code, ")"])

    if facility_name:
        enhanced_facility_name = "".join(["\n", " - ", facility_name])
    else:
        enhanced_facility_name = ""

    fancy_name = "".join(
        [enhanced_city_state_name, " ", enhanced_station_code, enhanced_facility_name]
    )
    return fancy_name


def amtrak_station_name_to_single_line_text(station_name: str, major=False) -> str:
    """
    Produce pretty Amtrak station name for plaintext -- single line.

    The easy version.  Station name to single line text.
    """
    if major:
        styled_station_name = station_name.upper()
    else:
        styled_station_name = station_name
    return styled_station_name


def amtrak_station_name_to_html(
    station_name: str, major=False, show_connections=True
) -> str:
    """
    Produce pretty Amtrak station name for HTML -- potentially multiline, and complex.

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

    # Special cases for exceptionally long city/state names.
    # Insert line breaks.
    raw_city_state_name = city_state_name
    match raw_city_state_name:
        case "Grand Canyon Village, AZ":
            city_state_name = "Grand Canyon<br>Village, AZ"
        case "Essex Junction-Burlington, VT":
            city_state_name = "Essex Junction<br>-Burlington, VT"
        # You would think you'd want to do St. Paul-Minneapolis,...
        # but there's plenty of horizontal space in the EB timetable
        # and no vertical space

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

    # It looks stupid to see "- Amtrak Station."
    # I know it's there to distinguish from bus stops, but come on.
    # Let's assume it's the Amtrak station unless otherwise specified.
    # Also saves critical vertical space on Empire Builder timetable.
    if facility_name and facility_name != "Amtrak Station":
        enhanced_facility_name = "".join(
            ["<br><span class=station-footnotes>", " - ", facility_name, "</span>"]
        )
    else:
        enhanced_facility_name = ""

    # Connections.  Hoo boy.  Default to nothing.
    connection_logos_html = ""
    if show_connections:
        # Special-casing for certain stations with LOTS of connections
        if station_code in []:
            # PHL has a very long facility_name;
            # WAS has a very long list of connecting services.
            # So snarf an extra line.
            connection_logos_html += "<br>"
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

    fancy_name = " ".join(
        [
            enhanced_city_state_name,
            enhanced_station_code,
            enhanced_facility_name,
            connection_logos_html,
        ]
    )
    return fancy_name
