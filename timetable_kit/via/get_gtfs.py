#! /usr/bin/env python3
# via/get_gtfs.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Retrieve VIA Rail's static GTFS data from the canonical location.

Severely duplicative of amtrak/get_gtfs.py.  Duplication should be removed,
but I needed a working prototype
"""

import sys  # for sys.exit
from pathlib import Path
from zipfile import ZipFile

import requests

# Where we should download the GTFS from.
# Found at www.viarail.ca/en/developer-resources
#
canonical_gtfs_url = "https://www.viarail.ca/sites/all/files/gtfs/viarail.zip"

# This is the URL we should publish at the bottom of the timetable as the
# source for GTFS data.  This should probably be a transit.land or similar
# reference, in case the canonical url changes.
published_gtfs_url = "https://www.transit.land/feeds/f-f-viarail~traindecharlevoix"

module_location = Path(__file__).parent
gtfs_zip_local_path = module_location / "gtfs.zip"
gtfs_unzipped_local_path = module_location / "gtfs"

# This cannot possibly be the right way to do this.
# wget is probably cleanest, but adds yet another dependency


def download_gtfs():
    """Download VIA rail's GTFS from its canonical location and return it"""
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
    """Save VIA Rail's GTFS file in a canonical local location."""
    with open(gtfs_zip_local_path, "wb") as binary_file:
        binary_file.write(gtfs_zip)


def unzip_gtfs():
    """
    Extract VIA Rail's GTFS file from a canonical local location to a canonical local location.

    This is used directly by the program.
    """
    with ZipFile(gtfs_zip_local_path, "r") as my_zip:
        if not gtfs_unzipped_local_path.exists():
            gtfs_unzipped_local_path.mkdir(parents=True)
        my_zip.extractall(path=gtfs_unzipped_local_path)
        print("Extracted to " + str(gtfs_unzipped_local_path))


# MAIN PROGRAM
if __name__ == "__main__":
    save_gtfs(download_gtfs())
    print("VIA Rail GTFS saved at " + str(gtfs_zip_local_path))
    unzip_gtfs()
    sys.exit(0)
