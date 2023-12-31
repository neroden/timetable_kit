#! /usr/bin/env python3
# maple_leaf/get_gtfs.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Routines for creating a Maple Leaf GTFS from Amtrak's GTFS and VIA's GTFS."""

import sys  # for sys.exit

from typing import Self
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import gtfs_kit  # type: ignore # Tell MyPy this has no type stubs

# Mine
from timetable_kit.feed_enhanced import FeedEnhanced  # for filtering

# For the merge
from timetable_kit import amtrak
from timetable_kit import via

from timetable_kit.get_gtfs import AgencyGTFSFiles, move_old_dir, move_old_file
from timetable_kit.merge_gtfs import merge_feed, remove_stop_code_column

from timetable_kit.maple_leaf.station_data import (
    amtrak_code_to_via_code,
    via_code_to_amtrak_code,
)


def translate_via_stations_to_amtrak(via_ml_feed):
    """Translates stations in the VIA feed to Amtrak stations.

    Returns altered feed.
    """
    new_feed = via_ml_feed.copy()

    # First, generate map from stop_id to VIA station code.
    stops = via_ml_feed.stops
    stop_id_to_via_code = dict(zip(stops["stop_id"], stops["stop_code"]))
    # Now make a map from stop_id to Amtrak station code.
    stop_id_to_amtrak_code = {
        stop_id: via_code_to_amtrak_code[via_code]
        for (stop_id, via_code) in stop_id_to_via_code.items()
    }
    # print(stop_id_to_amtrak_code)
    # Create a dict suitable for DataFrame.replace
    replacement_dict = {"stop_id": stop_id_to_amtrak_code}
    # Next, reassign the stop_id values in stop_times and stops.
    new_stop_times = via_ml_feed.stop_times.replace(replacement_dict)
    new_feed.stop_times = new_stop_times
    new_stops = via_ml_feed.stops.replace(replacement_dict)
    new_feed.stops = new_stops
    return new_feed


def eliminate_redundant_via_stations(via_ml_feed, amtrak_ml_feed):
    """Trims down the stops.txt in a VIA Maple Leaf feed (translated to Amtrak station
    codes) to only those stations which are not already in the Amtrak stops.txt.

    All the Canadian stations are in the Amtrak online database but not all of them are
    in the GTFS.
    """
    new_feed = via_ml_feed.copy()

    amtrak_stop_ids = amtrak_ml_feed.stops["stop_id"].tolist()
    via_stop_ids = via_ml_feed.stops["stop_id"].tolist()
    unique_via_stop_ids = list(set(via_stop_ids) - set(amtrak_stop_ids))
    print("Stops only present in VIA data:", unique_via_stop_ids)

    reduced_stops = via_ml_feed.stops[
        via_ml_feed.stops["stop_id"].isin(unique_via_stop_ids)
    ]
    print(reduced_stops)
    new_feed.stops = reduced_stops
    return new_feed


# We need a specialized variant.
class MapleLeafGTFSFiles(AgencyGTFSFiles):
    """Handles the creation of the Maple Leaf Frankenfeed from Amtrak and Via data"""

    def __init__(self: Self):
        """Initialize locations for Maple Leaf GTFS files."""
        super().__init__(agency_subdir="maple_leaf", url="")
        self._amtrak_gtfs_files: AgencyGTFSFiles = amtrak.get_gtfs_files()
        self._via_gtfs_files: AgencyGTFSFiles = via.get_gtfs_files()

    # Do not implement these methods, which exist on the superclass, on this class.
    # Because Maple Leaf doesn't really have its own GTFS.
    download = None
    save = None

    def download_and_save(self: Self):
        """Download Amtrak and Via GTFS, merge, and put in correct location

        Does not re-download Amtrak or Via GTFS unless it is missing.
        """
        if not self._amtrak_gtfs_files.is_downloaded():
            self._amtrak_gtfs_files.download_and_save()
        if not self._via_gtfs_files.is_downloaded():
            self._via_gtfs_files.download_and_save()
        # Now do the merge
        self.merge()
        # Merge produces both zipped and unzippled version

    def merge(self: Self):
        """Merge Amtrak and VIA data for the Maple Leaf only into a joint GTFS.

        Assumes that Amtrak and VIA data have already been downloaded.
        """
        print("Loading Amtrak GTFS")
        amtrak_feed = FeedEnhanced.enhance(
            gtfs_kit.read_feed(self._amtrak_gtfs_files.get_path(), dist_units="mi")
        )

        print("Filtering Amtrak feed")
        amtrak_ml_feed = amtrak_feed.filter_by_route_long_names(["Maple Leaf"])

        print("Loading VIA GTFS")
        via_feed = FeedEnhanced.enhance(
            gtfs_kit.read_feed(self._via_gtfs_files.get_path(), dist_units="mi")
        )

        print("Filtering VIA feed")
        via_ml_feed = via_feed.filter_by_route_long_names(["Toronto - New York"])

        print("Translating VIA stations")
        via_ml_feed = translate_via_stations_to_amtrak(via_ml_feed)
        print("Eliminating redundant VIA stations")
        via_ml_feed = eliminate_redundant_via_stations(via_ml_feed, amtrak_ml_feed)

        # Delete VIA feed_info, which is unmergeable. (Have to delete one or the other.)
        # Should really rebuild this from the whole cloth.
        new_feed_info = via_ml_feed.feed_info[0:0]
        via_ml_feed.feed_info = new_feed_info

        # At this point, a merger is *possible*, but the data is ugly.
        # We rely on certain other data, notably agency_id, not conflicting.
        # We should actually stuff prefixes on everything.  TODO.
        # We need to unify the stop lists and clean up.

        print("Merging feeds")
        merged_feed = merge_feed(amtrak_ml_feed, via_ml_feed)
        print("Eliminating stop_code column")
        remove_stop_code_column(merged_feed)

        # Experimentally, writing the feed out is slow.  Unzipping it is fast.
        # Writing it out unzipped is just as slow.
        # I didn't want to learn how to zip it.
        if self._file.exists():
            move_old_file(self._file)

        print("Writing zipped feed")
        merged_feed.write(self._file)
        print("Merged feed for Maple Leaf at", self._file)

        # Unzip for inspection and use by main timetable program
        self.unzip()


# This is our singleton global.
_gtfs_files = MapleLeafGTFSFiles()


# External interface.
def get_gtfs_files():
    """Retrieve the AgencyGTFSFiles object for the agency"""
    return _gtfs_files


if __name__ == "__main__":
    get_gtfs_files().download_and_save()
