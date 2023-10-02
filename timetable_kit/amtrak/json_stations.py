#! /usr/bin/env python3
# amtrak_json_stations.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Routines for extracting Amtrak's JSON station data and working with it.

Amtrak's entire station database is exposed as JSON, which is very useful.
In order to download it, this must be run as a program.

A couple of key pieces of data are only exposed as HTML, so the HTML is downloaded too.

The other routines here are for accessing it.

get_station_name is the primary one.
"""

# "./json_stations.py download"
# will download Amtrak's station files into the './stations/' directory
# otherwise runs test case

import sys
from pathlib import Path
from io import StringIO  # Needed to parse JSON
import argparse

import requests
import json  # better for the details import
from time import sleep  # Avoid slamming Amtrak's server too fast -- not needed

import pandas as pd

import random

# SO.  It turns out that Amtrak's station database is exposed as JSON.  Here are the key URLs.

# INITIALIZATION CODE
# GLOBAL VARIABLES

# This is the entire station list as json -- names and all.
stations_json_url = "https://www.amtrak.com/services/data.stations.json"

# This is the station detail list for one station.
station_details_url_prefix = "https://www.amtrak.com/content/amtrak/en-us/stations/"
station_details_url_infix = ".stationTabContainer."
station_details_url_postfix = ".json"

# This is the station HTML page for one station.
station_details_html_url_prefix = "https://www.amtrak.com/stations/"
station_details_html_file_postfix = ".html"

# Now, where to put the local cached copy?
module_location = Path(__file__).parent
stations_under_module = module_location / "stations"

working_directory = Path(".")
stations_under_wd = working_directory / "amtrak_stations"

# Default to the one inside the module.
station_details_dir = stations_under_module


#########
# First: the list of all stations, the data.stations.json file


def stations_json_local_path():
    """Return local path for the data.stations.json file as a Path"""
    return station_details_dir / "data.stations.json"


def download_stations_json() -> str:
    """Download Amtrak's basic stations database as json text; return it."""
    # This uses the 'requests' package to download it
    response = requests.get(stations_json_url)
    return response.text


def save_stations_json(stations_json: str):
    """Save Amtrak's basic stations database (json text) to a suitable file."""
    with open(stations_json_local_path(), "w") as stations_json_local_file:
        print(stations_json, file=stations_json_local_file)


def load_stations_json():
    """Load Amtrak's basic stations database (json text) from a suitable file.  Return it."""
    with open(stations_json_local_path(), "r") as stations_json_local_file:
        stations_json = stations_json_local_file.read()
    return stations_json


#########
# Second: the individual JSON files for each station


def station_details_filename(station_code: str) -> str:
    """
    Return filename for an Amtrak station details JSON file

    This does uppercase/lowercase correction.
    """
    # Step one: validate the station code
    if len(station_code) != 3:
        raise ValueError("Station code not of length 3")
    # This might well be case-sensitive
    first_station_code = str.lower(station_code)
    second_station_code = str.upper(station_code)
    filename = "".join(
        [
            first_station_code,
            station_details_url_infix,
            second_station_code,
            station_details_url_postfix,
        ]
    )
    return filename


def station_details_url(station_code: str) -> str:
    """
    Given an Amtrak station code, return the URL for the station details in JSON form.

    Watch out for "403 forbidden" issues...
    """
    # Step one: validate the station code
    if len(station_code) != 3:
        raise ValueError("Station code not of length 3")
    filename = station_details_filename(station_code)
    url = "".join(
        [
            station_details_url_prefix,
            filename,
        ]
    )
    return url


def station_details_local_path(station_code: str) -> str:
    """Return local pathname for an Amtrak station details JSON file"""
    # Step one: validate the station code
    if len(station_code) != 3:
        raise ValueError("Station code not of length 3")
    filename = station_details_filename(station_code)
    path = station_details_dir / filename
    return path


def download_station_details(station_code: str) -> str:
    """Download station details for one station as json text; return it."""
    response = requests.get(station_details_url(station_code))
    # This suffers from the possibility of failure.
    my_text = response.text
    if response.status_code != requests.codes.ok:
        print(
            "".join(
                [
                    "Download JSON for ",
                    station_code,
                    " returned error ",
                    str(response.status_code),
                    "; blanking file.",
                ]
            )
        )
        my_text = "{}"  # Don't fill with whatever garbage we got; this is valid JSON
    return my_text


def save_station_details(station_code: str, station_details: str):
    """Save station details for one station to a suitable file."""
    with open(
        station_details_local_path(station_code), "w"
    ) as station_details_local_file:
        print(station_details, file=station_details_local_file)


def load_station_details(station_code: str) -> str:
    """Load station details for one station as json text from a suitable file; return it."""
    with open(
        station_details_local_path(station_code), "r"
    ) as station_details_local_file:
        station_details = station_details_local_file.read()
    return station_details


#########
# Third: the individual HTML files for each station


def station_details_html_filename(station_code: str) -> str:
    """
    Return filename for an Amtrak station details HTML file

    This does uppercase/lowercase correction.
    """
    # Step one: validate the station code
    if len(station_code) != 3:
        raise ValueError("Station code not of length 3")
    # This is likely to be case-sensitive
    filename = "".join(
        [
            str.lower(station_code),
            station_details_html_file_postfix,
        ]
    )
    return filename


def station_details_html_url(station_code: str) -> str:
    """
    Given an Amtrak station code, return the URL for the station HTML page.

    Watch out for "403 forbidden" issues...
    """
    # Step one: validate the station code
    if len(station_code) != 3:
        raise ValueError("Station code not of length 3")
    # This might be case-sensitive
    url = "".join(
        [
            station_details_html_url_prefix,
            str.lower(station_code),
        ]
    )
    return url


def station_details_html_local_path(station_code: str) -> str:
    """Return local pathname for an Amtrak station details HTML file"""
    # Step one: validate the station code
    if len(station_code) != 3:
        raise ValueError("Station code not of length 3")
    filename = station_details_html_filename(station_code)
    path = station_details_dir / filename
    return path


def download_station_details_html(station_code: str) -> str:
    """Download station HTML file for one station; return it."""
    response = requests.get(station_details_html_url(station_code))
    # This suffers from the possibility of failure.
    my_text = response.text
    if response.status_code != requests.codes.ok:
        print(
            "".join(
                [
                    "Download HTML for ",
                    station_code,
                    " returned error ",
                    str(response.status_code),
                    "; blanking file.",
                ]
            )
        )
        my_text = ""  # Don't fill with whatever garbage we got; this is valid HTML
    return my_text


def save_station_details_html(station_code: str, station_details: str):
    """Save station HTML for one station to a suitable file."""
    with open(
        station_details_html_local_path(station_code), "w"
    ) as station_details_html_local_file:
        # If necessary, use utf-8 to prevent UnicodeEncodeError
        try:
            print(station_details, file=station_details_html_local_file)
        except:
            print(station_details.encode("utf-8"), file=station_details_html_local_file)


def load_station_details_html(station_code: str) -> str:
    """Load station HTML for one station as json text from a suitable file; return it."""
    with open(
        station_details_html_local_path(station_code), "r"
    ) as station_details_html_local_file:
        station_details = station_details_html_local_file.read()
    return station_details


#####
# Fourth: Big download routines


def download_one_station(station_code: str):
    """
    Download one of Amtrak's station details files.

    Usually used directly when a hiccup has screwed up one of the downloads.
    """
    print(station_code)
    station_details = download_station_details(station_code)
    save_station_details(station_code, station_details)
    station_details_html = download_station_details_html(station_code)
    save_station_details_html(station_code, station_details_html)


def download_all_stations(sleep_secs: float = 120.0):
    """
    Download all of Amtrak's station details files.

    By pre-downloading, avoids hammering Amtrak's website

    sleep_secs: Sleep between downloads for this many secs (a float)
    to avoid hammering Amtrak's website.
    """
    # First, get the main station database
    stations_json = download_stations_json()
    save_stations_json(stations_json)

    # Add a random delay of 0-60 seconds
    if sleep_secs != 0.0:
        rand_secs = random.random() * 60
        sleep(sleep_secs + rand_secs)

    # Then, cycle through the station codes
    # Have to set up a StringIO wrapper
    stations_json_as_file = StringIO(stations_json)
    # This line just works!
    stations = pd.io.json.read_json(stations_json_as_file, orient="records")
    for code in stations["code"].array:
        download_one_station(code)
        if sleep_secs != 0.0:
            rand_secs = random.random() * 60
            sleep(sleep_secs + rand_secs)
        # When debugging, don't loop...
        # break


#####
# Fifth: preparing the station name dictionary

# For getting station names from station codes.

# This is cached.
# It is filled by make_station_name_dict
station_name_dict = None


def get_station_name(station_code: str) -> str:
    """
    Given an Amtrak station code, return the long station name.

    Creates a dict on first invocation, uses the dict subsequently.
    """
    global station_name_dict
    if station_name_dict is None:
        station_name_dict = make_station_name_dict()
    return station_name_dict[station_code]


def make_station_name_dict():
    """
    Return a dict which takes a station code and returns a suitable printable station name.

    Expects json stations to be downloaded already, in a suitable local file
    """
    stations_json = load_stations_json()

    # Have to set up a StringIO wrapper
    stations_json_as_file = StringIO(stations_json)
    # This line just works!
    stations = pd.io.json.read_json(stations_json_as_file, orient="records")
    return dict(zip(stations.code, stations.autoFillName))


######
# Sixth: Processing the station data

# Notes on station details:
# stationAlias is alternate search terms to find the station (often absent)
# state is like "CA"
# name is like "Riverside, CA" -- it's not the station name, but the city name
# code is the station code
# city is like "Riverside" -- again, not station name
# stationName32 is the primary name, like "Moreno Valley, CA"
# facilityName32 is the subtitle, like "Back Bay Station" -- not always present
# facilityName64 is an alternate subtitle (often worse -- longer)
# "autoFillName" is the full name with the code in parentheses
#     like "Barstow, CA - Harvey House Railroad Depot (BAR)"
# "timezone" is P, M, C, or E
# "country" is usually blank, or CA for Canada.  No Mexico.

#
# The station address is nowhere.  It's on the main webpage instead, on the
# "hero-banner-and-info__card_block-address"
# and also the
# "hero-banner-and-info__car_station-type"
# It has to be scraped separately.  Yuck.


def do_station_processing():
    # EXPERIMENTAL AND INCOMPLETE AND DUPLICATES CODE
    local = True
    # stations_json = None # fill in next
    if local:
        stations_json = load_stations_json()
    else:
        stations_json = download_stations_json()

    # Believe it or not, this line JUST WORKS!!!!  Wow!
    # Have to set up a StringIO wrapper
    stations_json_as_file = StringIO(stations_json)
    # This line just works!
    stations = pd.io.json.read_json(stations_json_as_file, orient="records")

    # OK.  So let's dump-print that table...
    stations_csv_path = Path("./stations.csv")
    stations.to_csv(stations_csv_path, index=False)
    print("stations.csv dumped")
    # Note: 'country' is blank or CA for Canada (nothing else); stationAlias is of little value

    # FIXME: the following is not actually doing anything at this time

    # OK, so there are stations with defective details JSON records (aaaargh!)
    # Should report that to Amtrak TODO
    # BAT has a webpage.  The others are just blank.
    # Originally on this list but fixed: MOH

    station_list = stations["code"].array
    bad_station_list = []
    for code in station_list:
        station_details_json = load_station_details(code)
        if station_details_json in ["{}", "{}\n"]:  # Quick and dirty; FIXME
            bad_station_list.append(code)
        parsed_json = json.loads(station_details_json)
    # bad_station_list = ["BAT","BNN","DTR","PDT","AVC","TAP","WBT"]
    bad_station_list_path = Path("./bad_stations.csv")

    # Use PANDAS to dump to file, one per line
    df = pd.DataFrame(bad_station_list)
    df.to_csv(bad_station_list_path, index=False, header=False)
    print("bad_stations.csv dumped")

    cleaned_station_list = list(
        filter(lambda x: not x in bad_station_list, station_list)
    )
    return cleaned_station_list


def make_arg_parser():
    """Make argument parser for amtrak/json_stations.py"""
    arg_parser = argparse.ArgumentParser(
        description="""Download and/or run tests on Amtrak's JSON stations data.  With no arguments, does nothing."""
    )
    subparsers = arg_parser.add_subparsers(dest="command_name")
    download_parser = subparsers.add_parser(
        "download",
        help="Download Amtrak stations data; otherwise a local copy must exist",
        aliases=["down", "d"],
    )
    download_parser.add_argument(
        "--station-code",
        "--station",
        "--code",
        "-c",
        help="Station code to download.  If not specified, downloads all stations.",
        dest="station_code",
    )
    download_parser.add_argument(
        "--sleep",
        "-s",
        help="Number of seconds to wait between downloads.  Used to avoid hammering Amtrak's servers.  Default 2.0.",
        dest="sleep_secs",
        type=float,
        default=float(2.0),
    )
    process_parser = subparsers.add_parser(
        "process",
        help="Process Amtrak stations data, running tests; a local copy must exist. INCOMPLETE",
        aliases=["p"],
    )
    arg_parser.add_argument(
        "--directory",
        "-d",
        help="""Local directory to store Amtrak JSON station details in.
Default is within the module timetable_kit/amtrak/stations; but this might not be writable.
Another good option is ./amtrak_stations""",
        dest="stations_dir_name",
    )
    return arg_parser


# MAIN PROGRAM
if __name__ == "__main__":
    arg_parser = make_arg_parser()
    args = arg_parser.parse_args()

    if args.command_name is None:
        arg_parser.print_help()

    # This is ugly, clean it up later
    if args.stations_dir_name:
        # Possibly change the stations directory path globals
        # NOTE, we are not in a function so do not need global keyword
        station_details_dir = Path(args.stations_dir_name)
    # Create the directory if it does not exist
    if not station_details_dir.exists():
        station_details_dir.mkdir(parents=True)

    if args.command_name == "download":
        if args.station_code is None:
            download_all_stations(sleep_secs=args.sleep_secs)
        else:
            download_one_station(str.upper(args.station_code))
    if args.command_name == "process":
        do_station_processing()
    sys.exit(0)
