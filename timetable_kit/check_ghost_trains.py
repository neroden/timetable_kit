#! /usr/bin/env python3
# check_ghost_trains.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
# Initial version started by Christopher Juckins

import sys
from urllib.request import Request, urlopen


"""
This program essentially compares two lists:

a) The list of trains in a .csv spec file that we think are running
b) The list of trains from an external .txt file that are actually running

It will print differences so manual tweaks to the .csv can be done.

The external .txt files for trains actually running are on 
https://juckins.net/timetable_kit/trains_running/

The following is the list of route names as given in Amtrak's Track-A-Train data
(converted to lowercase, any spaces or slashes replaced with a "-") that are
used in the .txt files:

acela
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

Example filename: trains-actually-running-empire-service.txt
"""

# TO DO:
#
# Add in NN's csv-checker code provided via email
"""
Now, leaning on the code I've already written, this code should import a list 
of train numbers from a single .csv file...
...I should probably refactor this a little and move some of these subroutines
into different files, but anyway this should work.  Assuming you have your 
venv set up with timetable_kit and pandas.

from timetable_kit.timetable import (
    load_ttspec_csv,
    train_specs_list_from_tt_spec,
    flatten_train_specs_list,
)
from timetable_kit.tsn import (
    train_spec_to_tsn,
)

# Get the CSV as a Pandas DataFrame
tt_spec_csv = load_ttspec_csv(filename)
# Extract the train specs from the top row as a list
train_specs_list = train_specs_list_from_tt_spec(tt_spec)
# Flatten 48/448 notations, eliminate "noheader" suffixes
flattened_train_specs_set = flatten_train_specs_list(train_specs_list)
# Eliminate "monday", "tuesday" etc suffixes
flattened_tsn_list = [
    train_spec_to_tsn(train_spec) for train_spec in flattened_train_specs_set
]

This leaves only the process of reading the arguments list to get the filenames,
the process of importing the list of trains_running (which is probably 
newline-separated? space-separated?), and the process of looping over 
multiple CSV files and merging the lists from different CSV files.
"""

if __name__ == "__main__":
    
    #--- 
    # Quick comparison framework test
    #---
    csv_input = ["20", "66", "174"]
    print('csv_input: ', csv_input)

    trains_running = ["20", "80", "174"]
    print('trains_running: ', trains_running)
    
    missing_from_csv_input = list(set(trains_running).difference(csv_input))
    print('missing_from_csv_input:', missing_from_csv_input)
    
    csv_ghost_train = list(set(csv_input).difference(trains_running))
    print('csv_ghost_train: ', csv_ghost_train)
    print('')


    #---
    # Section to download external test file and read into list
    #---
    url_basename = 'https://juckins.net/timetable_kit/trains_running'
    url_prefixfilename = 'trains-actually-running'
    url_routename = 'empire-service'
    url_filename = url_prefixfilename + '-' + url_routename + '.txt'
    url_to_open = url_basename + '/' + url_filename
    print('url to open', url_to_open)

    # Get the file and print out contents
    req = Request(
        url = url_to_open,
        headers = {'User-Agent': 'Mozilla/5.0'}
        )
    webpage = urlopen(req).read().decode('utf-8')
    print('')
    print(webpage)

    # Split each line from the webpage into a list
    # Note this includes the 2 header lines that we remove later
    train_num_list = webpage.split('\n')
    #print('train_num_list: ', train_num_list)

    # Remove any blank strings from our list
    while("" in train_num_list):
        train_num_list.remove("")

    # Print our list, but ignore first 2 lines
    #print('Trains running on', train_num_list[0])
    #number_of_lines = len(train_num_list)
    #for i in range(2, number_of_lines):
    #    print(train_num_list[i])

    # Create and print our final list for comparison
    # Ignore the first 2 header lines
    train_num_list_compare = list()
    number_of_lines = len(train_num_list)
    for i in range(2, number_of_lines):
        train_num_list_compare.append(train_num_list[i])
    print('Trains running on', train_num_list[0])
    print(train_num_list_compare)
    

