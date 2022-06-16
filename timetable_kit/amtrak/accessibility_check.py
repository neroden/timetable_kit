#! /usr/bin/env python3
# amtrak/accessibility_check.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Take Amtrak's station database and process it to find deficits in accessibility.

Output will go in the "station_stats" folder

Requires local copy of Amtrak stations database: That local copy is generated by "json_stations.py download"

Requires local bad_stations.csv file: That is generated by "json_stations.py process"
"""
import sys  # for sys.exit
from pathlib import Path
import json

import pandas as pd

# These are mine
from timetable_kit.amtrak import json_stations
from timetable_kit.amtrak.json_stations import (
    load_stations_json,
    load_station_details,
)

# To filter out that which is not a train station
from timetable_kit.amtrak.station_type import is_train_station

# FIXME: this should be relative to something.
base_dir = Path(__file__).parent
station_stats_dir = base_dir / "station_stats"
stations_csv_path = station_stats_dir / "json_stations.csv"
bad_stations_path = base_dir / "bad_stations.csv"


def make_station_stats():
    stations_json = load_stations_json()

    # Believe it or not, this line JUST WORKS!!!!  Wow!
    stations = pd.io.json.read_json(stations_json, orient="records")
    # OK.  So let's dump-print that table...
    stations.to_csv(stations_csv_path, index=False)
    print(str(stations_csv_path) + " dumped.")
    # Note: 'country' is blank or CA for Canada (nothing else); stationAlias is of little value

    station_list = stations["code"].array

    # Amtrak has stations with defective and missing JSON records.
    # We detect these in json_stations.py process
    # Then put them in a file (one station per line), which we read here
    bad_station_df = pd.read_csv(bad_stations_path, header=None)
    bad_station_list = bad_station_df[0].array
    print("Omitting bad stations:")
    print(bad_station_list)
    cleaned_station_list = list(
        filter(lambda x: not x in bad_station_list, station_list)
    )

    # These are sets, so the "add only if not present" logic is automatic
    possible_features = set(())
    possible_baggage = set(())
    possible_parking = set(())
    possible_accessibility = set(())
    # Hours are different, don't try the same trick
    # possible_hours = set(())

    # Simultaneously accumulate certain lists of stations...
    inaccessible_platforms = set(())
    no_wheelchair_lifts = set(())
    high_platforms = set(())

    for code in cleaned_station_list:
        print("Analyzing " + code)
        station_details_json = None
        station_details_json = load_station_details(code)

        # The details aren't in a form where pd.io.json.read_json likes it
        # Works better to use json.load on the json... process later
        # Need "loads" to load from string
        parsed_json = json.loads(station_details_json)
        # Exactly five tabs in details -- if this fails, add to the bad_station_list above
        feature_json = parsed_json["feature"]
        baggage_json = parsed_json["baggage"]
        parking_json = parsed_json["parking"]
        accessibility_json = parsed_json["accessibility"]
        hours_json = parsed_json["hours"]

        if False:
            # This is a sanity check on Amtrak's data.
            del parsed_json["feature"]
            del parsed_json["baggage"]
            del parsed_json["parking"]
            del parsed_json["accessibility"]
            del parsed_json["hours"]
            if parsed_json:
                print("Whoops, extra JSON information for station " + code)

        # We ignore the keys other than "feature" and pull out the strings after "feature"
        # We know there are some {} dicts so we have to check for the feature key presence
        for x in feature_json:
            if "feature" in x:
                possible_features.add(x["feature"])
        for x in baggage_json:
            if "feature" in x:
                possible_baggage.add(x["feature"])
        for x in parking_json:
            if "feature" in x:
                possible_parking.add(x["feature"])
        for x in accessibility_json:
            if "feature" in x:
                possible_accessibility.add(x["feature"])
                # Track the list of inaccessible stations.  Ignore bus stops.
                if x["feature"] == "No accessible platform":
                    if is_train_station(code):
                        inaccessible_platforms.add(code)
                if x["feature"] == "No wheelchair lift":
                    if is_train_station(code):
                        no_wheelchair_lifts.add(code)
                if x["feature"] == "High platform":
                    if is_train_station(code):
                        high_platforms.add(code)

    # Finally out of the loop
    print("Went through all stations, no whammies")

    with open(
        station_stats_dir / "possible_features.txt", "w"
    ) as possible_features_file:
        possible_features_file.write("\n".join(sorted(possible_features)))
    with open(station_stats_dir / "possible_baggage.txt", "w") as possible_baggage_file:
        possible_baggage_file.write("\n".join(sorted(possible_baggage)))
    with open(station_stats_dir / "possible_parking.txt", "w") as possible_parking_file:
        possible_parking_file.write("\n".join(sorted(possible_parking)))
    with open(
        station_stats_dir / "possible_accessibility.txt", "w"
    ) as possible_accessibility_file:
        possible_accessibility_file.write("\n".join(sorted(possible_accessibility)))

    with open(
        station_stats_dir / "inaccessible_platforms.txt", "w"
    ) as inaccessible_platforms_file:
        inaccessible_platforms_file.write("\n".join(sorted(inaccessible_platforms)))

    # Wheelchair lifts are not always needed at high platforms...
    # Python implements set difference:
    low_platform_no_wheelchair_lifts = no_wheelchair_lifts - high_platforms

    # No wheelchair list is not very interesting if the platform itself is inaccessible...
    interesting_no_wheelchair_lifts = (
        low_platform_no_wheelchair_lifts - inaccessible_platforms
    )

    with open(
        station_stats_dir / "no_wheelchair_lifts.txt", "w"
    ) as no_wheelchair_lifts_file:
        no_wheelchair_lifts_file.write(
            "\n".join(sorted(interesting_no_wheelchair_lifts))
        )

    print("Station stats files placed in " + str(station_stats_dir))


# MAIN PROGRAM
if __name__ == "__main__":

    if not station_stats_dir.exists():
        station_stats_dir.mkdir(parents=True)

    make_station_stats()
    sys.exit(0)
