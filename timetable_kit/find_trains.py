#! /usr/bin/env python3
# find_trains.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Find all the trains from station A to station B (by all routes).

Sort by departure time.
Optionally filter by day of week.
Definitely filter by reference date.
"""

import argparse

# Monkey-patch the feed class
from timetable_kit import feed_enhanced

from timetable_kit.initialize import initialize_feed

from timetable_kit.debug import debug_print, set_debug_level
from timetable_kit.tsn import make_trip_id_to_tsn_dict

# Common arguments for the command line
from timetable_kit.timetable_argparse import (
    add_gtfs_argument,
    add_date_argument,
    add_debug_argument,
)


def find_trains(stop_one, stop_two, *, feed, trip_id_to_tsn):
    """
    Returns a list of trip_short_names (train numbers) which stop at both stops.

    Preferably, use a feed restricted to a single day (today_feed).  Not required though.

    Requires a trip_id_to_tsn map (dict).

    Consider returning trip_ids instead. FIXME
    Must be passed a feed, and two stop_ids.
    """
    # Start by filtering the stop_times for stop one.
    filtered_stop_times_one = feed.stop_times[feed.stop_times.stop_id == stop_one]
    # This is a bit tricky: attempt to maintain sorting order
    sorted_filtered_stop_times_one = filtered_stop_times_one.sort_values(
        by=["departure_time"]
    )
    debug_print(2, sorted_filtered_stop_times_one)

    # Now make a dict from trip_id to stop_sequence.
    # Since we've filtered by stop_id, this should be unique.
    trip_ids_one = sorted_filtered_stop_times_one["trip_id"].array
    stop_sequences_one = sorted_filtered_stop_times_one["stop_sequence"].array
    trip_id_to_stop_sequence_one = dict(zip(trip_ids_one, stop_sequences_one))

    # Now for stop two.
    filtered_stop_times_two = feed.stop_times[feed.stop_times.stop_id == stop_two]
    # And make another dict.
    trip_ids_two = filtered_stop_times_two["trip_id"].array
    stop_sequences_two = filtered_stop_times_two["stop_sequence"].array
    trip_id_to_stop_sequence_two = dict(zip(trip_ids_two, stop_sequences_two))

    # Since we're using this for intersection, a set is faster
    trip_ids_two_set = set(trip_ids_two)

    # Set method loses order, and it's hard to filter by direction:
    # trip_ids_intersection = trip_ids_one_set & trip_ids_two_set
    # trip_ids_list = list(trip_ids_intersection)

    # Now, include only the trips in both lists, retaining order of list one
    # And only the ones where stop one comes before stop two
    trip_ids_both = []
    for trip_id in trip_ids_one:
        # Stops at the first station...
        if trip_id in trip_ids_two_set:
            # Stops at the second station...
            if (
                trip_id_to_stop_sequence_one[trip_id]
                < trip_id_to_stop_sequence_two[trip_id]
            ):
                # Stops at the first station before the second station...
                trip_ids_both.append(trip_id)

    tsns = [trip_id_to_tsn[trip_id] for trip_id in trip_ids_both]

    # Should still be in the correct order
    print("Found trains: ", tsns)
    return tsns


def make_spec(route_ids, feed):
    """Not ready to use: put to one side for testing purposes"""
    # Creates a prototype timetable.  It will definitely need to be manipulated by hand.
    # Totally incomplete. FIXME
    route_ids = [
        route_id("Illini"),
        route_id("Saluki"),
        route_id("City Of New Orleans"),
    ]

    route_feed = feed.filter_by_route_ids(route_ids)
    today_feed = route_feed.filter_by_dates(reference_date, reference_date)
    # reference_date is currently a global

    print("Allbound:")
    print(today_feed.trips)

    print("Upbound:")
    up_trips = today_feed.trips[today_feed.trips.direction_id == 0]
    print(up_trips)

    print("Downbound:")
    down_trips = today_feed.trips[today_feed.trips.direction_id == 1]
    print(down_trips)


def make_argparser():
    parser = argparse.ArgumentParser(
        description="""Produce list of trains (trip_short_name) from stop one to stop two.
                        Useful for making sure you found all the trains from NYP to PHL.
                        Should be reviewed manually before generating tt-spec, especially for
                        days-of-week issues.
                    """,
    )
    add_gtfs_argument(parser)
    add_date_argument(parser)
    add_debug_argument(parser)
    parser.add_argument(
        "stop_one",
        help="""First stop""",
    )
    parser.add_argument(
        "stop_two",
        help="""Last stop""",
    )
    return parser


# MAIN PROGRAM
if __name__ == "__main__":
    parser = make_argparser()
    args = parser.parse_args()

    set_debug_level(args.debug)

    gtfs_filename = args.gtfs_filename
    master_feed = initialize_feed(gtfs=gtfs_filename)

    reference_date = args.reference_date
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")
    today_feed = master_feed.filter_by_dates(reference_date, reference_date)

    stop_one = args.stop_one
    stop_two = args.stop_two
    print("Finding trains from", stop_one, "to", stop_two)

    # TODO: figure out how to filter by day of week
    # today_monday_feed = today_feed.filter_by_day_of_week(monday==1)
    set_debug_level(2)

    # Make the two interconverting dicts
    trip_id_to_tsn = make_trip_id_to_tsn_dict(master_feed)
    # tsn_to_trip_id = make_tsn_to_trip_id_dict(today_monday_feed)

    find_trains(stop_one, stop_two, feed=today_feed, trip_id_to_tsn=trip_id_to_tsn)
