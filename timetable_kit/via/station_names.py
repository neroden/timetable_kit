# via/station_names.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style VIA station names as HTML or text.

Also routines to move from stop_id to and from station_code, and get station names.

Exported:
get_station_name_pretty
stop_id_to_stop_code
stop_code_to_stop_id

FIXME -- very much not ready
"""

from timetable_kit.debug import set_debug_level, debug_print

# Should the station be boldfaced
from timetable_kit.via.special_data import is_standard_major_station

# Map from station codes to connecting service names (matching those in timetable_kit.connecting_services)
from timetable_kit.via.connecting_services_data import connecting_services_dict

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html

# FIXME -- _prepare_dicts has horrible callbacks into timetable_kit.initialize.initialize_feed
from timetable_kit.via.get_gtfs import gtfs_unzipped_local_path
from timetable_kit.initialize import initialize_feed

# Initialization code.  We build the stop_code_to_stop_id and stop_id_to_stop_code dicts
# from the GTFS.
# These start blank and are filled in by initialization code on first use (memoized)
stop_code_to_stop_id_dict = None
stop_id_to_stop_code_dict = None


def _prepare_dicts():
    """
    Prepare the dicts for stop_code_to_stop_id and stop_id_to_stop_code.
    These depend on a previously established feed.
    """
    debug_print(1, "Preparing stop_code / stop_id dicts")

    # Right now this quite brutally reloads the feed.
    # FIXME this is a HORRIBLE hack and we don't want to do it
    gtfs_filename = gtfs_unzipped_local_path
    feed = initialize_feed(gtfs=gtfs_filename)

    # Now extract the dicts from the feed
    stop_codes = feed.stops["stop_code"].to_list()
    stop_ids = feed.stops["stop_id"].to_list()

    global stop_code_to_stop_id_dict
    global stop_id_to_stop_code_dict
    stop_code_to_stop_id_dict = dict(zip(stop_codes, stop_ids))
    stop_id_to_stop_code_dict = dict(zip(stop_ids, stop_codes))
    return


def stop_code_to_stop_id(stop_code: str) -> str:
    """Given a VIA stop_code, return a VIA stop_id"""
    # Memoized
    global stop_code_to_stop_id_dict
    if stop_code_to_stop_id_dict == None:
        _prepare_dicts()
    return stop_code_to_stop_id_dict[stop_code]


def stop_id_to_stop_code(stop_id: str) -> str:
    """Given a VIA stop_id, return a VIA stop_code"""
    # Memoized
    global stop_id_to_stop_code_dict
    if stop_id_to_stop_code_dict == None:
        _prepare_dicts()
    return stop_id_to_stop_code_dict[stop_id]


def get_station_name(station_code: str) -> str:
    """Given a VIA stop_code, return a suitable station name for plaintext"""
    # TODO FIXME
    return station_code


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


def station_name_to_single_line_text(station_name: str, major=False) -> str:
    """
    Produce pretty Amtrak station name for plaintext -- single line.

    The easy version.  Station name to single line text.
    """
    if major:
        styled_station_name = station_name.upper()
    else:
        styled_station_name = station_name
    return styled_station_name


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
        # By default, put the facility name on its own line
        br_for_facility_name = "<br>"
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
        # Special-casing for certain stations with LOTS of connections
        if station_code in []:
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

    fancy_name = "".join(
        [
            enhanced_city_state_name,
            " ",
            enhanced_station_code,
            enhanced_facility_name,  # Has its own space or <br> before it
            connection_logos_html,  # Has spaces or <br> befor it as needed
        ]
    )
    if station_code in []:
        # Put connections on line one, before the facility name line.
        fancy_name = "".join(
            [
                enhanced_city_state_name,
                " ",
                enhanced_station_code,
                enhanced_facility_name,  # Has its own space or <br> before it
                connection_logos_html,  # Has spaces or <br> befor it as needed
            ]
        )
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


### TESTING
if __name__ == "__main__":
    import timetable_kit

    set_debug_level(2)
    print(
        "Toronto stop id is:",
        timetable_kit.via.station_names.stop_code_to_stop_id("TRTO"),
    )
