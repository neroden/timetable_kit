#! /usr/bin/env python3
# find_connecting_buses.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Find all the connecting bus routes which connect to a named station, or a list of stations.

Sort by departure time.
Optionally filter by day of week.
Definitely filter by reference date.
"""

import argparse
import datetime

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


def find_connecting_buses_from_stop(stop, *, feed, trip_id_to_tsn):
    """
    Returns a list of trip_short_names (train numbers) which stop at both stops.

    Preferably, use a feed restricted to a single day (today_feed).  Not required though.

    Requires a trip_id_to_tsn map (dict).

    Consider returning trip_ids instead. FIXME
    Must be passed a feed, and one stop_id.
    """
    # Start by filtering the stop_times for stop one.
    filtered_stop_times = feed.stop_times[feed.stop_times.stop_id == stop]
    trip_ids = filtered_stop_times["trip_id"].array
    tsns = [trip_id_to_tsn[trip_id] for trip_id in trip_ids]

    # Should still be in the correct order
    print("Found trips at", stop, " : ", tsns)
    return tsns


def make_argparser():
    parser = argparse.ArgumentParser(
        description="""Produce list of bus & train trips (trip_short_name) touching a stop or list of stops.
                        Useful for finding the connecting services for a route.
                    """,
    )
    add_gtfs_argument(parser)
    add_date_argument(parser)
    add_debug_argument(parser)
    parser.add_argument(
        "stops",
        help="""Stop or stops""",
        nargs="+",  # 1 or more stop
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
    if reference_date is None:
        reference_date = datetime.date.today().strftime("%Y%m%d")
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")
    today_feed = master_feed.filter_by_dates(reference_date, reference_date)

    stops = args.stops

    # Make the two interconverting dicts
    trip_id_to_tsn = make_trip_id_to_tsn_dict(master_feed)
    # tsn_to_trip_id = make_tsn_to_trip_id_dict(today_monday_feed)
    for stop in stops:
        find_connecting_buses_from_stop(
            stop, feed=today_feed, trip_id_to_tsn=trip_id_to_tsn
        )
