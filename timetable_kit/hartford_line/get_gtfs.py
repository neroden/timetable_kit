#! /usr/bin/env python3
# hartford_line/get_gtfs.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Retrieve CT Rail Hartford Line's static GTFS data from the canonical location.

Severely duplicative of amtrak/get_gtfs.py.  Duplication should be removed, but I needed
a working prototype
"""

import sys  # for sys.exit
from pathlib import Path
from zipfile import ZipFile

import requests

# GTFS seems to be at:
# https://www.cttransit.com/about/developers
# But it uses *numerical* service IDs 1 (disabled), 2 (weekday), 3 (weekend)
# and it's at https://www.ctrides.com/hlgtfs.zip
canonical_gtfs_url = "https://www.ctrides.com/hlgtfs.zip"

module_location = Path(__file__).parent

gtfs_raw_zip_local_path = module_location / "gtfs_raw.zip"
gtfs_raw_unzipped_local_path = module_location / "gtfs_raw"


def download_gtfs():
    """Download Hartford Line's GTFS from its canonical location and return it."""
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


def save_gtfs(gtfs_raw_zip):
    """Save Hartford Line's GTFS file in a canonical local location."""
    with open(gtfs_raw_zip_local_path, "wb") as binary_file:
        binary_file.write(gtfs_raw_zip)


def unzip_gtfs():
    """Extract Hartford Line's GTFS file from a canonical local location to a canonical
    local location.

    This isn't used directly by the program; this is just for human inspection.
    """
    with ZipFile(gtfs_raw_zip_local_path, "r") as my_zip:
        if not gtfs_raw_unzipped_local_path.exists():
            gtfs_raw_unzipped_local_path.mkdir(parents=True)
        my_zip.extractall(path=gtfs_raw_unzipped_local_path)
        print("Extracted to " + str(gtfs_raw_unzipped_local_path))


# MAIN PROGRAM
if __name__ == "__main__":
    save_gtfs(download_gtfs())
    print("Hartford Line GTFS saved at " + str(gtfs_raw_zip_local_path))
    unzip_gtfs()
    sys.exit(0)
