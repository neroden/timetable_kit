#! /usr/bin/env python3
# amtrak_json_stations.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Routines for extracting Amtrak's JSON station data and working with it.
Amtrak's entire station database is exposed as JSON, which is very useful.
"""

# "./json_stations.py download"
# will download Amtrak's station files into the './stations/' directory
# otherwise runs test case

from pathlib import Path
import sys
import pandas as pd
import requests
import json # better for the details import
# from time import sleep # Avoid slamming Amtrak's server too fast -- not needed
import argparse

# SO.  It turns out that Amtrak's station database is exposed as JSON.  Here are the key URLs.

# INITIALIZATION CODE
# GLOBAL VARIABLES
# This is the station detail list for one station.
station_details_url_prefix = "https://www.amtrak.com/content/amtrak/en-us/stations/"
station_details_url_infix = ".stationTabContainer."
station_details_url_postfix = ".json"

# This is the entire station list as json -- names and all.
stations_json_url = "https://www.amtrak.com/services/data.stations.json"

# Now, where to put the local cached copy?
# module_location = Path(__file__).parent
# stations_under_module = module_location / "stations"
#
# working_directory = Path(".")
# stations_under_wd = working_directory / "stations"

station_details_dir = Path("./amtrak_stations")

def stations_json_local_path():
    """Return local path for the data.stations.json file as a Path"""
    return station_details_dir / "data.stations.json"

def station_details_filename(station_code: str) -> str:
    """Return filename for a Amtrak station details JSON file"""
    # Step one: validate the station code
    if (len(station_code) != 3):
        raise ValueError("Station code not of length 3")
    # This might well be case sensitive
    first_station_code = str.lower(station_code)
    second_station_code = str.upper(station_code)
    filename = ''.join([
                   first_station_code,
                   station_details_url_infix,
                   second_station_code,
                   station_details_url_postfix
                   ])
    return filename;

def station_details_url(station_code: str) -> str:
    """
    Given an Amtrak station code, return the URL for the station details in JSON form.

    Watch out for "403 forbidden" issues...
    """
    # Step one: validate the station code
    if (len(station_code) != 3):
        raise ValueError("Station code not of length 3")
    filename = station_details_filename(station_code)
    url = ''.join([station_details_url_prefix,
                   filename,
                   ])
    return url;

def station_details_local_path(station_code: str) -> str:
    """Return local pathname for an Amtrak station details JSON file"""
    # Step one: validate the station code
    if (len(station_code) != 3):
        raise ValueError("Station code not of length 3")
    filename = station_details_filename(station_code)
    path = station_details_dir / filename
    return path;

def download_stations_json() -> str:
    """Download Amtrak's basic stations database as json text; return it."""
    # This uses the 'requests' package to download it
    response = requests.get(stations_json_url)
    return response.text

def save_stations_json(stations_json: str):
    """Save Amtrak's basic stations databse (json text) to a suitable file."""
    with open(stations_json_local_path(),'w') as stations_json_local_file:
        print ( stations_json, file=stations_json_local_file )

def load_stations_json():
    """Load Amtrak's basic stations databse (json text) from a suitable file.  Return it."""
    with open(stations_json_local_path(),'r') as stations_json_local_file:
        stations_json = stations_json_local_file.read()
    return stations_json

# This one is called by the main timetable program.
def make_station_name_lookup_table():
    """
    Return a dict which takes a station code and returns a suitable printable station name.

    Expects json stations to be downloaded already, in a suitable local file
    """
    stations_json = load_stations_json()
    # Believe it or not, this line JUST WORKS!!!!  Wow!
    stations = pd.io.json.read_json(stations_json,orient='records')
    lookup_station_name = dict( zip(stations.code, stations.autoFillName) )
    return lookup_station_name

def download_station_details(station_code: str) -> str:
    """Download station details for one station as json text; return it."""
    response = requests.get(station_details_url(station_code))
    return response.text

def save_station_details(station_code: str, station_details: str):
    """Save station details for one station to a suitable file."""
    with open(station_details_local_path(station_code),'w') as station_details_local_file:
        print ( station_details, file=station_details_local_file)

def load_station_details(station_code: str) -> str:
    """Load station details for one station as json text from a suitable file; return it."""
    with open(station_details_local_path(station_code),'r') as station_details_local_file:
        station_details = station_details_local_file.read()
    return station_details

def download_all_stations():
    """
    Download all of Amtrak's station details files.

    By pre-downloading, avoids hammering Amtrak's website
    """
    # First, get the main station database
    stations_json = download_stations_json()
    save_stations_json(stations_json)

    # Then, cycle through the station codes
    stations = pd.io.json.read_json(stations_json,orient='records')
    for code in stations["code"].array:
        print (code)
        station_details = download_station_details(code)
        save_station_details(code, station_details)
        # When debugging, don't loop...
        # break
        # This is where I considered adding a 'sleep' statement but it worked without it
        #sleep(0.05)


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
    local=True
    # stations_json = None # fill in next
    if local:
        stations_json = load_stations_json()
    else:
        stations_json = download_stations_json()

    # Believe it or not, this line JUST WORKS!!!!  Wow!
    stations = pd.io.json.read_json(stations_json,orient='records')

    # OK.  So let's dump-print that table...
    stations_csv_path = Path("./stations.csv")
    stations.to_csv(stations_csv_path, index=False)
    print ("stations.csv dumped")
    # Note: 'country' is blank or CA for Canada (nothing else); stationAlias is of little valu

    # OK, so there are stations with defective details JSON records (aaaargh!)
    # Should report that to Amtrak TODO
    # BAT has a webpage.  The others are just blank.
    station_list = stations["code"].array
    bad_station_list = ["BAT","MOH", "BNN","DTR","PDT","AVC","TAP","WBT"]
    cleaned_station_list = list(filter(lambda x : not x in bad_station_list, station_list))
    return cleaned_station_list;

def make_arg_parser():
    # Argument parser setup code
    arg_parser = argparse.ArgumentParser(
        description='''Download and/or run tests on Amtrak's JSON stations data.  With no arguments, does nothing.'''
        )
    arg_parser.add_argument('--download',
        help='Download Amtrak stations data; otherwise a local copy must exist',
        dest='download',
        action='store_true',
        )
    arg_parser.add_argument('--process',
        help='Process Amtrak stations data, running tests; a local copy must exist. INCOMPLETE',
        dest='process',
        action='store_true',
        )
    arg_parser.add_argument('--directory','-d',
        help='Local directory to store Amtrak JSON station details in: default is [module]/stations',
        dest='stations_dir_name',
        )
    return arg_parser;

# MAIN PROGRAM
if __name__ == "__main__":

    arg_parser = make_arg_parser()
    args = arg_parser.parse_args()

    # This is ugly, clean it up later
    if (args.stations_dir_name):
        # Possibly change the stations directory path globals
        # NOTE, we are not in a function so do not need global keyword
        station_details_dir = Path(args.stations_dir_name)
    # Create the directory if it does not exist
    if not ( station_details_dir.exists() ):
        station_details_dir.mkdir(parents=True)

    if (args.download):
        download_all_stations()
    if (args.process):
        do_station_processing()
