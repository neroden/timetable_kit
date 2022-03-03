#! /usr/bin/env python3
# gtfs_type_cleanup.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Gtfs_kit is an excellent tool, but it puts practically everything into string types;
this is not always useful for later work.  These subroutines convert certain columns to integers.
"""

# Other people's packages
import pandas as pd
import gtfs_kit as gk

def type_corrected_agency(agency):
    """
    Return copy of agency DataFrame with integer types in appropriate columns.  Sort by agency_id.

    Take raw agency DataFrame, type-correct the agency ID, sort by it.  Can be repeated.
    """
    new_agency = agency.astype({'agency_id': 'int32'})
    new_agency_2 = new_agency.sort_values(by=['agency_id'])
    return new_agency_2

def type_corrected_calendar(calendar):
    """Return copy of calendar DataFrame with integer types in appropriate columns.  Sort by service_id."""
    new_calendar = calendar.astype({'service_id': 'int32',
                                    'monday': 'bool',
                                    'tuesday': 'bool',
                                    'wednesday': 'bool',
                                    'thursday': 'bool',
                                    'friday': 'bool',
                                    'saturday': 'bool',
                                    'sunday': 'bool',
                                    'start_date': 'int32',
                                    'end_date': 'int32'
                                   })
    new_calendar_2 = new_calendar.sort_values(by=['service_id'])
    return new_calendar_2

def type_corrected_routes(routes):
    """Return copy of routes DataFrame with integer types in appropriate columns.  Sort by route_id."""
    new_routes = routes.astype({'route_id': 'int32',
                                'agency_id': 'int32',
                                'route_type': 'int32' # 2 for trains, 3 for buses
                               })
    new_routes_2 = new_routes.sort_values(by=['route_id'])
    return new_routes_2

def type_corrected_stop_times(stop_times):
    """Return copy of stop_times with integer types in appropriate columns.  Sort by trip_id."""
    new_stop_times = stop_times.astype({'trip_id': 'int64',
                                        'stop_sequence': 'int32',
                                        'pickup_type': 'int32', # 1 = dropoff only, 2/3 = flag stop
                                        'drop_off_type': 'int32' # 1 = pickup only, 2/3 = flag stop
                                       })
    new_stop_times_2 = new_stop_times.sort_values(by=['trip_id'])
    return new_stop_times_2

def type_corrected_trips(trips):
    """
    Return copy of trips with integer types in appropriate columns.  Do not sort.

    Note that trip_id must be int64, as it tends to be enormous.
    """
    new_trips = trips.astype({'route_id': 'int32',
                              'service_id':'int32',
                              'trip_id': 'int64',
                              # 'trip_short_name': 'int32', # This is the Amtrak train number.  It is a number, but don't treat it as one.
                              'direction_id': 'int32' # This is 0 for west, 1 for east on the LSL only
                              }) # Note that shape_id does not exist in Amtrak data
    return new_trips

# Fix types on tables: integers where appropriate
def fix(feed):
    """Fixes types on all tables in the feed, in place."""
    new_agency = type_corrected_agency(feed.agency)
    feed.agency = new_agency
    new_calendar = type_corrected_calendar(feed.calendar)
    feed.calendar = new_calendar
    new_routes = type_corrected_routes(feed.routes)
    feed.routes = new_routes
    # Note that stops.txt contains no integers
    new_stop_times = type_corrected_stop_times(feed.stop_times)
    feed.stop_times = new_stop_times
    # Note that I am currently ignoring transfers.txt, which does contain integers
    new_trips = type_corrected_trips(feed.trips)
    feed.trips = new_trips
    return None
