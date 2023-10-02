# generic_agency/__init__.py
# Init file for generic agency subpackage of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.generic_agency subpackage

Functions for a generic agency.
"""


# The Agency class type, for others to inherit from
from .agency import Agency
# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

from . import implementation

from .implementation import gtfs_zip_local_path
from .implementation import gtfs_unzipped_local_path

from .implementation import get_route_name
from .implementation import get_station_name_pretty

from .implementation import station_has_checked_baggage
from .implementation import train_has_checked_baggage

from .implementation import station_has_accessible_platform
from .implementation import station_has_inaccessible_platform

from .implementation import patch_feed

from .implementation import is_connecting_service
from .implementation import is_sleeper_train
