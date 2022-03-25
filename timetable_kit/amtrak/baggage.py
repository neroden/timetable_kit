#! /usr/bin/env python3
# amtrak/baggage.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Make a dict from station code to checked baggage status (present / not present).

Requires local copy of Amtrak stations database: That local copy is generated by "json_stations.py download"
"""

from pathlib import Path
import pandas as pd
import json

# These are mine
from timetable_kit.debug import (set_debug_level, debug_print)
from timetable_kit.amtrak import json_stations
from timetable_kit.amtrak.json_stations import (
    load_stations_json,
    load_station_details,
    )

# FIXME: this should be relative to something.
#base_dir = Path(__file__).parent
#station_stats_dir = base_dir / "station_stats"
#stations_csv_path = station_stats_dir / "json_stations.csv"
#bad_stations_path = base_dir / "bad_stations.csv"

# This is a global filled on first use
checked_baggage_dict = None

def station_has_checked_baggage(station_code: str) -> bool:
    """
    Does this station have checked baggage service?

    Constructs and caches the data on first call.
    Requires that the JSON stations database already be downloaded.
    """
    global checked_baggage_dict
    if checked_baggage_dict is None:
        checked_baggage_dict = make_checked_baggage_dict()
    return checked_baggage_dict[station_code]

def make_checked_baggage_dict() -> dict[str, bool]:
    """
    Make a dict which maps from station code to whether it supports checked baggage.
    False if it doesn't;
    True if it does.
    """
    stations_json = load_stations_json()

    # Believe it or not, this line JUST WORKS!!!!  Wow!
    stations = pd.io.json.read_json(stations_json,orient='records')
    station_list = stations["code"].array

    checked_baggage_dict = {}

    for code in station_list:
        station_details_json = None
        station_details_json = load_station_details(code)
        if (station_details_json in ["{}","{}\n"]):  # Bad station
            debug_print(2, "Bad station details for", code, ": assuming no checked baggage")
            checked_baggage_dict[code] = False
        else:
            parsed_json = json.loads(station_details_json)
            # Exactly five tabs in details, one of which is "baggage".
            baggage_json = parsed_json["baggage"]

            for x in baggage_json:
                # baggage_json is a list.  Each element looks like {"feature", "blahblahblah"}.
                if "feature" in x:
                    if x["feature"] in ["Checked baggage service available "]: # Yes, with the space
                        checked_baggage_dict[code] = True
                        break
                    elif x["feature"] in ["No checked baggage service"]: # No space here
                        checked_baggage_dict[code] = False
                        break
            else: # Did not break out of the loop
                debug_print(2, "No information for", code, ": assuming no checked baggage")
                checked_baggage_dict[code] = False
    # Finally out of the loop
    return checked_baggage_dict

# TESTING
if __name__ == "__main__":
    set_debug_level(2)
    print(station_has_checked_baggage("NYP")) # This should generate and cache data
    print(station_has_checked_baggage("CHI")) # This should use cached data
    print(station_has_checked_baggage("SYR"))
    print(station_has_checked_baggage("BON"))
    quit()