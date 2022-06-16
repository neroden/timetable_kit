#! /usr/bin/env python3
# icons.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Merge two GTFS feeds.
"""

import sys # for argv
from pathlib import Path

import pandas as pd
import gtfs_kit as gk

def index_by_ids(old_feed: gk.Feed, / ) -> gk.Feed:
    """
    Return a copy of the feed, with all the tables which have unique IDs indexed by them.
    """
    feed = old_feed.copy()
    # Required files.
    # Note that the agency_id field is optional.  FIXME.
    feed.agency.set_index("agency_id", inplace = True)
    feed.stops.set_index("stop_id", inplace = True)
    feed.routes.set_index("route_id", inplace = True)
    feed.trips.set_index("trip_id", inplace = True)
    feed.stop_times.set_index("trip_id", inplace = True)
    if feed.calendar is not None:
        feed.calendar.set_index("service_id", inplace = True)
    if feed.calendar_dates is not None:
        feed.calendar_dates.set_index("service_id", inplace=True)
    if feed.fare_attributes is not None:
        feed.fare_attributes.set_index("fare_id", inplace=True)
    if feed.fare_rules is not None:
        feed.fare_rules.set_index("fare_id", inplace=True)
    if feed.shapes is not None:
        feed.shapes.set_index("shape_id", inplace=True)
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

def merge_feed(feed_a, feed_b) -> gk.Feed:
    """
    Merge two feeds.  Return the merged feed.

    All the _id fields must be unique.  Filter your feed first if you have duplicates.
    """

    # First, copy the incoming feeds for index manipulation.
    # They are now prepared to be concatenated.
    a = index_by_ids(feed_a)
    b = index_by_ids(feed_b)
    feed_out = gk.Feed(dist_units=a.dist_units)
    # FIXME: This uses the dist_units from A with no conversion attempt for B

    # FIXME: This is not working.  Try using database join instead :-(

    # Note that we have to hack into _trips, _calendar, and _calendar_dates
    # Because the decorated versions can't handle concat
    feed_out.agency = pd.concat([a.agency, b.agency], verify_integrity=True)
    feed_out.stops = pd.concat([a.stops, b.stops], verify_integrity=False) # for testing
    feed_out.routes = pd.concat([a.routes, b.routes], verify_integrity=True)
    feed_out.trips = pd.concat([a._trips, b._trips], verify_integrity=True)
    feed_out.stop_times = pd.concat([a.stop_times, b.stop_times], verify_integrity=True)
    feed_out.calendar = pd.concat([a._calendar, b._calendar], verify_integrity=True)
    feed_out.calendar_dates = pd.concat([a._calendar_dates], b._calendar_dates, verify_integrity=True)
    feed_out.fare_attributes = pd.concat([a.fare_attributes], b.fare_attributes, verify_integrity=True)
    feed_out.fare_rules = pd.concat([a.fare_rules, b.fare_rules], verify_integrity=True)
    feed_out.shapes = pd.concat([a.shapes, b.shapes], verify_integrity=True)
    feed_out.frequencies = pd.concat([a.frequencies, b.frequencies], verify_integrity=True)
    feed_out.transfers = pd.concat([a.transfers, b.transfers], verify_integrity=True)
    feed_out.feed_info = pd.concat([a.feed_info, b.feed_info], verify_integrity=True)
    feed_out.attributions = pd.concat([a.attributions, b.attributions], verify_integrity=True)
    # FIXME: this does not handle the tables not handled by gtfs_kit

    # NOTE: this leaves the pandas tables in feed_out indexed, which may be wrong.  FIXME

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

    feed_a = gk.read_feed(Path(feed_a_filename), dist_units="mi")
    feed_b = gk.read_feed(Path(feed_b_filename), dist_units="mi")

    feed_out = merge_feed(feed_a, feed_b)
    feed_out.write(Path(filename_out))
