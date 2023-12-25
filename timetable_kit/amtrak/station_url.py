#! /usr/bin/env python3
# amtrak/station_url.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Given an Amtrak three-letter station code, return the URL for that station's
JSON details.

Utility program for the user.  Not used by the timetable program.
"""
import argparse

from timetable_kit.amtrak.json_stations import station_details_url

arg_parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Given an Amtrak three-letter station code, return the URL for that station's JSON details webpage.",
)
arg_parser.add_argument(
    "code",
    help="Amtrak station code",
)

if __name__ == "__main__":
    args = arg_parser.parse_args()
    station_code = args.code
    print(station_details_url(station_code))
