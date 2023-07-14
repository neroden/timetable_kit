#! /usr/bin/env python3
# icons.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Merge two GTFS feeds.

Currently does no validation.
Deletes the shapes table, since we don't use it.
"""

import sys  # for argv
from pathlib import Path

import gtfs_kit
import pandas as pd


def index_by_ids(old_feed: gtfs_kit.Feed, /) -> gtfs_kit.Feed:
    """
    Return a copy of the feed, with all the tables which have unique IDs indexed by them.

    This will be a slightly broken Feed, as gtfs_kit.Feed does not expect the indexing.
    """
    feed = old_feed.copy()
    # Required files.
    # Note that the agency_id field is optional.  FIXME.
    feed.agency.set_index("agency_id", inplace=True)
    feed.stops.set_index("stop_id", inplace=True)
    feed.routes.set_index("route_id", inplace=True)
    feed.trips.set_index("trip_id", inplace=True)
    feed.stop_times.set_index("trip_id", inplace=True)
    if feed.calendar is not None:
        feed.calendar.set_index("service_id", inplace=True)
    if feed.calendar_dates is not None:
        feed.calendar_dates.set_index("service_id", inplace=True)
    if feed.fare_attributes is not None:
        feed.fare_attributes.set_index("fare_id", inplace=True)
    if feed.fare_rules is not None:
        feed.fare_rules.set_index("fare_id", inplace=True)
    # if feed.shapes is not None:
    #    feed.shapes.set_index("shape_id", inplace=True)
    # We don't use shapes.  Speed this up by deleting it entirely.
    feed.shapes = None
    if feed.frequencies is not None:
        feed.frequencies.set_index("trip_id", inplace=True)
    # Transfers is more complicated.  FIXME
    # pathways and levels are not implemented by gtfs_kit (whoops!)
    # if feed.pathways:
    #     feed.pathways.set_index("pathway_id", inplace=True)
    # if feed.levels:
    #    feed.levels.set_index("level_id", inplace=True)
    # feed_info doesn't need to be indexed by IDs.
    # Translations is much more complicated and isn't implemented by gtfs_kit (whoops!)
    if feed.attributions is not None:
        feed.attributions.set_index("attribution_id", inplace=True)
    return feed


# This is the set of all genuine table names in the feed
# Not including the internal ones.
# FIXME -- this is fragile.  Make more robust.
table_names = set(gtfs_kit.constants.FEED_ATTRS_1) - {"dist_units"}


def merge_feed(feed_a, feed_b) -> gtfs_kit.Feed:
    """
    Merge two feeds.  Return the merged feed.

    Does not do ANY checking for uniqueness or duplicates.
    To get a valid feed as a result, all the _id fields must be unique.
    Filter your feeds first if you have duplicates.
    """

    # gtfs_kit.constants.FEED_ATTRS_1
    # First, copy the incoming feeds for index manipulation.
    # They are now prepared to be concatenated.
    a = index_by_ids(feed_a)
    b = index_by_ids(feed_b)
    feed_out = gtfs_kit.Feed(dist_units=a.dist_units)
    # FIXME: This uses the dist_units from A with no conversion attempt for B

    for table_name in table_names:
        print("Doing", table_name)
        source_tables = [getattr(a, table_name), getattr(b, table_name)]
        match source_tables:
            case [None, None]:
                table_value = None
            case [None, value] | [value, None]:
                table_value = value.reset_index()
            case _:
                table_value = pd.concat(source_tables).reset_index()
        setattr(feed_out, table_name, table_value)

    return feed_out


# MAIN PROGRAM
if __name__ == "__main__":
    # TO DO: be smarter about this; use argparse
    if len(sys.argv) < 4:
        print("Usage: merge_gtfs.py gtfs-a.zip gtfs-b.zip gtfs-out.zip")
        sys.exit(1)
    feed_a_filename = sys.argv[1]
    feed_b_filename = sys.argv[2]
    filename_out = sys.argv[3]

    feed_a = gtfs_kit.read_feed(Path(feed_a_filename), dist_units="mi")
    feed_b = gtfs_kit.read_feed(Path(feed_b_filename), dist_units="mi")

    feed_out = merge_feed(feed_a, feed_b)
    feed_out.write(Path(filename_out))
