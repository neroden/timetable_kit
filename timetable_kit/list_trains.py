#! /usr/bin/env python3
# list_trains.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Two modes of invocation ./list_trains STATION: Find all the trains (& buses, etc.)
which stop at STATION.

./list_trains STATION_A STATION_B: Find all the trains (& buses, etc.) from station A to
station B (by all routes).

Sort by departure time. Filter by reference date. Optionally filter by day of week.
"""

import argparse
import sys  # for exit

from timetable_kit import runtime_config  # for the agency()
from timetable_kit.debug import debug_print, set_debug_level
from timetable_kit.feed_enhanced import FeedEnhanced
from timetable_kit.initialize import filter_feed_for_utilities
from timetable_kit.initialize import initialize_feed
from timetable_kit.runtime_config import agency  # for the agency()
from timetable_kit.runtime_config import agency_singleton

# Common arguments for the command line
from timetable_kit.timetable_argparse import (
    add_date_argument,
    add_day_argument,
    add_debug_argument,
    add_agency_argument,
    add_gtfs_argument,
)
from timetable_kit.tsn import make_trip_id_to_tsn_dict
from timetable_kit.tsn import stations_list_from_tsn


def get_trips_at(stop_id: str, *, feed: FeedEnhanced) -> list[str]:
    """Returns a list of trip_ids which stop at the chosen stop.

    Preferably, use a feed restricted to a single day (today_feed).  Not required
    though.

    Must be passed a feed, and one stop_id.
    """
    assert feed.stop_times is not None  # Silence MyPy
    # Start by filtering the stop_times for this stop.
    filtered_stop_times = feed.stop_times[feed.stop_times.stop_id == stop_id]
    # FIXME -- do we need to sort here?
    sorted_filtered_stop_times = filtered_stop_times.sort_values(by=["departure_time"])
    trip_ids = sorted_filtered_stop_times["trip_id"].to_list()
    return trip_ids


def get_trips_between(
    stop_one_id: str, stop_two_id: str, *, feed: FeedEnhanced
) -> list[str]:
    """Returns a list of trip_ids which stop at both stops, in that order.

    Preferably, use a feed restricted to a single day (today_feed).  Not required
    though.

    Must be passed a feed, and two stop_ids.
    """
    assert feed.stop_times is not None  # Silence MyPy
    # Start by filtering the stop_times for stop one.
    filtered_stop_times_one = feed.stop_times[feed.stop_times.stop_id == stop_one_id]
    # FIXME -- do we need to sort here?
    # This is a bit tricky: attempt to maintain sorting order
    sorted_filtered_stop_times_one = filtered_stop_times_one.sort_values(
        by=["departure_time"]
    )
    debug_print(2, sorted_filtered_stop_times_one)

    # Now make a dict from trip_id to stop_sequence.
    # Since we've filtered by stop_id, this should be unique.
    trip_ids_one = sorted_filtered_stop_times_one["trip_id"].to_list()
    stop_sequences_one = sorted_filtered_stop_times_one["stop_sequence"].to_list()
    trip_id_to_stop_sequence_one = dict(zip(trip_ids_one, stop_sequences_one))

    # Now for stop two.
    filtered_stop_times_two = feed.stop_times[feed.stop_times.stop_id == stop_two_id]
    # And make another dict.
    trip_ids_two = filtered_stop_times_two["trip_id"].to_list()
    stop_sequences_two = filtered_stop_times_two["stop_sequence"].to_list()
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
    return trip_ids_both


def sort_by_time_at_stop(
    trip_id_list: list[str],
    stop_id: str,
    *,
    feed: FeedEnhanced,
) -> list[str]:
    """Sort a list of trip_ids by departure time at a particular stop.

    Any trip_ids which do not stop at that stop are put last.
    """
    assert feed.stop_times is not None  # Silence MyPy
    # Start by filtering the stop_times for the specified stop.
    filtered_stop_times = feed.stop_times[feed.stop_times.stop_id == stop_id]
    # Filter again for the trip_ids.
    filtered_stop_times = filtered_stop_times[
        filtered_stop_times.trip_id.isin(trip_id_list)
    ]
    # Note that GTFS requires departure_time even for the last stop.
    sorted_filtered_stop_times = filtered_stop_times.sort_values(by=["departure_time"])
    sorted_trip_ids = sorted_filtered_stop_times["trip_id"].to_list()

    # Catch the ones which didn't stop at this stop and add them to the end.
    # Include duplicates.
    extra_trip_ids = []
    for x in trip_id_list:
        if x not in sorted_trip_ids:
            extra_trip_ids.append(x)
    sorted_trip_ids.extend(extra_trip_ids)

    return sorted_trip_ids


def report_dupes(tsn_list: list[str]):
    """Report duplicates in a list of tsns."""
    seen = set()
    dupes = []
    for tsn in tsn_list:
        if tsn not in seen:
            seen.add(tsn)
        else:
            # Note, if it appears three times, it'll be added to "dupes" twice
            dupes.append(tsn)
    if dupes:
        print("Warning, some tsns appear more than once:", dupes)


def make_argparser():
    parser = argparse.ArgumentParser(
        description="""
                    With ONE argument, produce list of trains/buses (trip_short_name) which stop at that stop.
                    Useful for finding all the connecting buses at FLG.

                    With TWO arguments, produce list of trains/buses (trip_short_name) which stop at the first stop, and later at the last stop.
                    Useful for making sure you found all the trains from NYP to PHL.

                    FOUR or a larger even number of arguments will be treated as a list of pairs,
                    so BOS NYP NYP PHL will get the trains from BOS to NYP and the trains from NYP to PHL.

                    In either case, results are sorted by departure time at the first stop.

                    The output should always be reviewed manually before generating tt-spec, especially for days-of-week issues.
                    """,
    )
    add_agency_argument(parser)
    add_gtfs_argument(parser)
    add_date_argument(parser)
    add_day_argument(parser)
    add_debug_argument(parser)
    parser.add_argument(
        "stops",
        help="""List of stops: either 1 stop (everything stopping at A),
                two stops (everything going from A to B),
                or a larger even number of stops (everything going from A to B or from C to D).
             """,
        nargs="*",
    )
    parser.add_argument(
        "--sort",
        help="""
             Sort the trains by their departure time at this stop code.
             Trains not stopping at this stop code will be listed last.
             Note that multi-day trains may be listed after other trains.
             """,
        type=str,
        dest="sync_stop",
    )
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

    runtime_config.set_agency(args.agency)

    if args.gtfs_filename:
        gtfs_filename = args.gtfs_filename
    else:
        # Default to agency
        gtfs_filename = agency().gtfs_unzipped_local_path

    # Initialize the feed & the singleton.
    master_feed = initialize_feed(gtfs=gtfs_filename)

    today_feed = filter_feed_for_utilities(
        master_feed, reference_date=args.reference_date, day_of_week=args.day
    )

    stops = args.stops
    sync_stop = args.sync_stop

    # Make the two interconverting dicts -- we only need one
    trip_id_to_tsn = make_trip_id_to_tsn_dict(today_feed)
    # tsn_to_trip_id = make_tsn_to_trip_id_dict(today_feed)

    if not stops:
        argparser.print_usage()
        print("Error: Must specify at least one stop.")
        sys.exit(1)
    if len(stops) == 1:
        stop = stops[0]
        print("Finding trips which stop at", stop)
        # Have to convert from stop_code to stop_id for VIA (no-op for Amtrak)
        stop_id = agency_singleton().stop_code_to_stop_id(stop)
        trip_ids = get_trips_at(stop_id, feed=today_feed)
        tsns = [trip_id_to_tsn[trip_id] for trip_id in trip_ids]
    elif len(stops) % 2 != 0:
        # Odd number of stops
        argparser.print_usage()
        print("Error: Must either specify one stop or an even number of stops.")
        sys.exit(1)
    else:
        # Turn list of stops into list of pairs of stops
        pairs = zip(stops[::2], stops[1::2])
        # Start with a blank list of tsns
        trip_ids = []
        for stop_one, stop_two in pairs:
            print("Finding trips from", stop_one, "to", stop_two)
            # Have to convert from stop_code to stop_id for VIA (no-op for Amtrak)
            stop_one_id = agency_singleton().stop_code_to_stop_id(stop_one)
            stop_two_id = agency_singleton().stop_code_to_stop_id(stop_two)
            this_pair_trip_ids = get_trips_between(
                stop_one_id, stop_two_id, feed=today_feed
            )

            # Report duplicates.  Important for catching GTFS weirdness.
            # We expect duplicates if we've entered multiple pairs, so only report dupes
            # if they occurred from a single pair.
            this_pair_tsns = [trip_id_to_tsn[trip_id] for trip_id in trip_ids]
            report_dupes(this_pair_tsns)

            # Now add to the master list
            trip_ids.extend(this_pair_trip_ids)

    # We have a list of trip_ids.
    if sync_stop:
        # Remove duplicates.  (FIXME: do in non-sorting case too?)
        trip_ids = list(set(trip_ids))
        # Sort.
        sync_stop_id = agency_singleton().stop_code_to_stop_id(sync_stop)
        sorted_trip_ids = sort_by_time_at_stop(trip_ids, sync_stop_id, feed=today_feed)
    else:
        sorted_trip_ids = trip_ids

    # Convert to tsns.  Note that duplicate TSNs can appear here (with different trip_ids),
    # And we definitely want the user to know about this, so leave those duplicates.
    sorted_tsns = [trip_id_to_tsn[trip_id] for trip_id in sorted_trip_ids]

    # Report the results!
    print("Trains found:", sorted_tsns)

    if args.extent:
        # We want to print first and last stops for each.
        for tsn in tsns:
            station_list_df = stations_list_from_tsn(today_feed, tsn)
            first_station = station_list_df.head(1).item()
            last_station = station_list_df.tail(1).item()
            print(tsn, first_station, last_station, sep="\t")
