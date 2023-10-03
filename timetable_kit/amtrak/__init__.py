# amtrak/__init.py__
# Init file for amtrak subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.amtrak module

Amtrak-specific functions for timetable_kit.

This defines an interface; VIA rail and others need to provide the same interface.
"""

# For inheritance (e.g. by Maple Leaf or Hartford Line)
from .agency import AgencyAmtrak

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# Published agency name
published_name = "Amtrak"
published_names_or = "Amtrak"
published_names_and = "Amtrak"
# Published agency website, for printing.
# Does not include the https:// and should be capitalized for print.
published_website = "Amtrak.com"

# CSS class for special modifications to the output.
# Currently only used to change the header bar color.
css_class = "amtrak-special-css"


# This is a temporary testing hack
# Later we will call these directly from the singleton
# These are do-nothings for Amtrak, but
# quite significant for VIA Rail
def stop_code_to_stop_id(stop_code: str):
    return get_singleton().stop_code_to_stop_id(stop_code)


def stop_id_to_stop_code(stop_id: str):
    return get_singleton().stop_id_to_stop_code(stop_id)


# Platform accessibility
def station_has_accessible_platform(station_code: str):
    return get_singleton().station_has_accessible_platform(station_code)


def station_has_inaccessible_platform(station_code: str):
    return get_singleton().station_has_inaccessible_platform(station_code)


# Baggage
from .baggage import station_has_checked_baggage

# For making the key for connecting services (including only those in this timetable)
# This takes a list of stations as an argument
from .connecting_services_data import get_all_connecting_services

# Where to find the GTFS
from .get_gtfs import (
    gtfs_unzipped_local_path,
    published_gtfs_url,
)

# How to title the routes at the top of the column
from .route_names import get_route_name

# For colorizing columns
from .special_data import (
    is_connecting_service,
    is_sleeper_train,
    is_high_speed_train,
)
from .special_data import train_has_checked_baggage

# Routine to pretty-print a station name
# (including subtitles, connecting agency logos, etc.)
from .station_names import get_station_name_pretty
