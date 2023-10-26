#! /usr/bin/env python3
# hartford_line/merge_gtfs.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Routines for modifying Hartford Line GTFS and merging it with Amtrak's GTFS.
"""

from pathlib import Path
from zipfile import ZipFile

import gtfs_kit

# Mine
from timetable_kit import amtrak
from timetable_kit import hartford_line
from timetable_kit.merge_gtfs import merge_feed
from timetable_kit.merge_gtfs import remove_stop_code_column

module_location = Path(__file__).parent

# This is where the merger of Amtrak and Hartford Line GTFS should go.
gtfs_zip_local_path = module_location / "gtfs.zip"
gtfs_unzipped_local_path = module_location / "gtfs"

# Amtrak GTFS will be pulled from amtrak.gtfs_unzipped_local_path
# Hartford Line raw GTFS will be pulled from hartford_line.gtfs_raw_unzipped_local_path

# Convert Hartford Line stop_id values from stops.txt to Amtrak stop_id values (station codes)
stop_id_conversion = {
    "1": "NHV",
    "2": "STS",
    "3": "WFD",
    "4": "MDN",
    "5": "BER",
    "6": "HFD",
    "7": "WND",
    "8": "WNL",
    "9": "SPG",
}


def run():
    """
    timetable_kit.hartford_line.merge_gtfs.run

    Merge Amtrak and Hartford Line data into a joint GTFS, "hartford_line/merged-gtfs.zip".
    Assumes that Hartford Line and Amtrak data have already been downloaded by amtrak/get_gtfs.py and hartford_line/get_gtfs.py.
    """
    print("Loading Amtrak and Hartford Line GTFS")
    amtrak_feed_path = Path(amtrak.gtfs_unzipped_local_path)
    amtrak_feed = gtfs_kit.read_feed(amtrak_feed_path, dist_units="mi")

    hl_feed_path = Path(hartford_line.get_gtfs.gtfs_raw_unzipped_local_path)
    hl_feed = gtfs_kit.read_feed(hl_feed_path, dist_units="mi")

    print("Cleaning Hartford Line feed")

    # We blow away the stops file so don't worry about it.
    # new_stops = hl_feed.stops
    # for idx in new_stops.index:
    #     hartford_stop_id = new_stops.at(idx, "stop_id")
    #     new_stops.at(idx,"stop_id") = stop_id_conversion[hartford_stop_id]
    # hl_feed.stops = new_stops

    new_stop_times = hl_feed.stop_times
    for idx in new_stop_times.index:
        # ALL the stop_id values need to be replaced, because the new
        # Hartford Line feed uses meaningless numbers.  Aaargh!
        hartford_stop_id = new_stop_times.at[idx, "stop_id"]
        new_stop_times.at[idx, "stop_id"] = stop_id_conversion[hartford_stop_id]
        # Hartford Line trip_ids are 4-digit or 5-digit numbers.
        # Unfortunately, these can overlap with Amtrak trip_ids, which run the gamut of digits.
        hartford_trip_id = new_stop_times.at[idx, "trip_id"]
        new_stop_times.at[idx, "trip_id"] = "H" + hartford_trip_id
    hl_feed.stop_times = new_stop_times
    print("Repaired stop_times")

    new_trips = hl_feed.trips
    for idx in new_trips.index:
        # Hartford Line trip_ids are 4-digit or 5-digit numbers.
        # Unfortunately, these can overlap with Amtrak trip_ids, which run the gamut of digits.
        hartford_trip_id = new_trips.at[idx, "trip_id"]
        new_trips.at[idx, "trip_id"] = "H" + hartford_trip_id
    hl_feed.trips = new_trips
    print("Repaired trips")

    # Delete all Hartford Line stops rows.  This makes an invalid feed, but all the stops are
    # listed in Amtrak's feed (after stop_id_conversion), so it'll be fine after merging.
    new_stops = hl_feed.stops[0:0]
    hl_feed.stops = new_stops

    # Delete Hartford Line feed_info, which is unmergeable.
    new_feed_info = hl_feed.feed_info[0:0]
    hl_feed.feed_info = new_feed_info

    # Amtrak route_ids are all numbers.  Hartford Line's is "HART".
    # Amtrak service_ids are all LONG numbers.  Hartford Line's are "1", "2", "3".
    # Amtrak agency_ids are all numbers.  Hartford Line's is "1", not used by Amtrak.
    # So we can just merge stupidly on the rest.

    print("Merging feeds")
    merged_feed = merge_feed(amtrak_feed, hl_feed)
    print("Eliminating stop code column")
    remove_stop_code_column(merged_feed)

    # Experimentally, writing the feed out is slow.  Unzipping it is fast.
    # Writing it out unzipped is just as slow.
    # I didn't want to learn how to zip it.
    print("Writing zipped feed")
    merged_feed.write(Path(gtfs_zip_local_path))
    print("Merged Hartford Line feed into Amtrak feed at", gtfs_zip_local_path)

    # Leave it open for inspection and for use by main timetable_kit program
    print("Unzipping feed")
    with ZipFile(gtfs_zip_local_path, "r") as my_zip:
        if not gtfs_unzipped_local_path.exists():
            gtfs_unzipped_local_path.mkdir(parents=True)
        my_zip.extractall(path=gtfs_unzipped_local_path)
        print("Extracted to " + str(gtfs_unzipped_local_path))


if __name__ == "__main__":
    run()
