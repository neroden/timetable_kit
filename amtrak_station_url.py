#! /usr/bin/env python3
# amtrak_station_url.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

import argparse

# These are mine
import amtrak_json_stations

arg_parser = argparse.ArgumentParser(
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description="Given an Amtrak three-letter station code, return the URL for that station's JSON details webpage."
    )
arg_parser.add_argument('code',
    help='Amtrak station code',
    )

if __name__ == "__main__":

    args = arg_parser.parse_args()
    station_code = args.code
    print(amtrak_json_stations.station_details_url(station_code))
    quit()
