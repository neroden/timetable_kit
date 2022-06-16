# antrak/__init.py__
# Init file for amtrak submodule of timetable_kit
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

# Trying this, not sure about it
from .get_gtfs import gtfs_zip_local_path
from .get_gtfs import gtfs_unzipped_local_path

# Primary exported methods
from .baggage import station_has_checked_baggage
from .special_data import train_has_checked_baggage
from .json_stations import get_station_name
from .route_names import get_route_name
from .access import (
    station_has_accessible_platform,
    station_has_inaccessible_platform,
)

# Special routine to patch Amtrak's defective GTFS feed
from .gtfs_cleanup import patch_feed

# Attempt to import under a simplified name
from .station_name_styling import amtrak_station_name_to_html as station_name_to_html
from .station_name_styling import (
    amtrak_station_name_to_multiline_text as station_name_to_multiline_text,
)
from .station_name_styling import (
    amtrak_station_name_to_single_line_text as station_name_to_single_line_text,
)
