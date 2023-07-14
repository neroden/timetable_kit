#! /usr/bin/env python3
# feed_enhanced.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module monkey-patches the Feed class from gtfs_kit to add methods.

The additions are primarily filter methods: designed to take a feed and filter
a bunch of data out to make a *smaller* feed which is quicker to do future processing on.
There is also an extraction method to pull out a single trip record from a reduced feed,
with error checking to make sure there's exactly one trip.
"""
from operator import not_  # Needed for bad_service_id filter

import gtfs_kit

from timetable_kit.errors import (
    NoTripError,
    TwoTripsError, InputError,
)

"""
gtfs_days is the list of all the days (Monday through Sunday) which form gtfs column headers,
appropriately lowercase for the column headers.
"""
gtfs_days = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


def filter_by_dates(self, first_date, last_date):
    """
    Filter the entire feed to remove anything before first_date or after last_date

    Returns a new filtered feed (original feed unchanged)
    Must be in GTFS date format (string of YYYYMMDD)
    - Filters calendar (direct)
    - Filters trips (by service_ids in calendar)
    - Filters stop_times (by trip_ids in trips)
    - FIXME: no other second-layer filtering
    Used for nearly all functions to get timetables effective for a single date
    """
    # N.B. Python's default string lexical compare is fine for GTFS date strings
    # And they MUST be strings
    new_feed = self.copy()
    # Calendar must stop on or after the first date of the period...
    filtered_calendar = self.calendar[self.calendar.end_date >= first_date]
    # ... and start on or before the last date of the period
    double_filtered_calendar = filtered_calendar[
        filtered_calendar.start_date <= last_date
    ]
    new_feed.calendar = double_filtered_calendar
    # Now filter trips by the service_ids in the calendar
    service_ids = new_feed.calendar["service_id"].array
    new_feed.trips = self.trips[self.trips.service_id.isin(service_ids)]
    # Now filter stop_times by the trip_ids in trips
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    return new_feed


def filter_by_day_of_week(
    self,
    day: str,
):
    """
    Filters the feed to trips which are running on the selected day.
    - Filters calendar (direct)
    - Filters trips (by service_ids in calendar)
    - Filters stop_times (by trip_ids in trips)
    - FIXME: no other second-layer filtering

    I did not want to write this.

    However, certain Amtrak trips have identical train numbers
    but different schedules on weekends vs. weekdays.
    (Specifically:
    79, 80, 1079, 20, 662, 88, 162, 89, 719,
    350, 351, 352, 353, 354, 355,
    6048, 6049, 6089, 6093, 6189, 6193,
    8721, 8722, 8821, 8822, 8748, 8205,
    8010, 8011, 8012, 8013, 8014, 8015, 8033,
    8042, 7203, )
    """
    # This assumes integer types for the day column in the calendar.
    if day not in gtfs_days:
        raise InputError("Expected GTFS day name")

    new_feed = self.copy()
    # This is where we filter the calendar by the value in the day column:
    new_feed.calendar = self.calendar[self.calendar[day] == 1]
    # Now filter trips by the service_ids in the calendar
    service_ids = new_feed.calendar["service_id"].array
    new_feed.trips = self.trips[self.trips.service_id.isin(service_ids)]
    # Now filter stop_times by the trip_ids in trips
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    return new_feed


def filter_by_days_of_week(
    self,
    days: list[str],
):
    """
    Filters the feed to trips which are running on one of the selected days.
    - Filters calendar (direct)
    - Filters trips (by service_ids in calendar)
    - Filters stop_times (by trip_ids in trips)
    - FIXME: no other second-layer filtering
    """
    # This assumes integer types for the day column in the calendar.
    for day in days:
        if day not in gtfs_days:
            raise InputError("Expected GTFS day name")

    new_feed = self.copy()
    # This is where we filter the calendar by the value in the day column.
    # This was easy with one day but is much more complex with multiple days.
    # First we have to create a calendar with an auxiliary column.
    tmp_calendar = self.calendar.copy()
    tmp_calendar["interesting"] = 0
    for day in days:
        tmp_calendar["interesting"] = tmp_calendar["interesting"] + tmp_calendar[day]

    # Filter based on the new column.
    tmp2_calendar = tmp_calendar[tmp_calendar["interesting"] >= 1]
    # Now drop the auxiliary column and use the new calendar.
    new_feed.calendar = tmp2_calendar.drop("interesting", axis="columns")

    # Now filter trips by the service_ids in the calendar
    service_ids = new_feed.calendar["service_id"].array
    new_feed.trips = self.trips[self.trips.service_id.isin(service_ids)]
    # Now filter stop_times by the trip_ids in trips
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    return new_feed


def filter_by_route_ids(self, route_ids):
    """
    Filter the entire feed to include only the specified route_ids (a list)

    Returns a new filtered feed (original feed unchanged)
    - filters routes and trips (direct)
    - filters calendar (by service_ids in trips)
    - filters stop_times (by trip_ids in trips)
    - FIXME: no other second-layer filtering
    - filtered trips is used for timetable generation
    - filtered routes is not currently used
    - filtered calendar, trips, and stop_times are used in compare_similar_services
    """
    new_feed = self.copy()
    new_feed.trips = self.trips[self.trips.route_id.isin(route_ids)]
    new_feed.routes = self.routes[self.routes.route_id.isin(route_ids)]
    # Now filter the calendar by the service_ids in the trips array
    service_ids = new_feed.trips["service_id"].array
    new_feed.calendar = self.calendar[self.calendar.service_id.isin(service_ids)]
    # Now filter the stop_times by the trip_ids in the trips array
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]

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
    - filtered calendar is not currently used
    """
    new_feed = self.copy()
    # First filter the trips.
    new_feed.trips = self.trips[self.trips.service_id.isin(bad_service_ids).apply(not_)]
    # Then the calendar.  Apologies for the long line!
    new_feed.calendar = self.calendar[
        self.calendar.service_id.isin(bad_service_ids).apply(not_)
    ]
    return new_feed


def filter_remove_one_day_calendars(self):
    """
    Remove all service_ids which are effective for only one day.

    Amtrak has a bad habit of listing one-day calendars in its GTFS.  This isn't really
    what we want for a printed timetable.  Worse, some of them actually overlap with the
    calendars for other dates.  Brute-force the problem by eliminating all of them.

    - Filters calendar (direct)
    - Filters trips (by service_ids in calendar)
    - Filters stop_times (by trip_ids in trips)
    - FIXME: no other second-layer filtering
    """
    new_feed = self.copy()
    # First filter the calendar
    new_feed.calendar = self.calendar[
        self.calendar.start_date != self.calendar.end_date
    ]
    # Now filter trips by the service_ids in the calendar
    service_ids = new_feed.calendar["service_id"].array
    new_feed.trips = self.trips[self.trips.service_id.isin(service_ids)]
    # Now filter stop_times by the trip_ids in trips
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    return new_feed


def filter_find_one_day_calendars(self):
    """
    Filter to *only* find service_ids which are effective for only one day.

    Amtrak has a bad habit of listing one-day calendars in its GTFS.  While we're usually
    trying to get rid of them, we might also want to examine them.

    Perhaps most useful for finding individual dates of "odd service".

    - Filters calendar (direct)
    - Filters trips (by service_ids in calendar)
    - Filters stop_times (by trip_ids in trips)
    - FIXME: no other second-layer filtering
    """
    new_feed = self.copy()
    # First filter the calendar
    new_feed.calendar = self.calendar[
        self.calendar.start_date == self.calendar.end_date
    ]
    # Now filter trips by the service_ids in the calendar
    service_ids = new_feed.calendar["service_id"].array
    new_feed.trips = self.trips[self.trips.service_id.isin(service_ids)]
    # Now filter stop_times by the trip_ids in trips
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    return new_feed


def filter_by_trip_short_names(self, trip_short_names):
    """
    Filter the entire feed to include only services with the specified trip_short_names (a list)

    Amtrak "trip short name" is in fact an Amtrak train or bus number
    Returns a new filtered feed (original feed unchanged)
    - filters trips (direct)
    - filters stop_times (by trip_ids in trips)
    - filters calendar (by service_ids in trips)
    - FIXME: no other second-layer filtering
    Often used with one-element list to get a single trip
    - filtered trips is used for retrieving a single trip_id, or a trip record
    - filtered stop_times is used for getting single trip stop times, but requires unique trip_id
    - filtered calendar is used for finding validity dates for a timetable
    Also used to speed up main timetable routine, by filtering irrelevancies out of stop_times.

    This is a pretty slow process.  Don't call it too often!
    """
    new_feed = self.copy()
    # First filter the trips
    new_feed.trips = self.trips[self.trips.trip_short_name.isin(trip_short_names)]
    # Then filter the stop_times
    trip_ids = new_feed.trips["trip_id"].array
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    service_ids = new_feed.trips["service_id"].array
    new_feed.calendar = self.calendar[self.calendar.service_id.isin(service_ids)]
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
    new_feed.trips = self.trips[self.trips.trip_id.isin(trip_ids)]
    # Then filter the stop_times
    new_feed.stop_times = self.stop_times[self.stop_times.trip_id.isin(trip_ids)]
    return new_feed


def get_single_trip(self):
    """
    If this feed contains only one trip, return the trip.

    -- If there's only one trip, return it.
    -- Otherwise throw a suitable error.
    -- Used for checking that we've reduced the trips table enough but not too much.
    """
    num_rows = self.trips.shape[0]
    if num_rows == 0:
        raise NoTripError(
            "Expected single trip: no trips in filtered trips table", self.trips
        )
    if num_rows > 1:
        # FIXME: important to print this now
        print(self.trips)
        raise TwoTripsError(
            "Expected single trip: too many trips in filtered trips table", self.trips
        )
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
    if my_trips.shape[0] == 0:
        raise NoTripError("No trip with trip_id ", trip_id)
    if my_trips.shape[0] > 1:
        raise TwoTripsError("Multiple trips with trip_id ", trip_id)
    my_trip = my_trips.iloc[0]
    return my_trip.trip_short_name


# Monkey patch starts here
gtfs_kit.Feed.filter_by_dates = filter_by_dates
gtfs_kit.Feed.filter_by_day_of_week = filter_by_day_of_week
gtfs_kit.Feed.filter_by_days_of_week = filter_by_days_of_week
gtfs_kit.Feed.filter_by_route_ids = filter_by_route_ids
gtfs_kit.Feed.filter_by_service_ids = filter_by_service_ids
gtfs_kit.Feed.filter_bad_service_ids = filter_bad_service_ids
gtfs_kit.Feed.filter_remove_one_day_calendars = filter_remove_one_day_calendars
gtfs_kit.Feed.filter_find_one_day_calendars = filter_find_one_day_calendars
gtfs_kit.Feed.filter_by_trip_short_names = filter_by_trip_short_names
gtfs_kit.Feed.filter_by_trip_ids = filter_by_trip_ids
gtfs_kit.Feed.get_single_trip = get_single_trip
gtfs_kit.Feed.get_single_trip_stop_times = get_single_trip_stop_times
gtfs_kit.Feed.get_trip_short_name = get_trip_short_name

# TESTING CODE
if __name__ == "__main__":
    from pathlib import Path

    gtfs_filename = "./amtrak/GTFS.zip"
    gtfs_path = Path(gtfs_filename)
    feed = gtfs_kit.read_feed(gtfs_path, dist_units="mi")
    print(feed.calendar)
    date_filtered_feed = feed.filter_by_dates("20220224", "20220224")
    print(date_filtered_feed.calendar)
