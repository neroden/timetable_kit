#! /usr/bin/env python3
# list_stations.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
List all the stations for a particular train number (trip_short_name), in order.
"""

import argparse
import os  # For os.getenv
import sys  # For sys.exit

from timetable_kit import runtime_config  # for the agency()
from timetable_kit.debug import debug_print, set_debug_level
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
    add_output_dirname_argument,
)
from timetable_kit.tsn import (
    stations_list_from_tsn,
)


def make_argparser():
    parser = argparse.ArgumentParser(
        description="""Get list of stations visited, in order, for a single train number (trip_short_name).
                       Useful when making tt-specs.
                       Should be reviewed manually before generating tt-spec.
                    """,
    )
    add_date_argument(parser)
    add_day_argument(parser)
    add_debug_argument(parser)
    add_agency_argument(parser)
    add_gtfs_argument(parser)
    add_output_dirname_argument(parser)
    parser.add_argument(
        "--trip",
        dest="trip_short_name",
        help="""This specifies which trip_short_name to use to generate the list of stations.
                For instance, if it's "51", train 51 will be used.
             """,
    )
    parser.add_argument(
        "trip",
        help="""This specifies which trip_short_name to use to generate the list of stations.
                For instance, if it's "51", train 51 will be used.
             """,
        nargs="?",
    )
    parser.add_argument(
        "--csv",
        help="""Produce output suitable for redirecting directly into a CSV file.""",
        action="store_true",
    )
    return parser


if __name__ == "__main__":
    my_arg_parser = make_argparser()
    args = my_arg_parser.parse_args()

    set_debug_level(args.debug)
    if args.csv:
        # No debugging info in output please!
        set_debug_level(0)

    output_dirname = args.output_dirname
    if not output_dirname:
        output_dirname = os.getenv("TIMETABLE_KIT_OUTPUT_DIR")
    if not output_dirname:
        output_dirname = "."

    # Eventually this will be set from the command line -- FIXME
    debug_print(2, "Agency found:", args.agency)
    runtime_config.set_agency(args.agency)

    if args.gtfs_filename:
        gtfs_filename = args.gtfs_filename
    else:
        # Default to agency
        gtfs_filename = agency().gtfs_unzipped_local_path

    master_feed = initialize_feed(gtfs=gtfs_filename)
    # Initialize the agency singleton from the feed.
    agency_singleton().init_from_feed(master_feed)

    today_feed = filter_feed_for_utilities(
        master_feed, reference_date=args.reference_date, day_of_week=args.day
    )

    optional_tsn = args.trip_short_name
    positional_tsn = args.trip
    match (optional_tsn, positional_tsn):
        case (None, None):
            raise ValueError("Can't generate a station list without a specific trip.")
        case (None, tsn) | (tsn, None):
            tsn = tsn.strip()  # Avoid whitespace problems
        case (_, _):
            raise ValueError(
                "Specified trip_short_name two different ways.  Use only one."
            )

    # And pull the station list, in order
    station_list_df = stations_list_from_tsn(today_feed, tsn)
    if not args.csv:
        print(station_list_df)
        sys.exit(0)

    # OK, this is the CSV specific path.
    station_list = station_list_df.to_list()
    station_list_with_commas = [x + ",,," for x in station_list]
    station_list_prefixed = [
        ",access,stations," + str(tsn),
        "column-options,,,ardp",
        "days,,," + station_list[0],
        "updown,,,",
        *station_list_with_commas,
    ]
    station_list_csv = "\n".join(station_list_prefixed)
    print(station_list_csv)
    # Consider dumping to CSV... but don't right now
    # output_filename = "".join([output_dirname, "/", "tt_", tsn, "_", "stations.csv"])
    # station_list_df.to_csv(output_filename, index=False)
    # Note: this will put "stop_id" in top row, which is OK
