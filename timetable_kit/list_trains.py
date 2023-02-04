#! /usr/bin/env python3
# list_trains.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Two modes of invocation
./list_trains STATION:
Find all the trains (& buses, etc.) which stop at STATION.

./list_trains STATION_A STATION_B:
Find all the trains (& buses, etc.) from station A to station B (by all routes).

Sort by departure time.
Filter by reference date.
Optionally filter by day of week.
"""

import sys  # for exit
import argparse
import datetime

import gtfs_kit

# Monkey-patch the feed class
from timetable_kit import feed_enhanced
from feed_enhanced import gtfs_days

from timetable_kit.initialize import initialize_feed
from timetable_kit.initialize import filter_feed_for_utilities

from timetable_kit.debug import debug_print, set_debug_level
from timetable_kit.tsn import make_trip_id_to_tsn_dict
from timetable_kit.tsn import stations_list_from_tsn

# Common arguments for the command line
from timetable_kit.timetable_argparse import (
    add_date_argument,
    add_day_argument,
    add_debug_argument,
    add_agency_argument,
    add_gtfs_argument,
)

from timetable_kit import runtime_config  # for the agency()
from timetable_kit.runtime_config import agency  # for the agency()


def get_trips_at(
    stop_one_id: str, *, feed: gtfs_kit.Feed, trip_id_to_tsn: dict
) -> list[str]:
    """
    Returns a list of trip_short_names (train numbers) which stop at the chosen stop.

    Preferably, use a feed restricted to a single day (today_feed).  Not required though.

    Requires a trip_id_to_tsn map (dict).

    Consider returning trip_ids instead. FIXME
    Must be passed a feed, and one stop_id.
    """
    # Start by filtering the stop_times for stop one.
    filtered_stop_times = feed.stop_times[feed.stop_times.stop_id == stop_one_id]
    sorted_filtered_stop_times = filtered_stop_times.sort_values(by=["departure_time"])
    trip_ids = sorted_filtered_stop_times["trip_id"].array
    tsns = [trip_id_to_tsn[trip_id] for trip_id in trip_ids]

    # Should still be in the correct order
    print("Found trips at", agency().stop_id_to_stop_code(stop_one_id), " : ", tsns)
    return tsns


def get_trips_between(
    stop_one_id: str, stop_two_id: str, *, feed: gtfs_kit.Feed, trip_id_to_tsn: dict
) -> list[str]:
    """
    Returns a list of trip_short_names (train numbers) which stop at both stops, in that order.

    Preferably, use a feed restricted to a single day (today_feed).  Not required though.

    Requires a trip_id_to_tsn map (dict).

    Consider returning trip_ids instead. FIXME
    Must be passed a feed, and two stop_ids.
    """
    # Start by filtering the stop_times for stop one.
    filtered_stop_times_one = feed.stop_times[feed.stop_times.stop_id == stop_one_id]
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
    filtered_stop_times_two = feed.stop_times[feed.stop_times.stop_id == stop_two_id]
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
        description="""
                    With ONE argument, produce list of trains/buses (trip_short_name) which stop at that stop.
                    Useful for finding all the connecting buses at FLG.

                    With TWO arguments, produce list of trains/buses (trip_short_name) which stop at the first stop, and later at the last stop.
                    Useful for making sure you found all the trains from NYP to PHL.

                    In either case, results are sorted by departure time at the first stop.

                    The output should always be reviewed manually before generating tt-spec, especially for days-of-week issues.
                    """,
    )
    add_date_argument(parser)
    add_debug_argument(parser)
    add_agency_argument(parser)
    add_gtfs_argument(parser)
    parser.add_argument(
        "stop_one",
        help="""First stop""",
    )
    parser.add_argument(
        "stop_two",
        help="""Last stop""",
        nargs="?",
    )
    add_day_argument(parser)
    parser.add_argument(
        "--extent",
        help="""Display first and last stations for each trip""",
        action="store_true",
    )
    return parser


# MAIN PROGRAM
if __name__ == "__main__":
    argparser = make_argparser()
    args = argparser.parse_args()

    set_debug_level(args.debug)

    # Eventually this will be set from the command line -- FIXME
    debug_print(2, "Agency found:", args.agency)
    runtime_config.set_agency(args.agency)

    if args.gtfs_filename:
        gtfs_filename = args.gtfs_filename
    else:
        # Default to agency
        gtfs_filename = agency().gtfs_unzipped_local_path

    master_feed = initialize_feed(gtfs=gtfs_filename)

    today_feed = filter_feed_for_utilities(
        master_feed, reference_date=args.reference_date, day_of_week=args.day
    )

    # Make the two interconverting dicts -- actually we only need one of them
    trip_id_to_tsn = make_trip_id_to_tsn_dict(master_feed)
    # tsn_to_trip_id = make_tsn_to_trip_id_dict(today_monday_feed)

    stop_one = args.stop_one
    stop_two = args.stop_two

    if stop_one is None:
        argparser.print_usage()
        sys.exit(1)
    if stop_two is None:
        print("Finding trips which stop at", stop_one)
        # Have to convert from stop_code to stop_id for VIA (no-op for Amtrak)
        stop_one_id = agency().stop_code_to_stop_id(stop_one)
        tsns = get_trips_at(stop_one_id, feed=today_feed, trip_id_to_tsn=trip_id_to_tsn)
    else:
        print("Finding trips from", stop_one, "to", stop_two)
        # Have to convert from stop_code to stop_id for VIA (no-op for Amtrak)
        stop_one_id = agency().stop_code_to_stop_id(stop_one)
        stop_two_id = agency().stop_code_to_stop_id(stop_two)
        tsns = get_trips_between(
            stop_one_id, stop_two_id, feed=today_feed, trip_id_to_tsn=trip_id_to_tsn
        )

    # Report the duplicates
    seen = set()
    dupes = []
    for tsn in tsns:
        if tsn not in seen:
            seen.add(tsn)
        else:
            # Note, if it appears three times, it'll be added to "dupes" twice
            dupes.append(tsn)
    if dupes:
        print("Warning, some tsns appear more than once:", dupes)

    if args.extent:
        # We want to print first and last stops for each.
        for tsn in tsns:
            station_list_df = stations_list_from_tsn(today_feed, tsn)
            first_station = station_list_df.head(1).item()
            last_station = station_list_df.tail(1).item()
            print(tsn, first_station, last_station, sep="\t")
