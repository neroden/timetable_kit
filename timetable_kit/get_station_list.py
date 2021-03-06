#! /usr/bin/env python3
# get_station_list.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Get all the stations for a particular train number (trip_short_name), in order.
"""

import sys  # For sys.exit
import os  # For os.getenv

import argparse
import datetime

# import pandas as pd # we call pandas routines but only on dataframes

# We may not actually need these directly?
import gtfs_kit

# Monkey-patch the feed class
from timetable_kit import feed_enhanced
from feed_enhanced import gtfs_days

from timetable_kit.initialize import initialize_feed
from timetable_kit import amtrak  # For the path of the default GTFS feed
from timetable_kit.debug import debug_print, set_debug_level

# Common arguments for the command line
from timetable_kit.timetable_argparse import (
    add_gtfs_argument,
    add_date_argument,
    add_debug_argument,
    add_output_dirname_argument,
)

from timetable_kit.tsn import (
    stations_list_from_tsn,
)


def make_argparser():
    parser = argparse.ArgumentParser(
        description="""Create CSV file with list of stations visited, in order, for a single train number (trip_short_name).
                       Useful when making tt-specs.
                       Should be reviewed manually before generating tt-spec.
                    """,
    )
    add_gtfs_argument(parser)
    add_date_argument(parser)
    add_debug_argument(parser)
    add_output_dirname_argument(parser)
    parser.add_argument(
        "--trip",
        dest="trip_short_name",
        help="""This specifies which trip_short_name to use to generate the list of stations.
                For instance, if it's "51", train 51 will be used,
                and the output will be tt_51_stations.csv.
             """,
    )
    parser.add_argument(
        "trip",
        help="""This specifies which trip_short_name to use to generate the list of stations.
                For instance, if it's "51", train 51 will be used,
                and the output will be tt_51_stations.csv.
             """,
        nargs="?",
    )
    parser.add_argument(
        "--day",
        help="""Restrict to trains/buses operating on a particular day of the week""",
    )
    return parser


if __name__ == "__main__":
    my_arg_parser = make_argparser()
    args = my_arg_parser.parse_args()

    set_debug_level(args.debug)
    output_dirname = args.output_dirname
    if not output_dirname:
        output_dirname = os.getenv("TIMETABLE_KIT_OUTPUT_DIR")
    if not output_dirname:
        output_dirname = "."

    if args.gtfs_filename:
        gtfs_filename = args.gtfs_filename
    else:
        # Default to Amtrak
        gtfs_filename = amtrak.gtfs_unzipped_local_path

    reference_date = args.reference_date
    if reference_date is None:
        reference_date = datetime.date.today().strftime("%Y%m%d")
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")
    master_feed = initialize_feed(gtfs=gtfs_filename)
    today_feed = master_feed.filter_by_dates(reference_date, reference_date)

    # Restrict by day of week if specified.
    day_of_week = args.day
    if day_of_week is not None:
        day_of_week = day_of_week.lower()
        if day_of_week not in gtfs_days:
            print("Specifed day of week not understood.")
            exit(1)
        today_feed = today_feed.filter_by_day_of_week(day_of_week)

    optional_tsn = args.trip_short_name
    positional_tsn = args.trip
    match (optional_tsn, positional_tsn):
        case (None, None):
            raise ValueError("Can't generate a station list without a specific trip.")
        case (None, tsn) | (tsn, None):
            pass
        case (_, _):
            raise ValueError(
                "Specified trip_short_name two different ways.  Use only one."
            )
    tsn = tsn.strip()  # Avoid whitespace problems

    # And pull the station list, in order
    station_list_df = stations_list_from_tsn(today_feed, tsn)
    print(station_list_df)
    # Consider dumping to CSV... but don't right now
    # output_filename = "".join([output_dirname, "/", "tt_", tsn, "_", "stations.csv"])
    # station_list_df.to_csv(output_filename, index=False)
    # Note: this will put "stop_id" in top row, which is OK
    sys.exit(0)
