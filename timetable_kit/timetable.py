#! /usr/bin/env python3
# timetable.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Generate timetables

timetable.py is the main program for generating timetables and related things
timetable.py --help gives documentation
"""

# Other people's packages
import argparse

from pathlib import Path
import os.path # for os.path abilities
import sys # Solely for sys.path

import datetime # for current date, tommorrow, etc.

import pandas as pd
import gtfs_kit as gk
# from collections import namedtuple
# import operator # for operator.not_
from weasyprint import HTML as weasyHTML
from weasyprint import CSS as weasyCSS

# My packages: Local module imports
# Note namespaces are separate for each file/module
# Also note: python packaging is really sucky for direct script testing.
from timetable_kit.errors import (
    GTFSError,
    NoStopError,
    TwoStopsError,
    NoTripError,
    TwoTripsError,
    InputError
)
from timetable_kit.debug import (set_debug_level, debug_print)
from timetable_kit.timetable_argparse import make_tt_arg_parser

# This one monkey-patches gk.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

# To intialize the feed -- does type changes
from timetable_kit.initialize import initialize_feed

# For reversing the type changes to output GTFS again
from timetable_kit import gtfs_type_cleanup

from timetable_kit import amtrak # so we don't have to say "timetable_kit.amtrak"
# To make it easier to isolate Amtrak dependencies in the main code, we always explicitly call:
# amtrak.special_data
# amtrak.json_stations

from timetable_kit import text_presentation

# This is the big styler routine, lots of CSS; keep out of main namespace
from timetable_kit.timetable_styling import (
    get_time_column_stylings,
    style_timetable_for_html,
    finish_html_timetable,
    )

from timetable_kit.amtrak.station_name_styling import (
    amtrak_station_name_to_html,
    amtrak_station_name_to_multiline_text,
    amtrak_station_name_to_single_line_text,
    )
from timetable_kit.tsn import (
    make_trip_id_to_tsn_dict,
    make_tsn_to_trip_id_dict,
    trip_from_tsn,
    stations_list_from_tsn,
    )

### tt-spec loading and parsing code

def load_tt_spec(filename):
    """Load a tt-spec from a CSV file"""
    tt_spec = pd.read_csv(filename, index_col=False, header=None, dtype = str)
    return tt_spec

def augment_tt_spec(raw_tt_spec, *, feed, date):
    """
    Fill in the station list for a tt-spec if it has a key code.

    Cell 0,0 is normally blank.
    If it is "Stations of 59", then (a) assume there is only one tt-spec row;
    (b) get the stations for 59 and fill the rows in from that

    Requires a feed and a date (the reference date; the train may change by date).

    Note that this tucks on the end of the tt_spec.  A "second row" for column-options
    will therefore be unaffected.  Other second rows may result in confusing results.
    """
    if (pd.isna(raw_tt_spec.iloc[0,0]) ):
        # No key code, nothing to do
        return tt_spec
    key_code = str(raw_tt_spec.iloc[0,0])
    debug_print(3, "Key code: " + key_code)
    if key_code.startswith("stations of "):
        key_train_name = key_code[len("stations of "):]
        # Filter the feed down to a single date...
        today_feed = feed.filter_by_dates(date, date)
        # And pull the stations list
        stations_df = stations_list_from_tsn(today_feed, key_train_name)
        new_tt_spec = raw_tt_spec.copy() # Copy entire original spec
        new_tt_spec.iloc[0,0] = float("nan") # Blank out key_code
        newer_tt_spec = pd.concat([new_tt_spec,stations_df]) # Yes, this works
        # The problem is that it leads to duplicate indices (ugh!)
        # So fully reset the index
        newest_tt_spec = newer_tt_spec.reset_index(drop=True)
        debug_print(1, newest_tt_spec)
        return newest_tt_spec

    raise InputError("Key cell must be blank or 'stations of xxx', was ", key_code)
    return

def stations_list_from_tt_spec(tt_spec):
    """Given a tt_spec dataframe, return the station list as a list of strings"""
    stations_df = tt_spec.iloc[1:,0]
    stations_list_raw = stations_df.to_list()
    stations_list_strings = [str(i) for i in stations_list_raw]
    stations_list = [i.strip() for i in stations_list_strings if i.strip() != '']
    return stations_list

def trains_list_from_tt_spec(tt_spec):
    """Given a tt_spec dataframe, return the trains list as a list of strings"""
    trains_df = tt_spec.iloc[0,1:]
    trains_list_raw = trains_df.to_list()
    trains_list_strings = [str(i) for i in trains_list_raw]
    trains_list = [i.strip() for i in trains_list_strings]
    return trains_list

def get_column_options(tt_spec):
    """
    Given a tt_spec dataframe with column-options in row 2, return a data structure for the column options.

    This data structure is a list (indexed by column number) wherein each element is a list.
    These inner lists are either empty, or a list of options.

    Options are free-form; currently only "reverse" is defined.  More will be defined later.
    Blank columns lead to a spurious "nan", but as long as we don't check for a "nan" option, who cares?
    (Possibly fix this later.)

    The column options are specified in row 2 of the table.  If they're not there, don't call this.
    """
    def nan_to_blank(s):
        if pd.isna(s):
            return ""
        else:
            return s

    if (tt_spec.iloc[1,0] not in ["column-options", "column_options"]):
        column_count = tt_spec.shape[1]
        # What, there weren't any?  Make a list containing blank lists:
        column_options = [[]] * column_count
        return column_options
    # Now for the main version
    column_options_df = tt_spec.iloc[1,0:] # second row, all of it
    column_options_raw_list = column_options_df.to_list()
    column_options_clean_list = [nan_to_blank(s) for s in column_options_raw_list]
    column_options_nested_list = [str(i).split() for i in column_options_clean_list]
    debug_print(1, column_options_nested_list)
    return column_options_nested_list

def split_trains_spec(trains_spec):
    """
    Given a string like "59 / 174 / 22", return a structured list:

    [["59, "174", "22"], True]

    Used to separate specs for multiple trains in the same timetable column.
    A single "59" will simply give {"59"}.

    A leading minus sign (-) means the column is reversed (read bottom to top);
    this is stripped by this method.
    """
    # Remove leading whitespace and possible leading minus sign
    clean_trains_spec = trains_spec.lstrip()

    raw_list = clean_trains_spec.split("/")
    clean_list = [item.strip() for item in raw_list] # remove whitespace again
    return clean_list

def flatten_trains_list(trains_list):
    """
    Take a nested list of trains and make a flast list of trains.

    Take a list of trains as specified in a tt_spec such as [NaN,'174','178/21','stations','23/1482']
    and make a flat list of all trains involved ['174','178','21','23','1482']
    without the special keywords like "station".
    """
    flattened_trains_list = []
    for ts in trains_list:
        train_nums = split_trains_spec(ts) # Separates at the "/"
        flattened_trains_list = [*flattened_trains_list, *train_nums]
    flattened_trains_set = set(flattened_trains_list)
    flattened_trains_set.discard("station")
    flattened_trains_set.discard("stations")
    flattened_trains_set.discard("services")
    flattened_trains_set.discard("")
    return flattened_trains_set

#### Subroutines for fill_tt_spec

def service_dates_from_trip_id(feed, trip_id):
    """
    Given a single trip_id, get the associated service dates by looking up the service_id in the calendar

    Returns an ordered pair (start_date, end_date)
    """
    # FIXME: The goal is to get the latest start date and earliest end date
    # for all trains in a list.  Do this in a more "pandas" fashion.
    service_id = feed.trips[feed.trips.trip_id == trip_id]["service_id"].squeeze()

    calendar_row = feed.calendar[feed.calendar.service_id == service_id]

    start_date = (calendar_row.start_date).squeeze()
    end_date = (calendar_row.end_date).squeeze()

    return [start_date, end_date]

def get_calendar_from_tsn (today_feed, trip_short_name):
    """
    Given a single train number (trip_short_name), and a feed containing only one day,
    extract the single calendar line for that train.
    """
    trip = trip_from_tsn(today_feed, trip_short_name)
    calendar = today_feed.calendar[today_feed.calendar.service_id == trip.service_id]
    # Slower version:
    # this_feed = today_feed.filter_by_service_ids([trip.service_id])
    # calendar = this_feed.calendar
    return calendar

def get_timepoint_from_tsn (today_feed, trip_short_name, station_code):
    """
    Given a single train number (trip_short_name),  station_code, and a feed containing only one day, extract a single timepoint.

    This wraps get_timepoint_from_trip_id.

    Converting from trip_short_name to trip_id is slow, so we don't want to do it every time.
    If you can do it first and call get_timepoint_from_trip_id, that is better.

    One trip_short_name will typically correspond to different trip_ids on different days.

    This should raise an error, but does not, if the trip_short_name generates two different trips.
    The reason it doesn't is errors in Amtrak's GTFS with identical-duplicate trips varying only
    by trip_id (same calendar, same days of week, same service, etc.)
    See trip_from_tsn for more.
    """
    my_trip_id = trip_from_tsn(today_feed, trip_short_name).trip_id
    debug_print(2, "debug in get_timepoint_from_tsn:", trip_short_name, my_trip_id)

    return get_timepoint_from_trip_id(today_feed, my_trip_id, station_code)

def get_timepoint_from_trip_id (feed, trip_id, station_code):
    """
    Given a single trip_id, station_code, and a feed, extract a single timepoint.

    This returns the timepoint (as a Series) taken from the stop_times GTFS feed.

    Throw TwoStopsError if it stops here twice.

    Return "None" if it doesn't stop here.  This is not an error.
    (Used to throw NoStopError if it doesn't stop here.  Too common.)
    """
    # Old, slower code:
    # stop_times = feed.filter_by_trip_ids([trip_id]).stop_times # Unsorted
    # timepoint_df = stop_times.loc[stop_times['stop_id'] == station_code]
    # The following is MUCH faster -- cuts test case from 35 secs to 20 secs:
    timepoint_df = feed.stop_times[   ( feed.stop_times["trip_id"] == trip_id )
                                    & ( feed.stop_times["stop_id"] == station_code )
                                  ]
    if (timepoint_df.shape[0] == 0):
        return None
    if (timepoint_df.shape[0] > 1):
        # This is a bail-out error, it can afford to be slow:
        # Note: the train number lookup only works if the feed is limited to one day,
        # thus making the reverse lookup unique.
        # It will throw an error otherwise.
        trip_id_to_tsn_dict = make_trip_id_to_tsn_dict(feed)
        tsn = trip_id_to_tsn_dict[my_trip_id]
        raise TwoStopsError(' '.join(["Train number", tsn,
                                  "with trip id", trip_id,
                                  "stops at station code", station_code,
                                  "more than once"
                                 ]) )
    timepoint = timepoint_df.iloc[0] # Pull out the one remaining row
    return timepoint

def get_dwell_secs (today_feed, trip_short_name, station_code):
    """
    Gets dwell time in seconds for a specific train at a specific station

    Should be passed a feed containing only one day.
    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)

    Used primarily to determine whether to put both arrival and departure times
    in the timetable for this station.
    """
    debug_print(2, "debug:", trip_short_name, station_code)
    timepoint = get_timepoint_from_tsn(today_feed, trip_short_name, station_code)
    if (timepoint is None):
        # If the train doesn't stop there, the dwell time is zero;
        # and we need thie behavior for make_stations_max_dwell_map
        return 0

    # There's a catch!  If this station is "discharge only" or "receive only",
    # it effectively has no official dwell time, and should not get two lines
    if (timepoint.drop_off_type == 1 or timepoint.pickup_type == 1):
        return 0

    # Normal case:
    departure_secs = gk.timestr_to_seconds(timepoint.departure_time)
    arrival_secs = gk.timestr_to_seconds(timepoint.arrival_time)
    dwell_secs = departure_secs - arrival_secs
    return dwell_secs

def make_stations_max_dwell_map (today_feed, tt_spec, dwell_secs_cutoff):
    """
    Return a dict from station_code to True/False, based on the trains in the tt_spec.

    Expects a feed already filtered to a single date.

    This is used to decide whether a station should get a "double line" or "single line" format in the timetable.

    First we extract the list of stations and the list of train names from the tt_spec.

    If any train in train_nums has a dwell time of dwell_secs or longer at a station,
    then the dict returns True for that station_code; otherwise False.
    """
    # First get stations and trains list from tt_spec.
    stations_list = stations_list_from_tt_spec(tt_spec)
    trains_list = trains_list_from_tt_spec(tt_spec) # Note still contains "/" items
    flattened_trains_set = flatten_trains_list(trains_list)

    # Now create a reduced GTFS database to look through
    reduced_feed = today_feed.filter_by_trip_short_names(flattened_trains_set)

    # Prepare the dict to return
    stations_dict = {}
    for s in stations_list:
        max_dwell_secs = 0
        for t in flattened_trains_set:
            max_dwell_secs = max( max_dwell_secs, get_dwell_secs(today_feed, t, s) )
        if (max_dwell_secs >= dwell_secs_cutoff):
            stations_dict[s] = True
        else:
            stations_dict[s] = False
    return stations_dict

### Work for main multi-train timetable factory:

def fill_tt_spec(tt_spec,
                  *,
                  feed,
                  date,
                  doing_html=False,
                  box_time_characters=False,
                  doing_multiline_text=True,
                  is_major_station="standard",
                  is_ardp_station="dwell",
                  dwell_secs_cutoff=300,
                 ):
    """
    Fill a timetable from a tt-spec template using GTFS data

    The tt-spec must be complete (run augment_tt_spec first)
    feed: GTFS feed to work with.  Mandatory.
    date: Reference date to get timetable for.  Default passed at command line. FIXME

    doing_html: Produce HTML timetable.  Default is false (produce plaintext timetable).
    box_time_characters: Box every character in the time in an HTML box to make them line up.
        For use with fonts which don't have tabular nums.
        Default is False.  Avoid if possible; fragile.
    doing_multiline_text: Produce multiline text in cells.  Ignored if doing_html.
        Default is True.
        If False, stick with single-line text (and never print arrival times FIXME)
    is_major_station: pass a function which says whether a station should be "major";
        "False" means false for all
        "standard" means a standard list of Amtrak major stations
        Defaults to "standard"
    is_ardp_station: pass a function which says whether a station should have arrival times;
        "False" means false for all; "True" means true for all
        Default is "dwell" (case sensitive), which uses dwell_secs_cutoff.
    dwell_secs_cutoff: Show arrival & departure times if dwell time is this many seconds
        or higher for some train in the tt_spec
        Defaults to 300, meaning 5 minutes.
        Probably don't want to ever make it less than 1 minute.
    """

    if feed is None:
        raise InputError("No feed passed to fill_tt_spec")
    if date is None:
        raise InputError("No date passed to fill_tt_spec")

    # Filter the feed to the relevant day.
    today_feed = feed.filter_by_dates(date, date)
    debug_print(1, "Feed filtered by dates.")

    # Find the train numbers involved
    trains_list = trains_list_from_tt_spec(tt_spec) # Note still contains "/" items
    flattened_trains_set = flatten_trains_list(trains_list)
    # Reduce the feed, by eliminating stuff from other trains and wrong days.
    # By reducing the stop_times table to be much smaller,
    # this hopefully makes each subsequent search for a timepoint faster.
    # This cuts a testcase runtime from 23 seconds to 20.
    reduced_feed = today_feed.filter_by_trip_short_names(flattened_trains_set)
    today_feed = reduced_feed
    debug_print(1, "Feed filtered by trip_short_name.")

    # Debugging for the reduced feed.  Seems to be fine.
    # with open( Path("./dump-stop-times.csv"),'w') as outfile:
	#    print(today_feed.stop_times.to_csv(index=False), file=outfile)

    # Extract a list of column options, if provided in the spec
    # This must be in the second row (row 1) and first column (column 0)
    # It ends up as a list (indexed by column number) of lists of options.
    column_options = get_column_options(tt_spec)
    if (tt_spec.iloc[1,0] in ["column-options", "column_options"]):
        # Delete the problem line before further work.
        # This drops by index and not by actual row number, irritatingly
        # Thankfully they're currently the same
        tt_spec = tt_spec.drop(1, axis="index")

    # Load variable function for station name printing
    prettyprint_station_name = None
    if (doing_html):
        prettyprint_station_name = amtrak_station_name_to_html
    elif (doing_multiline_text):
        prettyprint_station_name = amtrak_station_name_to_multiline_text
    else:
        prettyprint_station_name = amtrak_station_name_to_single_line_text
    if not callable(prettyprint_station_name):
        raise TypeError ("Received prettyprint_station_name which is not callable: ",
                         prettyprint_station_name)

    # Load variable functions for is_ardp_station and is_major_station
    if (is_major_station == False):
        is_major_station = ( lambda station_code : False )
    elif (is_major_station == "standard"):
        is_major_station = amtrak.special_data.is_standard_major_station
    if not callable(is_major_station):
        raise TypeError ("Received is_major_station which is not callable: ", is_major_station)

    if (is_ardp_station == False):
        is_ardp_station = ( lambda station_code : False )
    elif (is_ardp_station == True):
        is_ardp_station = ( lambda station_code : True )
    elif (is_ardp_station == "dwell"):
        # Prep max dwell map
        stations_max_dwell_map = make_stations_max_dwell_map (today_feed, tt_spec, dwell_secs_cutoff)
        is_ardp_station = lambda station_code : stations_max_dwell_map[station_code]
        debug_print(1, "Dwell map prepared.")
    if not callable(is_ardp_station):
        raise TypeError ("Received is_ardp_station which is not callable: ", is_ardp_station)


    tt = tt_spec.copy() # "deep" copy
    styler_t = tt_spec.copy() # another "deep" copy, parallel
    debug_print(1, "Copied tt-spec.")

    # Go through the columns to get an ardp columns map -- cleaner than current implementation
    # FIXME.

    # Base CSS for every data cell.  We probably shouldn't do this but it tests that the styler works.
    base_cell_css=""

    # NOTE, border variations not implemented yet FIXME
    # borders_final_css="border-bottom-heavy"
    # borders_initial_css="border-top-heavy"
    # Have to add "initial" and "final" with heavy borders


    # NOTE that this routine is NOT FAST.  It's the bulk of the time usage in the program.
    # It is much slower than the single-timetable program.
    [row_count, column_count] = tt_spec.shape

    header_replacement_list = [] # list, will fill in as we go
    header_styling_list = [] # list, to match column numbers.  Will fill in as we go
    this_column_gets_ardp = True # First column should
    next_column_gets_ardp = False # Subsequent columns shouldn't... usually
    for x in range(1, column_count): # First (0) column is the station code
        train_nums_str = str(tt_spec.iloc[0, x]).strip() # row 0, column x

        if train_nums_str in ["station","stations"]:
            station_column_header = text_presentation.get_station_column_header(doing_html=doing_html)
            header_replacement_list.append(station_column_header)
            header_styling_list.append("") # could include background color
        elif train_nums_str in ["services"]:
            services_column_header = text_presentation.get_services_column_header(doing_html=doing_html) # in a span
            header_replacement_list.append(services_column_header)
            header_styling_list.append("") # could include background color;
        else: # it's actually a train
            # Check column options for reverse, days:
            reverse = "reverse" in column_options[x]
            use_daystring = "days" in column_options[x]

            # Separate train numbers by "/"
            train_nums = split_trains_spec(train_nums_str)
            train_num = train_nums[0]
            if len(train_nums) > 1:
                raise InputError("Two trains in one column not implemented")
            time_column_header = text_presentation.get_time_column_header(train_num, doing_html=doing_html)
            header_replacement_list.append(time_column_header)
            if (doing_html):
                time_column_stylings = get_time_column_stylings(train_num)
                header_styling_list.append(time_column_stylings)
            else: # plaintext
                header_styling_list.append("")

        for y in range(1, row_count): # First (0) row is the header
            station_code = tt_spec.iloc[y, 0] # row y, column 0
            # Reset the styler string:
            cell_css_list = [base_cell_css]

            # Consider, here, whether to build parallel tables.
            # This allows for the addition of extra rows.
            if (not pd.isna(tt.iloc[y,x])):
                # It already has a value.
                # This is probably special text like "to Chicago".
                # We keep this.  (But note: should we HTML-ize it? FIXME )

                # But we have to set the styler.
                cell_css_list.append("special-cell") # can use row and col numbers to find it
            elif (pd.isna(station_code)):
                # Line which has no station code -- freeform line.
                # No times or station names here!
                # Prefilled text was done above; blanks should be made truly blank, "".
                tt.iloc[y,x] = ""
                cell_css_list.append("special-cell")
            else:
                # Blank to be filled in -- the usual case.
                if train_nums_str in ["station","stations"]: # Column for station names
                    cell_css_list.append("station-cell")
                    station_name_raw = amtrak.json_stations.lookup_station_name[station_code]
                    major = amtrak.special_data.is_standard_major_station(station_code)
                    station_name_str = prettyprint_station_name(station_name_raw, major)
                    tt.iloc[y,x] = station_name_str
                    # FIXME: need to show time zone...
                    next_column_gets_ardp = True # Put ardp in the column after the station names
                elif train_nums_str in ["services"]: # Column for station services codes
                    cell_css_list.append("services-cell")
                    next_column_gets_ardp = True # Put ardp in the column after the station services
                    # Here is where we should call out to the Amtrak stations database and look up
                    # the actual services.  FIXME.
                    tt.iloc[y,x] = ""
                else: # It's a train number.
                    # For a slashed train spec ( 549 / 768 ) pull the *first* train's times,
                    # then the second train's times *if the first train doesn't stop there*
                    # If the first train terminates and the second train starts, we need to
                    # somehow make it an ArDp station with double lines... tricky, not done yet
                    #
                    debug_print(3, ''.join(["Trains: ", str(train_nums), "; Stations:", station_code]) )
                    timepoint = get_timepoint_from_tsn(today_feed,train_num,station_code)

                    calendar = None # if not use_daystring
                    if (use_daystring):
                        calendar = get_calendar_from_tsn(today_feed, train_num)

                    # Need to insert complicated for loop here for multiple trains
                    # TODO FIXME

                    # MUST figure first_stop and last_stop
                    # ...which means we need to make earlier passes through the table FIXME

                    # Only assign the stylings if the train hasn't ended.  Tricky!  Dunno how to do it!
                    # Probably requires that earlier pass through the table.
                    if (timepoint is None):
                        # This train does not stop at this station
                        # Blank cell -- need to be cleverer about this FIXME
                        tt.iloc[y,x] = ""
                        cell_css_list.append("blank-cell")
                        # Confusing: we want to style some of these and not others.  Woof.
                        cell_css_list.append( get_time_column_stylings(train_num, "class") )
                    else:
                        cell_css_list.append("time-cell")
                        cell_css_list.append( get_time_column_stylings(train_num, "class") )

                        cell_text = text_presentation.timepoint_str(
                                    timepoint,
                                    doing_html=doing_html,
                                    box_time_characters=box_time_characters,
                                    reverse=reverse,
                                    two_row = is_ardp_station(station_code),
                                    use_ar_dp_str=this_column_gets_ardp,
                                    use_daystring=use_daystring,
                                    calendar=calendar,
                                    )
                        tt.iloc[y,x] = cell_text
            # Fill the styler.  We MUST overwrite every single cell of the styler.
            styler_t.iloc[y,x] = ' '.join(cell_css_list)
        # Set up for the next column:
        this_column_gets_ardp=next_column_gets_ardp
        next_column_gets_ardp=False

    # Now we have to delete the placeholder left column
    tt = tt.drop(labels=0, axis="columns")
    styler_t = styler_t.drop(labels=0, axis="columns")

    # And the placeholder top row
    tt = tt.drop(labels=0, axis="rows")
    styler_t = styler_t.drop(labels=0, axis="rows")

    # And now we have to rename the headers.  This is kind of ugly!
    # This is quite fragile and should be checked regularly.
    # It depends on having removed the placeholder column already.
    #
    # We have to do the styler and the tt at the same time,
    # or the styler will fail.
    tt.columns = header_replacement_list
    styler_t.columns = header_replacement_list

    return (tt, styler_t, header_styling_list)

##########################
#### NEW MAIN PROGRAM ####
##########################
if __name__ == "__main__":
    debug_print (3, "Dumping sys.path for clarity:", sys.path )

    my_arg_parser = make_tt_arg_parser()
    args = my_arg_parser.parse_args()

    set_debug_level(args.debug)
    output_dirname = args.output_dirname

    if (args.gtfs_filename):
        gtfs_filename = args.gtfs_filename
    else:
        # Default to Amtrak
        gtfs_filename = amtrak.gtfs_unzipped_local_path

    if (args.reference_date):
        reference_date = int( args.reference_date.strip() )
    else:
        # Use tomorrow as the reference date.
        # After all, you aren't catching a train today, right?
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        reference_date = int( tomorrow.strftime('%Y%m%d') )
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")

    master_feed = initialize_feed(gtfs=gtfs_filename)

    # Create the station name lookup table.
    # This is a global in amtrak.json_stations called
    # amtrak.json_stations.lookup_station_name
    # Expects JSON stations to be downloaded already (go easy on Amtrak bandwidth!)
    amtrak.json_stations.make_station_name_lookup_table()

    # Generate routes.html
    routes_html_path = Path(output_dirname) / "routes.html"
    with open(routes_html_path,'w') as outfile:
        print(master_feed.routes.to_html(), file=outfile)

    if not (args.type):
        print ("No type of timetable specified.")
        quit()

    if (args.type == "fill"):

        # Accept with or without .spec
        tt_filename_base = args.tt_spec_filename.removesuffix(".tt-spec")
        tt_spec_filename = tt_filename_base + ".tt-spec"
        # Output to "tt_" + filename  + ".whatever"
        output_pathname_before_suffix = "tt_" + tt_filename_base

        tt_spec = load_tt_spec(tt_spec_filename)
        tt_spec = augment_tt_spec(tt_spec, feed=master_feed, date=reference_date)
        debug_print(1, "tt-spec loaded and augmented")

        # Quick hack to speed up testing cycle:
        # implement this properly later TODO
        do_csv = False
        do_html = False
        do_pdf = True
        # Note that due to the inline images issue we may need to run
        # a completely separate HTML version for weasyprint.  We avoid this so far.
        # TODO
        # Consider using the SpartanTT font to handle this.  We can make the font
        # quasi-legit for screen readers by using correct Unicode code points.

        if (do_csv):
            (timetable, styler_table, header_styling) = fill_tt_spec(tt_spec,
                        feed = master_feed,
                        date = reference_date,
                        is_major_station=amtrak.special_data.is_standard_major_station,
                        is_ardp_station="dwell")
            # NOTE, need to add the header
            timetable.to_csv(output_pathname_before_suffix + ".csv", index=False, header=True)
            debug_print(1, "CSV done")

        if (do_html or do_pdf):
            # Main timetable, same for HTML and PDF
            (timetable, styler_table, header_styling_list) = fill_tt_spec(tt_spec,
                        feed = master_feed,
                        date = reference_date,
                        is_major_station=amtrak.special_data.is_standard_major_station,
                        is_ardp_station="dwell",
                        doing_html=True,
                        box_time_characters=False,)
            timetable_styled_html = style_timetable_for_html(timetable, styler_table)
            debug_print(1, "HTML styled")
            # We need a title for HTML and PDF pages
            page_title = "Timetable for " + tt_filename_base.capitalize() # FIXME

        if (do_html or do_pdf):
            # Produce the final complete page...
            timetable_finished_html = finish_html_timetable(
                timetable_styled_html,
                header_styling_list,
                title=page_title,
                box_time_characters=False,
                )
            with open(output_pathname_before_suffix + '.html' , 'w' ) as outfile:
                print(timetable_finished_html, file=outfile)
            debug_print(1, "Finished HTML done")

        if (do_pdf):
            # Pick up already-created HTML, convert to PDF
            weasy_html_pathname = output_pathname_before_suffix + '.html'
            html_for_weasy = weasyHTML(filename=weasy_html_pathname)
            html_for_weasy.write_pdf(output_pathname_before_suffix + ".pdf")
            debug_print(1, "Weasy done")

        quit()

    if (args.type == "test"):
        result = service_dates_from_trip_id(master_feed, 5002831767)
        print (result)
        quit()

        new_feed = master_feed.filter_remove_one_day_calendars()
        printable_calendar = gtfs_type_cleanup.type_uncorrected_calendar(new_feed.calendar)
        module_dir = Path(__file__).parent
        printable_calendar.to_csv( module_dir / "amtrak/gtfs/calendar_stripped.txt", index=False)
        print ("calendar without one-day calendars created")
        quit()

        print(master_feed.get_trip_short_name(55792814913))
        quit()

        tt_spec = load_tt_spec(args.tt_spec_filename)
        tt_spec = augment_tt_spec(tt_spec, feed=master_feed, date=reference_date)
        dwell_secs = get_dwell_secs("59","CDL")
        print("Dwell is", dwell_secs)
        quit()
