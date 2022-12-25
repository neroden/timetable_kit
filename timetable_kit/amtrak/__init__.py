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

# Trying this, not sure about it
from .get_gtfs import gtfs_zip_local_path
from .get_gtfs import gtfs_unzipped_local_path

# Primary exported methods
from .route_names import get_route_name
from .json_stations import get_station_name
from .special_data import is_standard_major_station  # Stations to capitalize

# Baggage
from .baggage import station_has_checked_baggage
from .special_data import train_has_checked_baggage

# Platform accessibility
from .access import (
    station_has_accessible_platform,
    station_has_inaccessible_platform,
)

# Station name munging routines:
# Attempt to import under a simplified name
# These will always become prettyprint_station_name in the main routine
from .station_name_styling import amtrak_station_name_to_html as station_name_to_html
from .station_name_styling import (
    amtrak_station_name_to_multiline_text as station_name_to_multiline_text,
)
from .station_name_styling import (
    amtrak_station_name_to_single_line_text as station_name_to_single_line_text,
)

# Special routine to patch Amtrak's defective GTFS feed
from .gtfs_cleanup import patch_feed

# For colorizing columns
from .special_data import is_connecting_service  # Highlight in different color
from .special_data import is_sleeper_train  # Different color, ideally icon
