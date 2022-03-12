#! /usr/bin/env python3
# feed_enhanced.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module monkey-patches the Feed class from gtfs_kit to add methods.

The additions are primarily filter methods: designed to take a feed and filter
a bunch of data out to make a *smaller* feed which is quicker to do future processing on.
There is also an extraction method to pull out a single trip record from a reduced feed,
with error checking to make sure there's exactly one trip.
"""
import gtfs_kit as gk
from operator import not_  # Needed for bad_service_id filter
from timetable_kit.errors import (
    GTFSError,
    NoTripError,
    TwoTripsError,
    )

def filter_by_dates(self, first_date, last_date):
    """
    Filter the entire feed to remove anything before first_date or after last_date

    Returns a new filtered feed (original feed unchanged)
    Must be in GTFS date format (string of YYYYMMDD)
    - Filters calendar (direct)
    - Filters trips (by service_ids in calendar)
    - FIXME: no other second-layer filtering
    Used for nearly all functions to get timetables effective for a single date
    """
    # N.B. Python's default string lexical compare is fine for GTFS date strings
    new_feed = self.copy()
    # Calendar must stop on or after the first date of the period...
    filtered_calendar = self.calendar[self.calendar.end_date >= first_date]
    # ... and start on or before the last date of the period
    double_filtered_calendar = filtered_calendar[filtered_calendar.start_date <= last_date]
    new_feed.calendar = double_filtered_calendar
    # Now filter trips by the service_ids in the calendar
    service_ids = new_feed.calendar["service_id"].array
    filtered_trips = self.trips[self.trips.service_id.isin(service_ids)]
    new_feed.trips = filtered_trips
    return new_feed

def filter_by_route_ids(self, route_ids):
    """
    Filter the entire feed to include only the specified route_ids (a list)

    Returns a new filtered feed (original feed unchanged)
    - filters routes and trips (direct)
    - filters calendar (by service_ids in trips)
    - FIXME: no other second-layer filtering
    - filtered trips is used for timetable generation
    - filtered routes is not currently used
    - filtered calendar and trips are used in compare_similar_services
    """
    new_feed = self.copy()
    filtered_trips = self.trips[self.trips.route_id.isin(route_ids)]
    new_feed.trips = filtered_trips
    filtered_routes = self.routes[self.routes.route_id.isin(route_ids)]
    new_feed.routes = filtered_routes
    # Now filter the calendar by the service_ids in the trips array
    service_ids = new_feed.trips["service_id"].array
    new_feed.calendar = self.calendar[self.calendar.service_id.isin(service_ids)]
    return new_feed

def filter_by_service_ids(self, service_ids):
    """
    Filter the entire feed to include only the specified service_ids (a list)

    Returns a new filtered feed (original feed unchanged)
    - filters calendar and trips (direct)
    - FIXME: no second-layer filtering
    - filtered calendar is used to extract the days of week for a service in the single trip printer
    - filtered trips is not currently used
    """
    new_feed = self.copy()
    # First the calendar
    new_feed.calendar = self.calendar[self.calendar.service_id.isin(service_ids)]
    # Kill any service_ids not in the (new) calendar.
    service_ids = new_feed.calendar["service_id"].array
    # Then filter the trips.
    new_feed.trips = self.trips[self.trips.service_id.isin(service_ids)]
    return new_feed

def filter_bad_service_ids(self, bad_service_ids):
    """
    Filter the entire feed to remove specified bad service_ids (a list)

    Returns a new filtered feed (original feed unchanged)
    - filters calendar and trips (direct)
    - filtered trips is used to avoid known-bad data
    - filtered calender is not currently used
    """
    new_feed = self.copy()
    # First filter the trips.
    filtered_trips = self.trips[self.trips.service_id.isin(bad_service_ids).apply(not_)]
    new_feed.trips = filtered_trips
    # Then the calendar.  Apologies for the long line!
    filtered_calendar = self.calendar[self.calendar.service_id.isin(bad_service_ids).apply(not_)]
    new_feed.calendar = filtered_calendar
    return new_feed

def filter_remove_one_day_calendars(self):
    """
    Remove all service_ids which are effective for only one day.

    Amtrak has a bad habit of listing one-day calendars in its GTFS.  This isn't really
    what we want for a printed timetable.  Worse, some of them actually overlap with the
    calendars for other dates.  Brute-force the problem by eliminating all of them.
    """
    new_feed = self.copy()
    # First filter the calendar
    filtered_calendar = self.calendar[self.calendar.start_date != self.calendar.end_date]
    new_feed.calendar = filtered_calendar
    # Kill service_ids not in the new calendar
    service_ids = new_feed.calendar["service_id"].array
    # Then filter the trips.
    new_feed.trips = self.trips[self.trips.service_id.isin(service_ids)]
    return new_feed


def filter_by_trip_short_names(self, trip_short_names):
    """
    Filter the entire feed to include only services with the specified trip_short_names (a list)

    Amtrak "trip short name" is in fact an Amtrak train or bus number
    Returns a new filtered feed (original feed unchanged)
    - filters trips (direct)
    - filters stop_times (by trip_ids in trips)
    - FIXME: no other second-layer filtering
    Usually used with one-element list to get a single trip
    - filtered trips is used for retrieving a single trip_id, or a trip record
    - filtered stop_times is used for getting single trip stop times, but requires unique trip_id
    """
    new_feed = self.copy()
    # First filter the trips
    filtered_trips = self.trips[self.trips.trip_short_name.isin(trip_short_names)]
    new_feed.trips = filtered_trips
    # Then filter the stop_times
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    return new_feed

def filter_by_trip_ids(self, trip_ids):
    """
    Filter the entire feed to include only services with the specified trip_ids (a list)

    Returns a new filtered feed (original feed unchanged)
    - filters trips and stop_times (direct)
    - FIXME: no second-layer filtering
    Usually used with one-element list to get a single trip
    """
    new_feed = self.copy()
    # First filter the trips
    filtered_trips = self.trips[self.trips.trip_id.isin(trip_ids)]
    new_feed.trips = filtered_trips
    # Then filter the stop_times
    filtered_stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    new_feed.stop_times = filtered_stop_times
    return new_feed

def get_single_trip(self):
    """
    If this feed contains only one trip, return the trip.

    -- If there's only one trip, return it.
    -- Otherwise throw a suitable error.
    -- Used for checking that we've reduced the trips table enough but not too much.
    """
    num_rows = self.trips.shape[0]
    if (num_rows == 0):
        raise NoTripError("Expected single trip: no trips in filtered trips table", self.trips)
    elif (num_rows > 1):
        # FIXME: important to print this now
        print( self.trips )
        raise TwoTripsError("Expected single trip: too many trips in filtered trips table", self.trips)
    this_trip_today = self.trips.iloc[0]
    return this_trip_today

def get_single_trip_stop_times(self, trip_id):
    """
    Get stop times for a single trip -- sorted into the correct order

    May need improved interface... not clear
    """
    filtered_feed = self.filter_by_trip_ids([trip_id])
    stop_times_1 = filtered_feed.stop_times
    stop_times_2 = stop_times_1.set_index("stop_sequence")
    stop_times_3 = stop_times_2.sort_index()
    return stop_times_3

def get_trip_short_name(self, trip_id):
    """
    Given a trip_id, recover the trip_short_name

    Since trip_ids are supposed to be unique, this should be an easy process.

    Very useful for debugging since trip_short_name is human-meaningful,
    and trip_id isn't.
    """
    my_trips = self.trips[self.trips["trip_id"] == trip_id]
    if (my_trips.shape[0] == 0):
        raise NoTripError("No trip with trip_id ", trip_id)
    elif (my_trips.shape[0] > 1):
        raise TwoTripsError("Multiple trips with trip_id ", trip_id)
    my_trip = my_trips.iloc[0]
    return my_trip.trip_short_name

# Monkey patch starts here
gk.Feed.filter_by_dates = filter_by_dates
gk.Feed.filter_by_route_ids = filter_by_route_ids
gk.Feed.filter_by_service_ids = filter_by_service_ids
gk.Feed.filter_bad_service_ids = filter_bad_service_ids
gk.Feed.filter_remove_one_day_calendars = filter_remove_one_day_calendars
gk.Feed.filter_by_trip_short_names = filter_by_trip_short_names
gk.Feed.filter_by_trip_ids = filter_by_trip_ids
gk.Feed.get_single_trip = get_single_trip
gk.Feed.get_single_trip_stop_times = get_single_trip_stop_times
gk.Feed.get_trip_short_name = get_trip_short_name

# TESTING CODE
if __name__ == "__main__":
    from pathlib import Path

    gtfs_filename="./gtfs-amtrak.zip"
    gtfs_path = Path(gtfs_filename)
    feed = gk.read_feed(gtfs_path, dist_units = "mi")
    print(feed.calendar)
    new_feed = feed.filter_by_dates("20220224","20220224")
    print(new_feed.calendar)
