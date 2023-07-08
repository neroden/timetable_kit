#! /usr/bin/env python3
# maple_leaf/merge_gtfs.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Routines for creating a Maple Leaf GTFS from Amtrak's GTFS and VIA's GTFS.
"""

import sys  # for sys.exit

from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import gtfs_kit

# Mine
from timetable_kit import amtrak
from timetable_kit import via
from timetable_kit.merge_gtfs import merge_feed

module_location = Path(__file__).parent

# This is where the Maple Leaf specific GTFS should go.
merged_gtfs_zip_local_path = module_location / "gtfs.zip"
merged_gtfs_unzipped_local_path = module_location / "gtfs"


def filter_feed_by_route_names(feed, route_names: list[str]):
    """
    Filteres a feed down to JUST the data for named routes.
    Erase the shapes data for speed.

    Returs the filtered feed.
    """
    new_feed = feed.copy()

    # Erase shapes.
    new_feed.shapes = None

    # Reduce routes to the Maple Leaf line only.
    new_routes = feed.routes[feed.routes["route_long_name"].isin(route_names)]
    print(new_routes)
    new_feed.routes = new_routes
    # Extract the route_id.
    route_row = new_routes.iloc[0]
    route_id = route_row["route_id"]
    # print(route_id)

    # Filter trips.txt by the route_id.
    new_trips = feed.trips[feed.trips.route_id == route_id]
    # print(new_trips)
    new_feed.trips = new_trips
    # Get the service_id values.
    service_ids = new_trips["service_id"].tolist()
    # print(service_ids)
    # Get the trip_id values.
    trip_ids = new_trips["trip_id"].tolist()
    # print(trip_ids)

    # Filter calendar.txt by the service_id.
    new_calendar = feed.calendar[feed.calendar["service_id"].isin(service_ids)]
    # print(new_calendar)
    new_feed.calendar = new_calendar

    # Filter stop_times.txt by the trip_id.
    new_stop_times = feed.stop_times[feed.stop_times["trip_id"].isin(trip_ids)]
    # print(new_stop_times)
    new_feed.stop_times = new_stop_times
    # Get ths stop_id values. (will have some redundancy)
    stop_ids = new_stop_times["stop_id"].tolist()
    # print(stop_ids)

    # Filter stops.txt by the stop_id.
    new_stops = feed.stops[feed.stops["stop_id"].isin(stop_ids)]
    # print(new_stops)
    new_feed.stops = new_stops

    return new_feed


def run():
    """
    timetable_kit.maple_leaf.merge_gtfs.run

    Merge Amtrak and VIA data for the Maple Leaf only into a joint GTFS, "maple_leaf/gtfs".
    Assumes that Amtrak and VIA data have already been downloaded by amtrak/get_gtfs.py and via/get_gtfs.py.
    """
    print("Loading Amtrak GTFS")
    amtrak_feed_path = Path(amtrak.gtfs_unzipped_local_path)
    amtrak_feed = gtfs_kit.read_feed(amtrak_feed_path, dist_units="mi")

    print("Filtering Amtrak feed")
    amtrak_maple_leaf_feed = filter_feed_by_route_names(amtrak_feed, ["Maple Leaf"])

    print("Loading VIA GTFS")
    via_feed_path = Path(via.gtfs_unzipped_local_path)
    via_feed = gtfs_kit.read_feed(via_feed_path, dist_units="mi")

    print("Filtering VIA feed")
    via_maple_leaf_feed = filter_feed_by_route_names(via_feed, ["Toronto - New York"])

    # Delete VIA feed_info, which is unmergeable. (Have to delete one or the other.)
    # Should really rebuild this from the whole cloth.
    new_feed_info = via_maple_leaf_feed.feed_info[0:0]
    via_maple_leaf_feed.feed_info = new_feed_info

    # At this point, a merger is *possible*, but the data is ugly.
    # We rely on certain other data, notably agency_id, not conflicting.
    # We should actually stuff prefixes on everything.  TODO.
    # We need to unify the stop lists and clean up.

    print("Merging feeds")
    merged_feed = merge_feed(amtrak_maple_leaf_feed, via_maple_leaf_feed)

    # Experimentally, writing the feed out is slow.  Unzipping it is fast.
    # Writing it out unzipped is just as slow.
    # I didn't want to learn how to zip it.
    print("Writing zipped feed")
    merged_feed.write(Path(merged_gtfs_zip_local_path))
    print("Merged feed for Maple Leaf at", merged_gtfs_zip_local_path)

    # Leave it open for inspection and use by main timetable program
    print("Unzipping feed")
    with ZipFile(merged_gtfs_zip_local_path, "r") as my_zip:
        if not merged_gtfs_unzipped_local_path.exists():
            merged_gtfs_unzipped_local_path.mkdir(parents=True)
        my_zip.extractall(path=merged_gtfs_unzipped_local_path)
        print("Extracted to " + str(merged_gtfs_unzipped_local_path))


if __name__ == "__main__":
    run()
