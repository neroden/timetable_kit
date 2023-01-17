# via/station_names.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Utility routines to style VIA station names as HTML or text.

Also routines to move from stop_id to and from station_code, and get station names.

Also accessibility info.

Exported:
get_station_name_pretty
stop_id_to_stop_code
stop_code_to_stop_id

station_has_accessible_platform
station_has_inaccessible_platform
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
stop_code_to_stop_name_dict = None

# And the accessibilty dicts
accessible_platform_dict = None
inaccessible_platform_dict = None


def _prepare_dicts():
    """
    Prepare the dicts for:
    stop_code_to_stop_id
    stop_id_to_stop_code
    stop_code_to_stop_name
    accessible_platform_dict
    inaccessible_platform_dict

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
    stop_names = feed.stops["stop_name"].to_list()

    global stop_code_to_stop_id_dict
    global stop_id_to_stop_code_dict
    global stop_code_to_stop_name_dict
    stop_code_to_stop_id_dict = dict(zip(stop_codes, stop_ids))
    stop_id_to_stop_code_dict = dict(zip(stop_ids, stop_codes))
    stop_code_to_stop_name_dict = dict(zip(stop_codes, stop_names))

    # OK.  Now wheelchair boarding.
    # First check for parent_station.
    # If this exists we need to do special stuff, which we have not implemented.
    # VIA Rail does not have stops with parents.
    # FIXME Warning! This depends on retaining the NaN blanks in the GTFS data.
    stops_with_parents = feed.stops.dropna(subset=["parent_station"])
    if not stops_with_parents.empty:
        print(
            "Stops with parents found -- this invalidates wheelchair access detection. Aborting."
        )
        print(stops_with_parents)
        exit(1)

    # We interpret wheelchair_boarding with strict accuracy.
    # 0 or blank == unknown
    # 1 == accessible, for at least some services
    # 2 == inaccessible
    # gtfs_cleanup.py will correctly turn blanks into 0s for us, so don't need to worry about blanks.
    # We simply assume the wheelchair_access column exists, since it does for VIA Rail.
    stop_wheelchair_boarding_list = feed.stops["wheelchair_boarding"].to_list()
    stop_can_board_list = [bool(x == 1) for x in stop_wheelchair_boarding_list]
    stop_cannot_board_list = [bool(x == 2) for x in stop_wheelchair_boarding_list]
    global accessible_platform_dict
    global inaccessible_platform_dict
    accessible_platform_dict = dict(zip(stop_codes, stop_can_board_list))
    inaccessible_platform_dict = dict(zip(stop_codes, stop_cannot_board_list))

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


def stop_code_to_stop_name(stop_code: str) -> str:
    """Given a VIA stop_code, return a VIA stop_name -- raw"""
    # Memoized
    global stop_code_to_stop_name_dict
    if stop_code_to_stop_name_dict == None:
        _prepare_dicts()
    return stop_code_to_stop_name_dict[stop_code]


def get_station_name_pretty(
    station_code: str, doing_multiline_text=False, doing_html=False
) -> str:
    """Given a VIA stop_code, return a suitable station name for plaintext, multiline text, or HTML"""

    # First, get the raw station name: Memoized
    stop_name_raw = stop_code_to_stop_name(station_code)
    # Is it major?
    major = is_standard_major_station(station_code)

    # Default to no facility name
    facility_name = None
    # Default to no connections from the name (this is unused)
    connections_from_name = []

    # Several stations have (EXO) in parentheses: one has (exo).  Get rid of this.
    # Some have GO Bus or GO as suffixes.  Get rid of this.
    # Clarify the confusing Niagara Falls situation.
    # This can be used to autogenerate connecting data, but isn't currently.  TODO
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

    if stop_name_clean == "Sainte-Foy":
        # Explain where St. Foy station is
        facility_name = "for Quebéc City"
    elif stop_name_clean == "Quebéc":
        # Distinguish from other Quebec City stations
        facility_name = "Gare du Palais"
    elif stop_name_clean in ["Montreal", "Montréal"]:  # remember accented e
        # Two stations here too
        facility_name = "Central Station"
    elif stop_name_clean in ["Anjou", "Sauvé"]:  # remember accented e
        # On the Senneterre timetable,
        # "EXO station" blows out a line which we need for Montreal
        facility_name = ""
    elif stop_name_clean == "Toronto":
        # Just for clarity
        facility_name = "Union Station"
    elif stop_name_clean == "Vancouver":
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


def station_has_inaccessible_platform(station_code: str) -> bool:
    """
    Does the station explicitly have an inaccessible platform?

    This excludes stations which don't say either way.

    Constructs and caches the data on first call.

    From GTFS data.
    """
    if inaccessible_platform_dict is None:
        _prepare_dicts()
    return inaccessible_platform_dict[station_code]


def station_has_accessible_platform(station_code: str) -> bool:
    """
    Does this station explicitly have an accessible platform?

    This excludes stations which don't say either way.

    Constructs and caches the data on first call.

    From GTFS data.
    """
    if accessible_platform_dict is None:
        _prepare_dicts()
    return accessible_platform_dict[station_code]


### TESTING
if __name__ == "__main__":
    import timetable_kit

    set_debug_level(2)
    print(
        "Toronto stop id is:",
        timetable_kit.via.station_names.stop_code_to_stop_id("TRTO"),
    )
