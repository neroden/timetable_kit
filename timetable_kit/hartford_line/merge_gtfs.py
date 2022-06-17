#! /usr/bin/env python3
# hartford_line/merge_gtfs.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Routines for modifying Hartford Line GTFS and merging it with Amtrak's GTFS.
"""

from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import gtfs_kit

# Mine
from timetable_kit import amtrak
from timetable_kit import hartford_line
from timetable_kit.merge_gtfs import merge_feed

module_location = Path(__file__).parent

# This is where the merger of Amtrak and Hartford Line GTFS should go.
merged_gtfs_zip_local_path = module_location / "merged-gtfs.zip"
merged_gtfs_unzipped_local_path = module_location / "merged-gtfs"

# Note:
# hartford_line.get_gtfs.gtfs_zip_local_path has the raw Hartford Line GTFS
# amtrak.get_gtfs.gtfs_zip_local_path has the raw Amtrak GTFS


def run():
    """
    timetable_kit.hartford_line.merge_gtfs.run

    Merge Amtrak and Hartford Line data into a joint GTFS, "hartford_line/merged-gtfs.zip".
    Assumes that Hartford Line and Amtrak data have already been downloaded by amtrak/get_gtfs.py and hartford_line/get_gtfs.py.
    """
    print("Loading Amtrak and Hartford Line GTFS")
    amtrak_feed_path = Path(amtrak.gtfs_zip_local_path)
    amtrak_feed = gtfs_kit.read_feed(amtrak_feed_path, dist_units="mi")

    hl_feed_path = Path(hartford_line.gtfs_zip_local_path)
    hl_feed = gtfs_kit.read_feed(hl_feed_path, dist_units="mi")

    print("Cleaning Hartford Line feed")
    # One of the station codes is different from Amtrak: the others are the same.

    # This risks replacing "ST" in columns other than stop_id,
    # but that doesn't happen in practice...
    new_stop_times = hl_feed.stop_times.replace("ST", "STS")
    hl_feed.stop_times = new_stop_times

    # Delete all Hartford Line stops rows.  This makes an invalid feed,
    # but all the stops are listed in Amtrak's feed, so it'll be fine after merging.
    new_stops = hl_feed.stops[0:0]
    hl_feed.stops = new_stops

    # Delete Hartford Line feed_info, which is unmergeable.
    new_feed_info = hl_feed.feed_info[0:0]
    hl_feed.feed_info = new_feed_info

    # Amtrak route_ids are all numbers.  Hartford Line's is "HL".
    # Amtrak service_ids are all numbers.  Hartford Line's have underscores and letters.
    # Amtrak agency_ids are all numbers.  Hartford Line's is "hartford-line".
    # Hartford Line trip_ids are 4-digit numbers.  Amtrak trip_ids are much longer.
    # So we can just merge stupidly on the rest.

    print("Merging feeds")
    merged_feed = merge_feed(amtrak_feed, hl_feed)

    # print("Exporting feed to files")
    # if not merged_gtfs_unzipped_local_path.exists():
    #     merged_gtfs_unzipped_local_path.mkdir(parents=True)
    # merged_feed.write(Path(merged_gtfs_unzipped_local_path))

    # Experimentally, writing the feed out is slow.  Unzipping it is fast.
    # Writing it out unzipped is just as slow.
    # I didn't want to learn how to zip it.
    print("Writing zipped feed")
    merged_feed.write(Path(merged_gtfs_zip_local_path))
    print("Merged Hartford Line feed into Amtrak feed at", merged_gtfs_zip_local_path)

    # Leave it open for inspection
    print("Unzipping feed")
    with ZipFile(merged_gtfs_zip_local_path, "r") as my_zip:
        if not merged_gtfs_unzipped_local_path.exists():
            merged_gtfs_unzipped_local_path.mkdir(parents=True)
        my_zip.extractall(path=merged_gtfs_unzipped_local_path)
        print("Extracted to " + str(merged_gtfs_unzipped_local_path))


if __name__ == "__main__":
    run()
