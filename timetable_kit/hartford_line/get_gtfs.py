#! /usr/bin/env python3
# hartford_line/get_gtfs.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Retrieve CT Rail Hartford Line's static GTFS data from the canonical location.

Severely duplicative of amtrak/get_gtfs.py.  Duplication should be removed,
but I needed a working prototype
"""

import sys  # for sys.exit
from pathlib import Path
from zipfile import ZipFile

import requests

# Found at transit.land.  New on 6-14-2022.
#
# Transitland URL:
# https://www.transit.land/feeds/f-cttransit~hartford~line
#
canonical_gtfs_url = "http://www.hartfordline.com/files/gtfs/gtfs.zip"

module_location = Path(__file__).parent

# Note that Amtrak's was uppercase, Hartford Line's is lowercase...
gtfs_zip_local_path = module_location / "gtfs.zip"
gtfs_unzipped_local_path = module_location / "gtfs"

# This cannot possibly be the right way to do this.
# wget is probably cleanest, but adds yet another dependency


def download_gtfs():
    """Download Hartford Line's GTFS from its canonical location and return it"""
    response = requests.get(canonical_gtfs_url)
    if response.status_code != requests.codes.ok:
        print(
            "".join(
                [
                    "Download of ",
                    canonical_gtfs_url,
                    " failed with error ",
                    str(response.status_code),
                    ".",
                ]
            )
        )
        response.raise_for_status()  # Raise an error
    return response.content  # This is binary data


def save_gtfs(gtfs_zip):
    """Save Hartford Line's GTFS file in a canonical local location."""
    with open(gtfs_zip_local_path, "wb") as binary_file:
        binary_file.write(gtfs_zip)


def unzip_gtfs():
    """
    Extract Hartford Line's GTFS file from a canonical local location to a canonical local location.

    This isn't used directly by the program; this is just for human inspection.
    """
    with ZipFile(gtfs_zip_local_path, "r") as my_zip:
        if not gtfs_unzipped_local_path.exists():
            gtfs_unzipped_local_path.mkdir(parents=True)
        my_zip.extractall(path=gtfs_unzipped_local_path)
        print("Extracted to " + str(gtfs_unzipped_local_path))


# MAIN PROGRAM
if __name__ == "__main__":
    save_gtfs(download_gtfs())
    print("Hartford Line GTFS saved at " + str(gtfs_zip_local_path))
    unzip_gtfs()
    sys.exit(0)
