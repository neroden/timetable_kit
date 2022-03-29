# antrak/__init.py__
# Init file for amtrak submodule of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

# I'll be quite honest; I don't know what I'm doing here.
# This seems to work to allow the parent package to say
#   import timetable_kit.amtrak
# and then use
#   amtrak.special_data.whatever
# later on.  This doesn't seem to work without these lines.
from . import (
    agency_cleanup,
    special_data,
    station_name_styling,
    json_stations, # this is the big one
    )

# Trying this, not sure about it
from .get_gtfs import gtfs_zip_local_path
from .get_gtfs import gtfs_unzipped_local_path

# Primary exported methods
from .baggage import station_has_checked_baggage
from .special_data import train_has_checked_baggage
from .json_stations import get_station_name
from .route_names import get_route_name
from .access import (station_has_accessible_platform,
    station_has_inaccessible_platform, )
