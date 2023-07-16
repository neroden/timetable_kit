# hartford_line/__init.py__
# Init file for maple_leaf subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.maple_leaf module

Maple Leaf specific functions for timetable_kit.

This defines an interface; each agency needs to provide the same interface
"""

# Hartford Line leans on Amtrak functions, but this does not work
# import timetable_kit.amtrak as amtrak

# Published agency name
published_name = "Amtrak and VIA Rail"
published_names_or = "Amtrak or VIA Rail"
published_names_and = "Amtrak and VIA Rail"
# Published agency website, for printing.
# Does not include the https:// and should be capitalized for print.
published_website = "Amtrak.com"

# CSS class for special modifications to the output.
# Currently only used to change the header bar color.
css_class = "amtrak-special-css"

# Where to find the GTFS (merged GTFS)
from .merge_gtfs import (
    gtfs_unzipped_local_path,
)

# Published URL for the GTFS.... um.  Use Amtrak for now
# Need to redo the templates to allow multiples
published_gtfs_url = (
    "https://www.transit.land/feeds/f-9-amtrak~amtrakcalifornia~amtrakcharteredvehicle"
)


# These are do-nothings for Amtrak and Hartford Line, but
# quite significant for VIA Rail
def stop_code_to_stop_id(stop_code: str) -> str:
    return stop_code


def stop_id_to_stop_code(stop_id: str) -> str:
    return stop_id


# Most of the rest of this should be copied from Amtrak

# How to title the routes at the top of the column
from timetable_kit.amtrak.route_names import get_route_name

# Routine to pretty-print a station name
# (including subtitles, connecting agency logos, etc)
# Based on Amtrak's but with subtle differences.
# (Amtrak station DB DOES include Canadian stations)
from .station_names import get_station_name_pretty

# Baggage
from timetable_kit.amtrak.baggage import station_has_checked_baggage
from timetable_kit.amtrak.special_data import train_has_checked_baggage

# Platform accessibility
# (BUT WAIT... Need to use GTFS data for VIA) TODO
from timetable_kit.amtrak.access import (
    station_has_accessible_platform,
    station_has_inaccessible_platform,
)

# Special routine to patch Amtrak's defective GTFS feed
# (VIA does not currently need patches)
from timetable_kit.amtrak.gtfs_patches import patch_feed

# For colorizing columns
from timetable_kit.amtrak.special_data import (
    is_connecting_service,
    is_sleeper_train,
    is_high_speed_train,
)

# For making the key for connecting services (including only those in this timetable)
# This takes a list of stations as an argument
from .connecting_services_data import get_all_connecting_services
