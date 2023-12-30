#! /usr/bin/env python3
# greyhound/get_gtfs.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Retrieve Greyhound's static GTFS data from the canonical location."""

from timetable_kit.get_gtfs import AgencyGTFSFiles

# Found at transit.land.
# Also at The Mobility Database on GitHub.  MobilityData/mobility-database
# This is the URL we should download the GTFS from.
canonical_gtfs_url = "http://gtfs.gis.flix.tech/gtfs_generic_us.zip"

# This is our singleton global.
_gtfs_files = AgencyGTFSFiles("greyhound", canonical_gtfs_url)


# Extrenal interface.
def get_gtfs_files():
    """Retrieve the AgencyGTFSFiles object for the agency"""
    return _gtfs_files


# MAIN PROGRAM
if __name__ == "__main__":
    get_gtfs_files().download_and_save()
