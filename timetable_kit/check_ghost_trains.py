#! /usr/bin/env python3
# check_ghost_trains.py
# Part of timetable_kit
# Copyright 2023 Christopher Juckins & Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This program essentially compares two lists:

a) The list of trains in a .csv spec file that we think are running
b) The list of trains from an external .txt file that are actually running

It will print differences so manual tweaks to the .csv can be done.

The external .txt files for trains actually running are on 
https://juckins.net/timetable_kit/trains_running/

Example filename: trains-actually-running-empire-service.txt

The following is the list of route names as given in Amtrak's Track-A-Train data
(converted to lowercase, any spaces or slashes replaced with a "-") that are
used in the .txt files:

acela
adirondack
amtrak-cascades
auto-train
california-zephyr
capitol-corridor
capitol-limited
cardinal
carolinian-piedmont
city-of-new-orleans
coast-starlight
crescent
downeaster
empire-builder
empire-service
ethan-allen-express
heartland-flyer
hiawatha
illinois-service
keystone
lake-shore-limited
lincoln-service-missouri-river-runner
maple-leaf
michigan-services
missouri-river-runner
northeast-regional
pacific-surfliner
pennsylvanian
san-joaquins
silver-service-palmetto
southwest-chief
sunset-limited
texas-eagle
vermonter
winter-park-express

Adirondack is missing but will likely come back in the future.
"""

import argparse
import re
from urllib.request import Request, urlopen  # for reading juckins webpage

from timetable_kit.sew_pages import (
    read_list_file,
)
from timetable_kit.timetable import (
    load_ttspec_csv,
    train_specs_list_from_tt_spec,
    flatten_train_specs_list,
)
from timetable_kit.tsn import (
    train_spec_to_tsn,
)

# This only works on a specific list of preprogrammed services.
# The keys are names of the services which can be given to this program
# at the command line.
# Each entry's value is a dict with two keys.
# "list_file" gives a .list file in specs_amtrak/
# "route_names" gives a list for looking up in juckins's table of trains actually running.
prepared_timetables = {
    "nec": {
        "list_file": "nec-bos-was.list",
        "route_names": [
            "acela",
            "northeast-regional",
            "vermonter",
            "keystone",
            "pennsylvanian",
            "cardinal",
            "carolinian-piedmont",
            "crescent",
            "silver-service-palmetto",
        ],
    },
    "empire-service": {
        "list_file": "empire-service.list",
        "route_names": [
            "empire-service",
            "ethan-allen-express",
            "adirondack",
            "maple-leaf",
            "lake-shore-limited",
        ],
    },
    "keystone-service": {
        "list_file": "keystone-service.list",
        "route_names": [
            "keystone-service",
            "pennsylvanian",
        ],
    },
}


def make_argparser():
    """
    Generate argument parser for check_ghost_trains.py
    """
    parser = argparse.ArgumentParser(
        description="""Check CSV spec files for Amtrak routes against lists of trains actually running from juckins.net""",
    )
    parser.add_argument(
        "timetable",
        help="Timetable to check for",
        choices=prepared_timetables.keys(),
    )
    return parser


def get_csvs_from_list(filename, input_dir):
    """Given a .list file, get the list of CSV train spec filepaths"""
    raw_list = read_list_file(filename, input_dir=input_dir)
    cooked_list = [input_dir + "/" + item + ".csv" for item in raw_list]
    return cooked_list


def get_trains_from_csv(filename):
    """Given a CSV train spec file, get the list of trains in it"""
    # Get the CSV as a Pandas DataFrame
    tt_spec_csv = load_ttspec_csv(filename)
    # Extract the train specs from the top row as a list
    train_specs_list = train_specs_list_from_tt_spec(tt_spec_csv)
    # Flatten 48/448 notations, eliminate "noheader" suffixes
    flattened_train_specs_set = flatten_train_specs_list(train_specs_list)
    # Eliminate "monday", "tuesday" etc suffixes
    flattened_tsn_list = [
        train_spec_to_tsn(train_spec) for train_spec in flattened_train_specs_set
    ]
    return flattened_tsn_list


def get_trains_from_juckins(route_name):
    """Get a list of trains actually running on a given route from juckins.net"""
    # Get the webpage
    url_basename = "https://juckins.net/timetable_kit/trains_running"
    url_prefixfilename = "trains-actually-running"
    url_routename = route_name
    url_to_open = "".join(
        [url_basename, "/", url_prefixfilename, "-", url_routename, ".txt"]
    )
    print("url to open:", url_to_open)

    # Get the file and print out contents
    req = Request(url=url_to_open, headers={"User-Agent": "Mozilla/5.0"})
    webpage = urlopen(req).read().decode("utf-8")

    # Split each line from the webpage into a list
    # Note this includes the 2 header lines that we remove later
    train_num_list = webpage.split("\n")

    # Print the first two lines, they have useful information
    print(train_num_list[0], train_num_list[1])

    # Remove any blank strings from our list
    while "" in train_num_list:
        train_num_list.remove("")

    # Create and print our final list for comparison
    # Ignore the first 2 header lines
    return train_num_list[2:]


if __name__ == "__main__":
    my_arg_parser = make_argparser()
    args = my_arg_parser.parse_args()

    # ---
    # Section to download external test file and read into list
    # ---
    route_names = prepared_timetables[args.timetable]["route_names"]
    trains_running = []
    for route_name in route_names:
        trains_running.extend(get_trains_from_juckins(route_name))
    print("Trains running on", route_names)
    print(trains_running)

    #
    # Section to get trains listed in csv
    input_dir = "./specs_amtrak"
    list_file = prepared_timetables[args.timetable]["list_file"]
    full_filenames = get_csvs_from_list(list_file, input_dir)
    print("Checking CSVs:", full_filenames)
    trains_listed = []
    for ff in full_filenames:
        for train_num in get_trains_from_csv(ff):
            if train_num not in trains_listed:
                trains_listed.append(train_num)
    print("Trains listed in CSVs:", trains_listed)

    # ---
    # Comparison
    # ---

    missing_from_csv = list(set(trains_running).difference(trains_listed))
    # Filter out false positives for the NEC
    if args.timetable == "nec":
        print("Excluding 6XX-series (PHL-HAR)")
        print("Excluding 4XX-series (NHV-points north)")
        print("Excluding 7X-series (RGH-CLT)")
        real_missing = []
        for x in missing_from_csv:
            if re.fullmatch(r"4\d\d", x):
                pass
            elif re.fullmatch(r"6\d\d", x):
                pass
            elif re.fullmatch(r"7\d", x):
                pass
            else:
                real_missing.append(x)
        missing_from_csv = real_missing
    print("trains running but not in CSV:", missing_from_csv)

    ghost_trains = list(set(trains_listed).difference(trains_running))
    print("ghost trains (in CSV but not running):", ghost_trains)

    print("")
