#! /usr/bin/env python3
# amtrak/station_type.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Make various dicts from station code to whether the station is a train station or a
bus stop.

Also, runnable as a script to get the same information.

Requires local copy of Amtrak stations database: That local copy is generated by "json_stations.py download"
This has very similar code to baggage.py
"""

import sys  # for sys.exit
from io import StringIO  # Needed to parse JSON
import pandas as pd

# For parsing the HTML pages
import lxml.html

from timetable_kit.amtrak.json_stations import (
    load_stations_json,
    load_station_details_html,
)

# These are mine
from timetable_kit.debug import set_debug_level, debug_print

# This is a map from what we might see in the web page,
# to the key information in the form:
# [train or bus, shelter type]
# Since train_or_bus is used in detecting Amtrak's ADA compliance,
# if it's a train station for not-Amtrak-only, we consider it a bus stop.
station_types_decoding_map = {
    # This is the most basic curbside bus stop
    "Bus Stop - Curbside Bus Stop only (no shelter)": [0, 0],
    # Misprinted at LVP and SQM:
    "Curbside Bus Stop only (no shelter)": [0, 0],
    # This is too, but when at a transit center?
    "Bus Station - Curbside Bus Stop only (no shelter)": [0, 0],
    # I don't know why this is different: wheelchair access maybe?
    # I think it's off-street, but usually at random restaurants
    "Bus Stop - Platform only (no shelter)": [0, 0],
    # This is only found at WBT (West Oakland BART).
    # You can wait inside the station.
    "Bus Station - Platform only (no shelter)": [0, 1],
    # Ferry Terminals are inevitably used as bus stops by Amtrak
    # This is only found at BRI (Bristol, RI)
    "Ferry Terminal - Platform only (no shelter)": [0, 0],
    # There are several of these.  What even IS this?
    # It's used at Green Bay, but also at Metrolink stations in California
    # and Morgan Hill Caltrain station in California
    # And Green Bay, Blacksburg, VA, Woodburn, OR, and Wheatland, Wyoming Arby's.
    "Bus Stop - Platform with Shelter": [0, 1],
    # This is only found at WIC (Wichita, Kansas).  Why?
    "Bus Station - Platform with Shelter": [0, 1],
    # These are bus stops with a third-party (resort etc.) waiting room
    "Bus Stop - Station Building (with waiting room)": [0, 2],
    # These are proper transit center type bus stations
    "Bus Station - Station Building (with waiting room)": [0, 2],
    # Ferry Terminals are inevitably used as bus stops by Amtrak
    "Ferry Terminal - Station Building (with waiting room)": [0, 2],
    # This is only found at Livermore, CA (LIV).
    # It's a train station for someone else, not for Amtrak.
    "Train Station - Curbside Bus Stop only (no shelter)": [0, 0],
    # Typical rural train station
    "Train Station - Platform only (no shelter)": [1, 0],
    # Slightly better rural train station
    "Train Station - Platform with Shelter": [1, 1],
    # Nice train station
    "Train Station - Station Building (with waiting room)": [1, 2],
}


# This is a global filled on first use
train_or_bus_dict: dict[str, bool] | None = None
shelter_dict: dict[str, bool] | None = None


def is_train_station(station_code: str) -> bool:
    """Is this a train station (not a bus station)?

    Constructs and caches the data on first call. Requires that the JSON stations
    database already be downloaded.
    """
    if train_or_bus_dict is None:
        make_station_type_dicts()
    assert train_or_bus_dict is not None  # Silence MyPy
    return train_or_bus_dict[station_code]


def has_shelter(station_code: str) -> bool:
    """Does this train station have a building, or does this bus stop have a building?

    Constructs and caches the data on first call. Requires that the JSON stations
    database already be downloaded.
    """
    if shelter_dict is None:
        make_station_type_dicts()
    assert shelter_dict is not None  # Silence MyPy
    return shelter_dict[station_code]


def make_station_type_dicts() -> None:
    """Make dicts which map from station code to train or bus, and shelter or not.

    These are globals within this module.
    """
    stations_json = load_stations_json()

    # Believe it or not, this line JUST WORKS!!!!  Wow!
    stations = pd.io.json.read_json(StringIO(stations_json), orient="records")
    station_list = stations["code"].to_list()

    global train_or_bus_dict
    global shelter_dict
    train_or_bus_dict = {}
    shelter_dict = {}

    print("Collecting station type information...")
    for station_code in station_list:
        station_details_html = None
        station_details_html = load_station_details_html(station_code)

        # This is the part where we use the lxml library.
        html_tree = lxml.html.fromstring(station_details_html)
        description_list = html_tree.xpath(
            # '//h5[@class="hero-banner-and-info__card_station-type"]/text()'
            # it could have additional classes, so the search has to be more complicated
            '//h5[contains(concat(" ",@class," ")," hero-banner-and-info__card_station-type ")]/text()'
        )
        # For exotic reasons, the description is returned in a list.
        # This is usually a one-item list, but occasionally it comes out
        # as a multiple item list with duplicates.
        assert isinstance(description_list, list)  # Silence MyPy
        if not description_list:
            print(f"No description for {station_code}")
            continue
        if len(description_list) > 1:
            print(f"Excess description for {station_code} : {description_list}")
            # Only happens at VBC, and the two descriptions are identical
        assert isinstance(description_list[0], str)  # Silence MyPy
        # May have stray newlines and whitespace; remove this
        description = description_list[0].strip()
        if description not in station_types_decoding_map:
            print(f"Unexpected description for {station_code} : {description}")
            # Fill... something in.
            train_or_bus_dict[station_code] = False
            shelter_dict[station_code] = False
        else:
            [train_or_bus, shelter] = station_types_decoding_map[description]
            train_or_bus_dict[station_code] = bool(train_or_bus)
            shelter_dict[station_code] = bool(shelter_dict)
    print("Station type dicts made.")
    return


# TESTING
# This accepts a station code and gives information about it
if __name__ == "__main__":
    set_debug_level(2)
    station_code = sys.argv[1].upper()
    print(
        station_code,
        "is train station?",
        is_train_station(station_code),
        "has shelter?",
        has_shelter(station_code),
    )
