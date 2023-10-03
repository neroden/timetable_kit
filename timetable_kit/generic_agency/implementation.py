# generic_agency/implementation.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
This contains generic code which should be used for agencies which don't have their own subpackages.
"""

import gtfs_kit

gtfs_zip_local_path = None
gtfs_unzipped_local_path = None


def get_route_name(today_feed, route_id) -> str:
    """
    Given today_feed and a route_id, produce a suitable name for a column subheading.
    """
    # Unacceptable stub implementation
    return str(route_id)


def get_station_name_pretty(station_code: str) -> str:
    # Unacceptable stub implementation
    return station_code
