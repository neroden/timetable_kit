#! /usr/bin/env python3
# make_spec.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Prepare a spec file -- MUST BE CHECKED MANUALLY !!!!

Takes the same arguments as list_trains.py, PLUS --trip like list_stations.py
"""

import argparse
import sys  # for exit

import pandas as pd

from timetable_kit import runtime_config  # for the agency()
from timetable_kit.debug import set_debug_level
from timetable_kit.initialize import filter_feed_for_utilities
from timetable_kit.initialize import initialize_feed
from timetable_kit.list_trains import (
    get_trips_between,
    report_dupes,
    sort_by_time_at_stop,
)
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
from timetable_kit.tsn import (
    make_trip_id_to_tsn_dict,
    stations_list_from_tsn,
)


def make_argparser():
    parser = argparse.ArgumentParser(
        description="""
                    With TWO arguments, produce list of trains/buses (trip_short_name) which stop at the first stop, and later at the last stop.
                    Useful for making sure you found all the trains from NYP to PHL.

                    FOUR or a larger even number of arguments will be treated as a list of pairs,
                    so BOS NYP NYP PHL will get the trains from BOS to NYP and the trains from NYP to PHL.

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
        help="""List of stops: either two stops (everything going from A to B),
                or a larger even number of stops (everything going from A to B or from C to D).
             """,
        nargs="*",
    )
    parser.add_argument(
        "--sort",
        help="""Sort the trains by their departure time at this stop code""",
        type=str,
        dest="sync_stop",
        required=True,
    )
    parser.add_argument(
        "--trip",
        dest="trip_short_name",
        help="""This specifies which trip_short_name to use to generate the list of stations.
                For instance, if it's "51", train 51 will be used.
             """,
        required=True,
    )
    return parser


# MAIN PROGRAM
if __name__ == "__main__":
    argparser = make_argparser()
    args = argparser.parse_args()

    # Silence debugging...
    set_debug_level(0)

    runtime_config.set_agency(args.agency)

    if args.gtfs_filename:
        gtfs_filename = args.gtfs_filename
    else:
        # Default to agency
        gtfs_filename = agency().gtfs_unzipped_local_path

    # Initialize the feed and the singleton.
    master_feed = initialize_feed(gtfs=gtfs_filename)

    today_feed = filter_feed_for_utilities(
        master_feed, reference_date=args.reference_date, day_of_week=args.day
    )

    stops = args.stops
    sync_stop = args.sync_stop

    key_tsn = args.trip_short_name
    key_tsn = key_tsn.strip()  # Avoid whitespace problems

    # Make the two interconverting dicts -- we only need one
    trip_id_to_tsn = make_trip_id_to_tsn_dict(today_feed)
    # tsn_to_trip_id = make_tsn_to_trip_id_dict(today_feed)

    if (not stops) or (len(stops) % 2 != 0):
        # Odd number of stops
        argparser.print_usage()
        print("Error: Must specify an even number of stops.")
        sys.exit(1)
    else:
        # Turn list of stops into list of pairs of stops
        pairs = zip(stops[::2], stops[1::2])
        # Start with a blank list of tsns
        trip_ids = []
        for stop_one, stop_two in pairs:
            # print("Finding trips from", stop_one, "to", stop_two)
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

    tsn_column_headers = ["", "access", "stations", *sorted_tsns]

    # Now pull the station list from key_tsn, in order
    station_list_df = stations_list_from_tsn(today_feed, key_tsn)
    # Prefix the standard options columns
    prefix_list = ["", "column-options", "days", "updown"]
    prefix_df = pd.DataFrame(prefix_list)
    left_column_df = pd.concat([prefix_df, station_list_df])

    # OK.  Create a blank DataFrame: this is the only reasonable way to do this.
    num_cols = len(tsn_column_headers)
    my_df = pd.DataFrame(index=left_column_df.index, columns=range(num_cols))

    # This replaces the top *row*
    my_df.iloc[0] = tsn_column_headers
    # This replaces the left *column*
    my_df[0] = left_column_df[0]
    # This puts the first ardp in place: row 2, column 4
    my_df.iat[1, 3] = "ardp"
    # This fills the days column with the reference station
    days_list = [sync_stop] * len(sorted_tsns)
    days_list = ["days", "", "", *days_list]
    my_df.iloc[2] = days_list
    # Replace NaNs with blank strings
    my_df.fillna("", inplace=True)

    # Now we have to figure out how to dump the DataFrame to CSV.
    result = my_df.to_csv(index=False, header=False)
    print(result)
