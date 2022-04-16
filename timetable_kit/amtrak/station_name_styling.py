# amtrak/station_name_styling.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style Amtrak station names as HTML or text.
"""


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


def amtrak_station_name_to_html(station_name: str, major=False) -> str:
    """
    Produce pretty Amtrak station name for HTML -- potentially multiline, and complex.

    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable HTML version
    If "major", then make the station name bigger and bolder
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

    fancy_name = " ".join(
        [enhanced_city_state_name, enhanced_station_code, enhanced_facility_name]
    )
    return fancy_name
