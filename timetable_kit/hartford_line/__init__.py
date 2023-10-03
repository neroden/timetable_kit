# hartford_line/__init.py__
# Init file for hartford_line subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.hartford_line module

Hartford-line-specific functions for timetable_kit.

This defines an interface; each agency needs to provide the same interface
"""

# Hartford Line leans on Amtrak functions, but this does not work
# import timetable_kit.amtrak as amtrak

# Published agency name
published_name = "CTRail Hartford Line"
published_names_and = "CTRail Hartford Line and Amtrak"
# Published agency website, for printing.
# Does not include the https:// and should be capitalized for print.
published_website = "HartfordLine.com"

# CSS class for special modifications to the output.
# Currently only used to change the header bar color.
css_class = "amtrak-special-css"

# Where to find the GTFS (merged GTFS)
from .merge_gtfs import (
    gtfs_unzipped_local_path,
)

# Published URL for the Hartford Line GTFS
from .get_gtfs import (
    published_gtfs_url,
)


# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# Most of the rest of this should be copied from Amtrak

# How to title the routes at the top of the column
from timetable_kit.amtrak.route_names import get_route_name

# Routine to pretty-print a station name
# (including subtitles, connecting agency logos, etc.)
# This needs to be different from Amtrak's.
from .station_names import get_station_name_pretty

# Baggage
from timetable_kit.amtrak.baggage import station_has_checked_baggage
from timetable_kit.amtrak.special_data import train_has_checked_baggage

# For colorizing columns
from timetable_kit.amtrak.special_data import (
    is_connecting_service,
    is_sleeper_train,
    is_high_speed_train,
)

# For making the key for connecting services (including only those in this timetable)
# This takes a list of stations as an argument
from .connecting_services_data import get_all_connecting_services
