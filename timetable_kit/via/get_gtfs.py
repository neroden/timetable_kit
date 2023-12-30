#! /usr/bin/env python3
# via/get_gtfs.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Retrieve VIA Rail's static GTFS data from the canonical location."""

from timetable_kit.get_gtfs import AgencyGTFSFiles

# Where we should download the GTFS from.
# Found at www.viarail.ca/en/developer-resources
#
canonical_gtfs_url = "https://www.viarail.ca/sites/all/files/gtfs/viarail.zip"

# This is our singleton global.
_gtfs_files = AgencyGTFSFiles("via", canonical_gtfs_url)


# External interface.
def get_gtfs_files():
    """Retrieve the AgencyGTFSFiles object for the agency"""
    return _gtfs_files


# MAIN PROGRAM
if __name__ == "__main__":
    get_gtfs_files().download_and_save()
