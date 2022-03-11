#! /usr/bin/env python3
# get_wiki_stations.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Unused module.

Designed to pull Amtrak station data from Wikipedia.

Probably not needed because we can get it from Amtrak's website.
"""

import argparse

arg_parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''Process the list of Amtrak stations in Wikipedia.

Although Wikipedia is not an authoritative source, it can be useful when Amtrak sources are buggy or incomplete, for sanity checks and data filtering.

You must download the Wikipedia page locally first.
Since this is for debugging, it will probably never be made more elegant than this.

Input file:
  ./wikipedia/List of Amtrak stations - Wikipedia.html
Output files:
  ./wikipedia/wiki-stations.csv
    One row for each station, in alphabetical order by station code
    Will contain both train stations and bus stops
    Columns: Station code, Station name, City, State, Connections
  ./wikipedia/train-stations-only.txt
    One row for each station code in alphabetical order by station code
    Will contain only train stations

Stops without station codes will be listed on standard output for debugging.
Duplicate station codes (if any) will be listed on standard output for debugging.
'''
       )

# arg_parser.add_argument('--url',
#    help='''URL for the List of Amtrak Stations Wikipedia page''',
#    default = "https://en.wikipedia.org/wiki/List_of_Amtrak_stations",
#    )
arg_parser.add_argument('--file',
    help='''HTML file of the List of Amtrak stations Wikipedia page''',
    dest="wiki_page_filename",
    default = "./wikipedia/List of Amtrak stations - Wikipedia.html"
    )
arg_parser.add_argument('--csv-out',
    help='''CSV output filename''',
    dest="csv_filename",
    default = "./wikipedia/wiki_stations.csv"
    )
arg_parser.add_argument('--train-stations-out',
    help='''Train station list output filename''',
    dest="train_station_list_filename",
    default = "./wikipedia/train-stations-only.txt"
    )

import pandas as pd
import re

from pathlib import Path
from math import nan

# This is initialization code for split_bus_stop_name
# split_bus_stop is a compiled re, global
if (True):
    re_station_name = r"([^(]*)" # no left parens in station name
    re_whitespace = r"\s+" # minimum one space
    re_left_parenthesis = r"[(]"
    re_station_code = r"([^)]{3})" # no right parens in station code
    re_right_parenthesis = r"[)]"
    re_split_bus_stop = "".join([re_station_name,
                                 re_whitespace,
                                 re_left_parenthesis,
                                 re_station_code,
                                 re_right_parenthesis,
                                 ])
    split_bus_stop = re.compile(re_split_bus_stop)

def split_bus_stop_name(name):
    """
    Splits a name like "Place (PLC)" into two columns, ("Place","PLC")

    If formatted wrong like "Name", returns ("Name", "")
    """
    match = split_bus_stop.match(name)
    if not match:
        # Didn't match; leave stop code blank
        return (name, "")
    return match.groups()

# Main program starts here

def get_wiki_stations(wiki_page_filename, csv_filename, train_station_list_filename):

    wiki_page_path = Path(wiki_page_filename)

    wikitables = pd.read_html(wiki_page_path)
    # As of Dec 3 2021:
    # Table 0, 1 and, 2 are just Wikipedia junk ("This article has issues")
    # Table 3 is the stations
    # Table 4 is the suspended stations
    # Table 5 is the future stations
    # Table 6 is the Thruway motorcoach stations

    desired_index = pd.Index(['stop_id','stop_name','city','state','connections'])

    stations = wikitables[3]
    print(stations.columns)
    # Columns found in stations:
    # 'Station', 'Station code', 'Location', 'State or province', 'Route', 'Opened', 'Rebuilt', 'Connections'

    # Three-step process: remove unwanted columns; rename columns; reorder columns
    stations_2 = stations.drop(["Route","Opened","Rebuilt"],axis="columns")
    station_old_to_new_columns = {
                                  'Station':'stop_name',
                                  'Station code':'stop_id',
                                  'Location':'city',
                                  'State or province':'state',
                                  'Connections':'connections',
                                  }
    stations_3 = stations_2.rename(columns=station_old_to_new_columns)
    stations_4 = stations_3.reindex(columns=desired_index)

    # Must remove Lakeland and replace
    stations_5 = stations_4[stations_4.stop_name != 'Lakeland']

    # Lakeland famously needs special treatment.
    LAK_row ={'stop_id':'LAK',
        'stop_name':'Lakeland (for points north)',
        'city':'Lakeland',
        'state':'FL',
        'connections':nan}
    LKL_row ={'stop_id':'LKL',
        'stop_name':'Lakeland (for points south)',
        'city':'Lakeland',
        'state':'FL',
        'connections':nan}
    extra_stations = pd.DataFrame.from_records([LAK_row,LKL_row])

    bus_stops = wikitables[6]
    # Columns found in bus_stops: 'Stop', 'Location', 'State', 'Connection'

    # Enhance the bus stops list by splitting stop_name from stop_code
    bus_stop_long_names = bus_stops["Stop"] # This is a series
    bus_stop_name_tuple = bus_stop_long_names.apply(split_bus_stop_name)
    # Now we have a series of 2-tuples.  Reconstruct a dataframe
    new_columns = pd.DataFrame.from_records(bus_stop_name_tuple.array, columns=["stop_name","stop_id"])
    # Now append the new DataFrame to the old
    bus_stops_2 = pd.concat([bus_stops, new_columns], axis='columns')

    # Conform to the same shape as the stations table
    stops_old_to_new_columns = {
                                'Location':'city',
                                'State':'state',
                                }
    bus_stops_3 = bus_stops_2.rename(columns=stops_old_to_new_columns)
    bus_stops_4 = bus_stops_3.reindex(columns=desired_index) # Drops unwanted "Connection" table

    # Find the empty stops and complain
    no_id_stops = bus_stops_4[bus_stops_4.stop_id==""]
    print ("Stops without station codes (if any):")
    print (no_id_stops)
    # Then drop them
    # bus_stops_5 = bus_stops_4.drop(bus_stops_4.index[bus_stops_4['stop_id']==""])
    # That works, this is simpler
    bus_stops_5 = bus_stops_4[bus_stops_4.stop_id != ""]

    # Perris had the wrong station code in Wikipedia. I fixed it.

    # A few stops have two names and are marked weirdly.
    # There are not enough of these to bother writing processing code.
    # Special-case them.
    MEE_row ={'stop_id':'MEE',
        'stop_name':'Monroe - Eastbound',
        'city':'Monroe',
        'state':'WA',
        'connections':nan}
    MEW_row ={'stop_id':'MEW',
        'stop_name':'Monroe - Westbound',
        'city':'Monroe',
        'state':'WA',
        'connections':nan}
    SKE_row ={'stop_id':'SKE',
        'stop_name':'Skyhomish - Eastbound',
        'city':'Skyhomish',
        'state':'WA',
        'connections':nan}
    SKW_row ={'stop_id':'SKW',
        'stop_name':'Skyhomish - Westbound',
        'city':'Skyhomish',
        'state':'WA',
        'connections':nan}

    extra_bus_stops = pd.DataFrame.from_records([MEE_row,MEW_row,SKE_row,SKW_row])

    # There's a few errors in the bus data in Wikipedia.
    # Drop the bus stop version of BRK, which is a train station:
    bus_stops_5 = bus_stops_5[bus_stops_5.stop_id != "BRK"]
    # Drop the bus stop version of PRO, which is a train station:
    bus_stops_5 = bus_stops_5[bus_stops_5.stop_id != "PRO"]
    # Drop the first copy of Livermore (keep Livermore-Transit Center) :
    bus_stops_5 = bus_stops_5[bus_stops_5.stop_name != "Livermore"]


    # Assemble all the stops together
    small_list = pd.concat([stations_5,extra_stations])
    big_list = pd.concat([stations_5,extra_stations,bus_stops_5,extra_bus_stops])

    # And a sanity check for duplicate entries
    stop_ids = big_list["stop_id"]
    duplicate_stop_ids = stop_ids[stop_ids.duplicated()]
    print ("Duplicate station codes (if any):")
    print (duplicate_stop_ids)

    # Get the list of stations which are actual stations, not bus stops
    train_station_stop_ids = small_list["stop_id"]
    with open(train_station_list_filename,'w') as train_stations_file:
        train_stations_file.write('\n'.join(sorted(train_station_stop_ids)))
    print ("List of actual train stations output to " + train_station_list_filename)

    sorted_big_list = big_list.sort_values(by="stop_id")
    sorted_big_list.to_csv(csv_filename, index=False)
    print ("Wikipedia's station list has been output to " + csv_filename)
    return sorted_big_list

# MAIN PROGRAM
if __name__ == "__main__":
    args = arg_parser.parse_args()
    wiki_stations_list = get_wiki_stations(
                            wiki_page_filename = args.wiki_page_filename,
                            csv_filename = args.csv_filename,
                            train_station_list_filename = args.train_station_list_filename,
                            )
    # Done
