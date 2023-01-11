# antrak/__init.py__
# Init file for amtrak subpackage of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

# I'll be quite honest; I don't know what I'm doing here.
# This seems to work to allow the parent package to say
#   import timetable_kit.amtrak
# and then use
#   amtrak.special_data.whatever
# later on.  This doesn't seem to work without these lines.

"""
timetable_kit.amtrak module

Amtrak-specific functions for timetable_kit.
"""
from . import (
    agency_cleanup,
    special_data,
    station_name_styling,
    json_stations,  # this is the big one
)

# Published agency name
published_name = "Amtrak"
# Published agency website, for printing.
# Does not include the https:// and should be capitalized for print.
published_website = "Amtrak.com"

# Where to find the GTFS
from .get_gtfs import gtfs_zip_local_path
from .get_gtfs import gtfs_unzipped_local_path
from .get_gtfs import published_gtfs_url

# How to title the routes at the top of the column
from .route_names import get_route_name

# Routine to pretty-print a station name
# (including subtitles, connecting agency logos, etc)
from .station_name_styling import get_station_name_pretty

# Baggage
from .baggage import station_has_checked_baggage
from .special_data import train_has_checked_baggage

# Platform accessibility
from .access import (
    station_has_accessible_platform,
    station_has_inaccessible_platform,
)

# Special routine to patch Amtrak's defective GTFS feed
from .gtfs_cleanup import patch_feed

# For colorizing columns
from .special_data import is_connecting_service  # Highlight in different color
from .special_data import is_sleeper_train  # Different color, ideally icon

# For making the key for connecting services (including only those in this timetable)
# This takes a list of stations as an argument
from .connecting_services_data import get_all_connecting_services
