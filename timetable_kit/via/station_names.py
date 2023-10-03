# via/station_names.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style VIA station names as HTML or text.

Subroutine of get_station_name_pretty
"""
from __future__ import annotations


def _fix_name_and_facility(
    stop_name_raw: str, facility_name: Optional[str]
) -> Tuple[str, Optional[str]]:
    """
    Fix situations where the stop name contains facility info.

    Returns (name, facility)
    """
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

    return (stop_name_clean, facility_name)
