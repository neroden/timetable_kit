#! /usr/bin/env python3
# hartford_line/get_gtfs.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Retrieve CT Rail Hartford Line's static GTFS data and merge with Amtrak's."""

from typing import Self
from pathlib import Path
from zipfile import ZipFile

# For loading the feeds for merging
import gtfs_kit  # type: ignore # Tell MyPy this has no type stubs

from timetable_kit.get_gtfs import (
    AgencyGTFSFiles,
    move_old_dir,
    move_old_file,
)
import timetable_kit.amtrak as amtrak  # for get_gtfs_files

# For the merge process
from timetable_kit.merge_gtfs import merge_feed
from timetable_kit.merge_gtfs import remove_stop_code_column


# GTFS seems to be at:
# https://www.cttransit.com/about/developers
# But it uses *numerical* service IDs 1 (disabled), 2 (weekday), 3 (weekend)
# and it's at https://www.ctrides.com/hlgtfs.zip
canonical_gtfs_url = "https://www.ctrides.com/hlgtfs.zip"


# We need a specialized variant.
class HartfordLineGTFSFiles(AgencyGTFSFiles):
    def __init__(self: Self):
        """Initialize locations for Hartford Line GTFS files."""
        super().__init__(agency_subdir="hartford_line", url=canonical_gtfs_url)
        self._amtrak_gtfs_files: AgencyGTFSFiles = amtrak.get_gtfs_files()
        self._merged_dir: Path = (
            self.agency_dir / "merged_gtfs"
        )  # Where merged GTFS goes
        self._merged_file: Path = (
            self.agency_dir / "merged_gtfs.zip"
        )  # Where merged GTFS goes

    def download_and_save(self: Self):
        """Download Hartford Line and Amtrak GTFS, merge, and put in correct location

        Does not re-download Amtrak GTFS unless it is missing.
        """
        # First get the raw files
        super().download_and_save()
        # Then get the Amtrak files, if necessary
        if not self._amtrak_gtfs_files.is_downloaded():
            self._amtrak_gtfs_files.download_and_save()
        # Now do the merge
        self.merge()

    def get_path(self: Self):
        """Return the path for the merged Hartford Line GTFS"""
        return self._merged_dir

    # Convert Hartford Line stop_id values from stops.txt to Amtrak stop_id values (station codes)
    _STOP_ID_CONVERSION = {
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

    def merge(self: Self):
        """Merge Amtrak and Hartford Line data and store in appropriate location.

        Assumes that Hartford Line and Amtrak data have already been downloaded
        """
        print("Loading Amtrak and Hartford Line GTFS")
        amtrak_feed = gtfs_kit.read_feed(
            self._amtrak_gtfs_files.get_path(), dist_units="mi"
        )
        hl_feed = gtfs_kit.read_feed(self._dir, dist_units="mi")

        print("Cleaning Hartford Line feed")

        # We blow away the stops file so don't worry about it.
        # new_stops = hl_feed.stops
        # for idx in new_stops.index:
        #     hartford_stop_id = new_stops.at(idx, "stop_id")
        #     new_stops.at(idx,"stop_id") = _STOP_ID_CONVERSION[hartford_stop_id]
        # hl_feed.stops = new_stops

        new_stop_times = hl_feed.stop_times
        for idx in new_stop_times.index:
            # ALL the stop_id values need to be replaced, because the new
            # Hartford Line feed uses meaningless numbers.  Aaargh!
            hartford_stop_id = new_stop_times.at[idx, "stop_id"]
            new_stop_times.at[idx, "stop_id"] = self._STOP_ID_CONVERSION[
                hartford_stop_id
            ]
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
        # listed in Amtrak's feed (after _STOP_ID_CONVERSION), so it'll be fine after merging.
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
        if self._merged_file.exists():
            move_old_file(self._merged_file)

        print("Writing zipped feed")
        merged_feed.write(self._merged_file)
        print("Merged Hartford Line feed into Amtrak feed at", self._merged_file)

        # Leave it open for inspection and for use by main timetable_kit program
        print("Unzipping feed at", self._merged_dir)
        if self._merged_dir.exists():
            move_old_dir(self._merged_dir)

        self._merged_dir.mkdir(parents=True, exist_ok=False)
        with ZipFile(self._merged_file, "r") as my_zip:
            my_zip.extractall(path=self._merged_dir)
            print("Extracted to " + str(self._merged_dir))

    def is_downloaded(self: Self) -> bool:
        """Return true if there is a GTFS file in the appropriate location

        Used to avoid redundant downloading
        """
        return self._merged_file.exists()


# This is our singleton global.
_gtfs_files = HartfordLineGTFSFiles()


# External interface.
def get_gtfs_files():
    """Retrieve the AgencyGTFSFiles object for the agency"""
    return _gtfs_files


# MAIN PROGRAM
if __name__ == "__main__":
    get_gtfs_files().download_and_save()
