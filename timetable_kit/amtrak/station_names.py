# amtrak/station_names.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style Amtrak station names as HTML or text.
"""

# Map from station codes to connecting service names (matching those in timetable_kit.connecting_services)
from timetable_kit.amtrak.connecting_services_data import connecting_services_dict

# These are used to select how to do the pretty-printing
from timetable_kit.amtrak.json_stations import get_station_name
from timetable_kit.amtrak.special_data import is_standard_major_station

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html
from timetable_kit.generic_agency.station_names import parse_station_name


def station_name_to_multiline_text(station_name: str, major=False) -> str:
    """
    Produce pretty Amtrak station name for plaintext -- multi-line.

    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable text version (possibly multiple lines)
    If "major", then make the station name bigger and bolder
    We want to avoid very long lines as they mess up timetable formats
    """
    (city_state_name, facility_name, station_code) = parse_station_name(station_name)

    enhanced_city_state_name = city_state_name.upper() if major else city_state_name

    enhanced_station_code = f"({station_code})"

    enhanced_facility_name = f"\n - {facility_name}" if facility_name else ""

    fancy_name = (
        f"{enhanced_city_state_name} {enhanced_station_code}{enhanced_facility_name}"
    )
    return fancy_name


def station_name_to_single_line_text(station_name: str, major=False) -> str:
    """
    Produce pretty Amtrak station name for plaintext -- single line.

    The easy version.  Station name to single line text.
    """
    return station_name.upper() if major else station_name


def station_name_to_html(station_name: str, major=False, show_connections=True) -> str:
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
        case "Lompoc-Surf, CA -Amtrak Station":
            city_state_name = "Lompoc-Surf, CA"
        # You would think you'd want to do St. Paul-Minneapolis,...
        # but there's plenty of horizontal space in the EB timetable
        # and no vertical space

    if major:
        enhanced_city_state_name = (
            f"<span class=major-station >{city_state_name}</span>"
        )
    else:
        enhanced_city_state_name = (
            f"<span class=minor-station >{city_state_name}</span>"
        )

    enhanced_station_code = f"<span class=station-footnotes>({station_code})</span>"

    # It looks stupid to see "- Amtrak Station."
    # I know it's there to distinguish from bus stops, but come on.
    # Let's assume it's the Amtrak station unless otherwise specified.
    # Also saves critical vertical space on Empire Builder timetable.
    #
    # Also eliminate Providence's "Amtrak/MBTA Station";
    # saves critical space on NEC timetables, and we're indicating the MBTA connection
    # in another way anyway.
    if facility_name and facility_name not in ["Amtrak Station", "Amtrak/MBTA Station"]:
        # By default, put the facility name on its own line
        br_for_facility_name = "<br>"
        if station_code in ["BOS", "BBY"]:
            # Save lines on some timetables by putting the facility code on the same line as the station
            # This is needed at Boston for the Richmond timetable
            # Consider at Toronto for the sheer number of connecting services on the next line
            br_for_facility_name = " "
        if station_code == "PHL":
            # facility_name == "William H. Gray III 30th St. Station"
            # Sorry, Mr. Gray, your name is too long
            facility_name = "30th St. Station"
        if station_code == "NYP":
            # facility_name == "Moynihan Train Hall"
            # Explain that this is Penn Station
            # We have the room because we're taking an extra line for connecting services
            facility_name = "Moynihan Train Hall at Penn Station"
        enhanced_facility_name = f"{br_for_facility_name}<span class=station-footnotes> - {facility_name}</span>"
    else:
        enhanced_facility_name = ""

    # Connections.  Hoo boy.  Default to nothing.
    connection_logos_html = ""
    if show_connections:
        # Special-casing for certain stations with LOTS of connections
        if station_code in ["NYP", "SLC", "SNC", "OSD"]:
            # NYP has a long facility name and a lot of connections
            # SLC has connections with very long lines
            # On the Pacific Surfliner:
            # SNC (San Juan Capistrano), OSD (Oceanside)
            # have excessively wide connection logos
            # Grab an extra line in these cases
            # TWO (Toronto) has a lot of connections,
            # but Empire Service timetables have more width than length available
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

    fancy_name = (
        f"{enhanced_city_state_name} {enhanced_station_code}"
        + enhanced_facility_name  # Has its own space or <br> before it
        + connection_logos_html  # Has spaces or <br> before it as needed
    )
    # FIXME: This is commented out because it's the same assignment after a check. Is it supposed to be here?
    # if station_code in ["ANA", "OLT"]:
    #     # San Diego Old Town has a short station name and a long facility name,
    #     # but also several long connecting services.  So put connections on line one,
    #     # before the facility name line.
    #     # Same with Anaheim.
    #     fancy_name = "".join(
    #         [
    #             enhanced_city_state_name,
    #             " ",
    #             enhanced_station_code,
    #             enhanced_facility_name,  # Has its own space or <br> before it
    #             connection_logos_html,  # Has spaces or <br> before it as needed
    #         ]
    #     )
    return fancy_name


def get_station_name_pretty(
    station_code: str, doing_multiline_text=False, doing_html=False
) -> str:
    if doing_html:
        # Note here that show_connections is on by default.
        # There is no mechanism for turning it off.
        prettyprint_station_name = station_name_to_html
    elif doing_multiline_text:
        prettyprint_station_name = station_name_to_multiline_text
    else:
        prettyprint_station_name = station_name_to_single_line_text

    raw_station_name = get_station_name(station_code)
    major = is_standard_major_station(station_code)
    cooked_station_name = prettyprint_station_name(raw_station_name, major)

    return cooked_station_name
