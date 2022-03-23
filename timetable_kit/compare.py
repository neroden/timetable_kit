#! /usr/bin/env python3
# compare.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Find timing differences on a route between similar services.

Used to see how many services with different dates are actually the same service.
"""

# Other people's packages
import argparse
import datetime

import pandas as pd
import gtfs_kit as gk

# My packages: Local module imports
# Note namespaces are separate for each file/module
# Also note: python packaging is really sucky for direct script testing.
from timetable_kit.errors import (
    GTFSError,
    NoStopError,
    TwoStopsError,
    NoTripError,
    TwoTripsError,
    InputError
)
from timetable_kit.debug import (set_debug_level, debug_print)
from timetable_kit.timetable_argparse import make_tt_arg_parser

# This one monkey-patches gk.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

# To intialize the feed -- does type changes
from timetable_kit.initialize import initialize_feed

from timetable_kit import amtrak # so we don't have to say "timetable_kit.amtrak"

# Common arguments for the command line
from timetable_kit.timetable_argparse import (
    add_gtfs_argument,
    add_date_argument,
    add_debug_argument,
    )

### "Compare" Debugging routines to check for changes in timetable

def compare_stop_lists(base_trip, trips, *, feed):
    """
    Find the diff between one trip and a bunch of other (presumably similar) trips.

    Debugging routine used to identify upcoming changes in train schedules.
    Given a stop_list DataFrame and a list of stop_list DataFrames,
    all with the same shape, (we may expand this later FIXME)
    print the diff of each later one with the first.

    Prefers to start with stop_times tables with unique, but matching, indexes.
    Using stop_sequence as the index can usually provide this.
    """
    if (len(trips) == 0):
        print ("No trips, stopping.")
        return
    if (len(trips) == 1):
        print ("Only 1 trip, stopping.")
        return
    # Drop the trip_id because it will always compare differently
    base_stop_times = feed.get_single_trip_stop_times(base_trip["trip_id"])
    base_stop_times = base_stop_times.drop(["trip_id"], axis="columns")
    for trip in (trips.itertuples()):
        stop_times = feed.get_single_trip_stop_times(trip.trip_id)
        stop_times = stop_times.drop(["trip_id"],axis="columns")
        # Use powerful features of DataTable
        comparison = base_stop_times.compare(stop_times, align_axis="columns", keep_shape=True)
        if (not comparison.any(axis=None)):
            print( " ".join(["Identical:", str(base_trip.trip_id), "and", str(trip.trip_id)]) + "." )
        else:
            reduced_comparison = comparison.dropna(axis="index",how="all")
            print( " ".join(["Comparing:",str(base_trip.trip_id),"vs.",str(trip.trip_id)]) + ":" )
            #print( reduced_comparison )
            # Works up to here!

            # Please note the smart way to add an extra MultiIndex layer is with "concat".
            # Completely nonobvious.  "concat" with "keys" option.

            # We want to recover the stop_id for more comprehensibility.
            # Stupid program wants matching-depth MultiIndex.  There is no easy way to make it.
            # So make it the stupid way!  Build it exactly parallel to the real comparison.
            fake_comparison = base_stop_times.compare(base_stop_times,
                                                      align_axis="columns",
                                                      keep_shape=True,
                                                      keep_equal=True)
            reduced_fake_comparison = fake_comparison.filter(
                                            items=reduced_comparison.index.array,
                                            axis="index"
                                            )
            enhanced_comparison = reduced_comparison.combine_first(reduced_fake_comparison)
            # And we're ready to print.
            print( enhanced_comparison )
    return

def compare_similar_services(route_id, *, feed):
    """
    Find timing differences on a route between similar services.

    Used to see how many services with different dates are actually the same service
    """
    route_feed = feed.filter_by_route_ids([route_id])

    print("Calendar:")
    print(route_feed.calendar)

    print("Downbound:")
    downbound_trips = route_feed.trips[route_feed.trips.direction_id == 0] # W for LSL
    print(downbound_trips)
    base_trip = downbound_trips.iloc[0, :] # row 0, all columns
    compare_stop_lists(base_trip,downbound_trips, feed=route_feed)

    print("Upbound:")
    upbound_trips = route_feed.trips[route_feed.trips.direction_id == 1] # E for LSL
    print(upbound_trips)
    base_trip = upbound_trips.iloc[0, :] # row 0, all columns
    compare_stop_lists(base_trip,upbound_trips, feed=route_feed)
    return

def make_argparser():
    parser = argparse.ArgumentParser(
        description="""Compare timetables for all trips on a single route.
                       Used to spot schedule changes for making tt-specs.
                    """,
        )
    add_gtfs_argument(parser)
    add_date_argument(parser)
    add_debug_argument(parser)
    parser.add_argument("--route",
        dest="route_long_name",
        help="""This specifies which route_long_name to use.
                For instance "Cardinal" or "Lake Shore Limited".
             """
        )
    return parser


### Main program
if __name__ == "__main__":
    my_arg_parser = make_argparser()
    args = my_arg_parser.parse_args()

    set_debug_level(args.debug)

    if (args.gtfs_filename):
        gtfs_filename = args.gtfs_filename
    else:
        # Default to Amtrak
        gtfs_filename = amtrak.gtfs_unzipped_local_path

    if (args.reference_date):
        reference_date = int( args.reference_date.strip() )
    else:
        # Use tomorrow as the reference date.
        # After all, you aren't catching a train today, right?
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        reference_date = int( tomorrow.strftime('%Y%m%d') )
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")

    master_feed = initialize_feed(gtfs=gtfs_filename)

    route_long_name = args.route_long_name

    # Create lookup table from route name to route id. Amtrak only has long names, not short names.
    lookup_route_id = dict(zip(master_feed.routes.route_long_name, master_feed.routes.route_id))
    route_id = lookup_route_id[route_long_name]

    compare_similar_services(route_id, feed=master_feed)
    quit()
