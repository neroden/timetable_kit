# via/station_names.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style VIA station names as HTML or text.

Exported:
get_station_name_pretty
"""

from timetable_kit.debug import set_debug_level, debug_print

# The singleton -- for converting stop code to stop name
from timetable_kit.via import get_singleton

# Should the station be boldfaced
from timetable_kit.via.special_data import is_standard_major_station

# Map from station codes to connecting service names (matching those in timetable_kit.connecting_services)
from timetable_kit.via.connecting_services_data import connecting_services_dict

# Find the HTML for a specific connecting agency's logo
from timetable_kit.connecting_services import get_connecting_service_logo_html


def get_station_name_pretty(
    station_code: str, doing_multiline_text=False, doing_html=False
) -> str:
    """Given a VIA stop_code, return a suitable station name for plaintext, multiline text, or HTML"""

    # First, get the raw station name: Memoized
    stop_name_raw = get_singleton().stop_code_to_stop_name(station_code)
    # Is it major?
    major = is_standard_major_station(station_code)

    # Default to no facility name
    facility_name = None
    # Default to no connections from the name (this is unused)
    connections_from_name = []

    # Several stations have (EXO) in parentheses: one has (exo).  Get rid of this.
    # Some have GO Bus or GO as suffixes.  Get rid of this.
    # Clarify the confusing Niagara Falls situation.
    if stop_name_raw.endswith(" (EXO)") or stop_name_raw.endswith(" (exo)"):
        stop_name_clean = stop_name_raw.removesuffix(" (EXO)").removesuffix(" (exo)")
        facility_name = "EXO station"
        connections_from_name.append("exo")
    elif stop_name_raw.endswith(" GO Bus"):
        stop_name_clean = stop_name_raw.removesuffix(" GO Bus")
        facility_name = "GO Bus station"
    elif stop_name_raw.endswith(" GO"):
        stop_name_clean = stop_name_raw.removesuffix(" GO")
        facility_name = "GO station"
        connections_from_name.append("go_transit")
    elif stop_name_raw.endswith(" Bus"):
        stop_name_clean = stop_name_raw.removesuffix(" Bus")
        facility_name = "Bus station"
    elif stop_name_raw == "Niagara Falls Station":
        stop_name_clean = "Niagara Falls, NY"
    elif stop_name_raw == "Niagara Falls":
        stop_name_clean = "Niagara Falls, ON"
    else:
        stop_name_clean = stop_name_raw

    match stop_name_clean:
        case "Sainte-Foy":
            # Explain where St. Foy station is
            facility_name = "for Quebéc City"
        case "Quebéc":
            # Distinguish from other Quebec City stations
            facility_name = "Gare du Palais"
        case "Montreal" | "Montréal":  # remember accented e
            # Two stations here too
            facility_name = "Central Station"
        case "Anjou" | "Sauvé":  # remember accented e
            # On the Senneterre timetable,
            # "EXO station" blows out a line which we need for Montreal
            facility_name = ""
        case "Ottawa":
            # Make it clear which LRT station this goes with
            facility_name = "Tremblay"
        case "Toronto":
            # Just for clarity
            facility_name = "Union Station"
        case "Vancouver":
            # There ARE two train stations in Vancouver
            facility_name = "Pacific Central Station"

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
