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
from collections import namedtuple
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
    InputError
)
from timetable_kit.timetable_argparse import make_tt_arg_parser

# This one monkey-patches gk.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

from timetable_kit import gtfs_type_cleanup

from timetable_kit import amtrak # so we don't have to say "timetable_kit.amtrak"
# To make it easier to isolate Amtrak dependencies in the main code, we always explicitly call:
# amtrak.special_data
# amtrak.agency_cleanup
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

# GLOBAL VARIABLES
# Will be changed by command-line arguments, hopefully!
# Debugging on?
debug = True
# The Amtrak GTFS feed files -- FIXME, this is hackish
gtfs_filename = str( amtrak.gtfs_unzipped_local_path )
# The output directory
output_dirname="."
# The date we are preparing timetables for (redefine after reading command line)
reference_date = None

# GLOBAL VARIABLES
# The master variable for the feed; overwritten in initialize_feed
master_feed=None
# The enhanced agency list; likewise
enhanced_agency=None
# Lookup table from route name to route id, likewise
lookup_route_id=None
# Trip lookup table, currently unused
trip_lookup_table=None
# Lookup table from station code to desired printed station name, overwritten later
lookup_station_name=None



# Useful debugging function for Pandas tables
def dumptable(table, filename):
    """Print an table as HTML to a file, for debugging.  Directory and suffix are added."""
    with open(''.join([output_dirname,'/',filename,'.html']),'w') as outfile:
	    print(table.to_html(), file=outfile)

#### INITIALIZATION CODE
def initialize_feed():
    global master_feed
    global enhanced_agency
    global lookup_route_id

    print ("Using GTFS file " + gtfs_filename)
    path = Path(gtfs_filename)
    # Amtrak has no shapes file, so no distance units.  Check this if a shapes files appears.
    # Also affects display miles so default to mi.
    master_feed = gk.read_feed(path, dist_units='mi')

    master_feed.validate()

    # Fix types on every table in the feed
    gtfs_type_cleanup.fix(master_feed)

    # Clean up Amtrak agency list.  Includes fixing types.
    # This is non-reversible, so give it its own variable.
    enhanced_agency = amtrak.agency_cleanup.revised_amtrak_agencies(master_feed.agency)
    # Go ahead and change the master feed copy.
    master_feed.agency = enhanced_agency

    # Create lookup table from route name to route id. Amtrak only has long names, not short names.
    lookup_route_id = dict(zip(master_feed.routes.route_long_name, master_feed.routes.route_id))

    # Create a lookup table by trip id... all trips... belongs elsewhere
    indexed_trips = master_feed.trips.set_index('trip_id')
    global trip_lookup_table
    trip_lookup_table = indexed_trips.to_dict('index')
    # print(trip_lookup_table) # this worked

    # This is Amtrak-specific
    fix_known_errors(master_feed)
    return

def fix_known_errors(feed):
    """
    Change the feed in place to fix known errors.
    """
    # Cardinal 1051 (DST switch date) with wrong direction ID

    # There's an error in the trips. Attempt to fix it.
    # THIS WORKS for fixing errors in a feed.  REMEMBER IT.
    # Revised for PANDAS 1.4.
    my_trips = feed.trips

    # print ( my_trips[my_trips["trip_short_name"] == "1051"] )
    my_trips.loc[my_trips["trip_short_name"] == "1051","direction_id"] = 0
    # print ( my_trips[my_trips["trip_short_name"] == "1051"] )

    # Error fixed.  Put back into the feed.
    feed.trips = my_trips
    return

### END OF INITIALIZATION CODE

# Convenience functions for the currently-global route_id and station_name lookup tables
def route_id(route_name):
    """Given a route long name, return the ID."""
    return lookup_route_id[route_name]

def station_name(code):
    """Given a station code, return the printable name."""
    return lookup_station_name[code]

### tt-spec loading and parsing code

def load_tt_spec(filename):
    """Load a tt-spec from a CSV file"""
    tt_spec = pd.read_csv(filename, index_col=False, header=None, dtype = str)
    return tt_spec

def augment_tt_spec(raw_tt_spec):
    """
    Fill in the station list for a tt-spec if it has a key code.

    Cell 0,0 is normally blank.
    If it is "Stations of 59", then (a) assume there is only one tt-spec row;
    (b) get the stations for 59 and fill the rows in from that

    Uses the globals master_feed and reference_date.
    """
    if (pd.isna(raw_tt_spec.iloc[0,0]) ):
        # No key code, nothing to do
        return tt_spec
    key_code = str(raw_tt_spec.iloc[0,0])
    # print("Key code: " + key_code)
    if key_code.startswith("stations of "):
        key_train_name = key_code[len("stations of "):]
        # Filter the feed down to a single date...
        today_feed = master_feed.filter_by_dates(reference_date, reference_date)
        # And pull the stations list
        stations_df = stations_list_from_trip_short_name(today_feed, key_train_name)
        new_tt_spec = raw_tt_spec.iloc[0:,] # Get first row
        new_tt_spec.iloc[0,0] = float("nan") # Blank out key_code
        newer_tt_spec = pd.concat([new_tt_spec,stations_df]) # Yes, this works
        return newer_tt_spec

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

def is_column_reversed(trains_spec):
    """
    Given a string like "-59 / 174 / 22", return True if the timetable column should read bottom to top, False otherwise.

    All this actually does is check for a leading minus sign.  If it's present, this is a bottom-to-top timetable column.
    This applies to the ENTIRE column, so the minus sign must be on the FIRST train number (only).
    """
    clean_trains_spec = trains_spec.lstrip()
    reverse=False
    if (clean_trains_spec[0]=="-"):
        reverse=True
    return reverse

def split_trains_spec(trains_spec):
    """
    Given a string like "-59 / 174 / 22", return a structured list:

    [["59, "174", "22"], True]

    Used to separate specs for multiple trains in the same timetable column.
    A single "59" will simply give {"59"}.

    A leading minus sign (-) means the column is reversed (read bottom to top);
    this is stripped by this method.
    """
    # Remove leading whitespace and possible leading minus sign
    clean_trains_spec = trains_spec.lstrip()
    cleaner_trains_spec = clean_trains_spec.lstrip("-")

    raw_list = cleaner_trains_spec.split("/")
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

### "Compare" Debugging routines to check for changes in timetable

def compare_stop_lists(base_trip, trips):
    """
    Find the diff between one trip and a bunch of other (presumably similar) trips.

    Debugging routine used to identify upcoming changes in train schedules.
    Given a stop_list DataFrame and a list of stop_list DataFrames,
    all with the same shape, (we may expand this later FIXME)
    print the diff of each later one with the first.

    Prefers to start with stop_times tables with unique, but matching, indexes.
    Using stop_sequence as the index can usually provide this.
    """
    if (len(trips) == 0):
        print ("No trips, stopping.")
        return
    if (len(trips) == 1):
        print ("Only 1 trip, stopping.")
        return
    # Drop the trip_id because it will always compare differently
    base_stop_times = master_feed.get_single_trip_stop_times(base_trip["trip_id"])
    base_stop_times = base_stop_times.drop(["trip_id"], axis="columns")
    for trip in (trips.itertuples()):
        stop_times = master_feed.get_single_trip_stop_times(trip.trip_id)
        stop_times = stop_times.drop(["trip_id"],axis="columns")
        # Use powerful features of DataTable
        comparison = base_stop_times.compare(stop_times, align_axis="columns", keep_shape=True)
        if (not comparison.any(axis=None)):
            print( " ".join(["Identical:", str(base_trip.trip_id), "and", str(trip.trip_id)]) + "." )
        else:
            reduced_comparison = comparison.dropna(axis="index",how="all")
            print( " ".join(["Comparing:",str(base_trip.trip_id),"vs.",str(trip.trip_id)]) + ":" )
            #print( reduced_comparison )
            # Works up to here!

            # Please note the smart way to add an extra MultiIndex layer is with "concat".
            # Completely nonobvious.  "concat" with "keys" option.

            # We want to recover the stop_id for more comprehensibility.
            # Stupid program wants matching-depth MultiIndex.  There is no easy way to make it.
            # So make it the stupid way!  Build it exactly parallel to the real comparison.
            fake_comparison = base_stop_times.compare(base_stop_times,
                                                      align_axis="columns",
                                                      keep_shape=True,
                                                      keep_equal=True)
            reduced_fake_comparison = fake_comparison.filter(
                                            items=reduced_comparison.index.array,
                                            axis="index"
                                            )
            enhanced_comparison = reduced_comparison.combine_first(reduced_fake_comparison)
            # And we're ready to print.
            print( enhanced_comparison )
    return

def compare_similar_services(route_id):
    """
    Find timing differences on a route between similar services.

    Used to see how many services with different dates are actually the same service
    """
    route_feed = master_feed.filter_by_route_ids([route_id])
    feed = route_feed.filter_bad_service_ids(amtrak.special_data.global_bad_service_ids)

    print("Calendar:")
    print(feed.calendar)

    print("Downbound:")
    downbound_trips = feed.trips[feed.trips.direction_id == 0] # W for LSL
    print(downbound_trips)
    base_trip = downbound_trips.iloc[0, :] # row 0, all columns
    compare_stop_lists(base_trip,downbound_trips)

    print("Upbound:")
    upbound_trips = feed.trips[feed.trips.direction_id == 1] # E for LSL
    print(upbound_trips)
    base_trip = upbound_trips.iloc[0, :] # row 0, all columns
    compare_stop_lists(base_trip,upbound_trips)
    return

### Timetable prototype generation (nonfunctional)

def make_spec():
    """Not ready to use: put to one side for testing purposes"""
    # Creates a prototype timetable.  It will definitely need to be manipulated by hand.
    # Totally incomplete. FIXME
    route_ids = [route_id("Illini"),route_id("Saluki"),route_id("City Of New Orleans")]

    route_feed = master_feed.filter_by_route_ids(route_ids)
    today_feed = route_feed.filter_by_dates(reference_date, reference_date)
    # reference_date is currently a global

    print("Allbound:")
    print(today_feed.trips)

    print("Upbound:")
    up_trips = today_feed.trips[today_feed.trips.direction_id == 0]
    print(up_trips)

    print("Downbound:")
    down_trips = today_feed.trips[today_feed.trips.direction_id == 1]
    print(down_trips)

### First, simplistic, timetable production attempt

def format_single_trip_timetable(stop_times,
                                 calendar=False,
                                 infrequent=False,
                                 doing_html=False,
                                 box_characters=False,
                                 min_dwell=0,
                                 reverse=False,
                                 train_number="" ):
    """
    Make a workable timetable for a single trip of the Cardinal or Sunset Limited.

    Assumes that stop_times has been indexed by stop_sequence, and sorted.

    doing_html: output text with HTML annotations rather than plaintext (newline vs. <br>, use of <b>, etc.)
    box_characters: for use with fonts which don't have tabular nums.  Avoid if possible.

    min_dwell: if dwell time is less than this number of minutes,
    only departure times are shown, and arrival times are unpublished.
    This is useful for shortening public timetables.

    reverse: reverses Ar/Dp -- an ugly hack for upside-down timetables.  The timetable must
    still be turned upside down manually afterwards.

    infrequent: if False (the default) the calendar is ignored.  (FOR NOW.  FIXME)
    calendar: a calendar with a single row containing the correct calendar for the service.  Optional.
    train_number: used as header for the times column
    """

    # CSS class "shortcuts"
    # in future, color will likely be changed
    bg_cornsilk_css     = "color-cornsilk"

    # Define the columns, in order, and create empty DataFrames for timetable & styler
    # By defining the columns first we avoid order dependency later
    timetable_columns = pd.Index(["Time","StationCode"])
    timetable_base = pd.DataFrame(columns=timetable_columns)
    styler_base = pd.DataFrame(columns=timetable_columns)

    # The styler table must be the exact same shape as the output table
    # -- styles will apply to each cell specifically
    # Header styling has to be done separately, with a big yuck...

    list_of_timetable_rows = [] # accumulate, then append to blank base
    list_of_styler_rows = [] # accumulate, then append to blank base

    # This gets the first and last stop index number.  Helps with pretty-printing...
    stop_sequence_numbers = stop_times.index
    first_stop_number = stop_sequence_numbers.min()
    last_stop_number = stop_sequence_numbers.max()

    for timepoint in stop_times.itertuples():
        # print(timepoint)

        # Decide whether to suppress dwell
        departure_secs = gk.timestr_to_seconds(timepoint.departure_time)
        arrival_secs = gk.timestr_to_seconds(timepoint.arrival_time)
        dwell_secs = departure_secs - arrival_secs
        suppress_dwell = False
        if (dwell_secs < min_dwell * 60):
            suppress_dwell = True

        # Special treatment of first and last stops
        is_first_stop = False;
        is_last_stop = False;
        if (timepoint.Index == first_stop_number):
            is_first_stop = True;
        if (timepoint.Index == last_stop_number):
            is_last_stop = True;

        # Receive-only / Discharge-only
        receive_only = False;
        discharge_only = False;
        if (is_first_stop):
            receive_only = True; # Logically speaking... but don't annotate it
        if (is_last_stop):
            discharge_only = True; # Logically speaking... but don't annotate it
        if (timepoint.drop_off_type == 1 and timepoint.pickup_type == 0):
            receive_only = True;
        elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 0):
            discharge_only = True;

        # One row or two?
        if (receive_only or discharge_only or suppress_dwell):
            styler_one_row = True
        else: #reverse
            styler_one_row = False

        # Big bad subroutine call
        arrival_departure_str = text_presentation.timepoint_str( timepoint,
                two_row=(not styler_one_row),
                use_ar_dp_str=True,
                doing_html = doing_html,
                box_characters = box_characters,
                use_daystring = infrequent,
                calendar = calendar,
                is_first_stop = is_first_stop,
                is_last_stop = is_last_stop,
            )

        # Prettyprint the station name
        station_name_raw = lookup_station_name[timepoint.stop_id]
        if ( amtrak.special_data.is_standard_major_station(timepoint.stop_id) ):
            major = True
        else:
            major = False

        if (doing_html):
            station_name_str = amtrak_station_name_to_html(station_name_raw, major)
        else:
            if (major):
                station_name_str = station_name_raw.upper()
            else:
                station_name_str = station_name_raw

        # This is *not* order-dependent; the order is set by the first row, up above.
        tt_row_dict = {}
        tt_row_dict["Time"]        = [arrival_departure_str]
        tt_row_dict["StationCode"] = [station_name_str]
        tt_row = pd.DataFrame(tt_row_dict, index=[timepoint.Index])
        list_of_timetable_rows.append(tt_row)

        # This is *not* order-dependent; the order is set by the first row, up above.
        sr_dict = {}
        sr_dict["Time"]     = [" ".join(["time_column", bg_cornsilk_css])]
        sr_dict["StationCode"]  = [" ".join(["stations_column", ])]
        styler_row = pd.DataFrame(sr_dict, index=[timepoint.Index])
        list_of_styler_rows.append(styler_row)

    timetable = timetable_base.append(list_of_timetable_rows)
    styler = styler_base.append(list_of_styler_rows)

    # OK.  Whew.  Now we rename the column headers....
    # Use the train number as the column header for times
    time_column_prefix = "Train #"
    time_column_header = "".join([time_column_prefix, str(train_number)])
    if (doing_html):
        time_column_header = ''.join([time_column_prefix,"<br>","<strong>",str(train_number),"</strong>"])

    # This is the output table header, which will rename the columns at the end
    tt_new_dict = {}
    tt_new_dict["Time"] = time_column_header
    tt_new_dict["StationCode"] = "Station"

    # This lets us rename the columns so the parallel styler table works.
    # It does *not* let us style the headers, sadly.
    styler_new_dict = {}
    styler_new_dict["Time"]        = tt_new_dict["Time"]
    styler_new_dict["StationCode"] = tt_new_dict["StationCode"]

    # OK.  Now really rename the column headers...
    new_timetable = timetable.rename(columns=tt_new_dict)
    new_styler = styler.rename(columns=styler_new_dict)

    # Revisit the heading styling:
    # Build a list to keep track of the header styles
    header_styling_list = [ " background-color: cornsilk; ",
                            " ",
                          ]

    print(new_timetable)
    return (new_timetable, new_styler, header_styling_list)

def print_single_trip_tt(trip):
    """
    Print a single trip timetable (including Cardinal and Sunset but not Texas Eagle)

    Probably not that useful, but proof of concept
    """

    stop_times = master_feed.get_single_trip_stop_times(trip.trip_id)
    train_number = trip.trip_short_name

    # Extract the service days of the week
    # Filter to the calendar for the specific service
    today_feed = master_feed.filter_by_dates(reference_date, reference_date)
    this_feed = today_feed.filter_by_service_ids([trip.service_id])

    # Should give exactly one calendar -- we don't test that here, though
    daystring = text_presentation.day_string(this_feed.calendar)
    if (daystring == "Daily"):
        infrequent = False
    else:
        infrequent = True
        # This is not really correct; but it's good enough for once-a-day overnights.
        # Trains which don't run overnight should never be marked "infrequent", because
        # the days can be at the top of the column instead of next to the time.

    # Output filename without the .html, .pdf, and .csv suffix:
    output_pathname_before_suffix = ''.join([output_dirname, "/tt_",str(train_number)])

    # Main run to generate HTML:
    [timetable, styler_table, header_styling_list] = format_single_trip_timetable( stop_times,
                                    calendar=this_feed.calendar,
                                    infrequent=infrequent,
                                    min_dwell=5,
                                    train_number=train_number,
                                    doing_html=True,
                                    box_characters=False,
                                    )

    # Run the styler on the timetable...
    timetable_styled_html = style_timetable_for_html(timetable, styler_table)

    # Produce the final complete page...
    page_title = "Timetable for Amtrak Train #" + str(train_number)
    timetable_finished_html = finish_html_timetable(timetable_styled_html, header_styling_list, title=page_title, box_characters=False)
    with open( output_pathname_before_suffix + '.html' , 'w' ) as outfile:
        print(timetable_finished_html, file=outfile)

    # Now rebuild the final complete page for Weasyprint...
    # (We will probably need to rerun the entire routine due to the annoying inline-image issue)
    timetable_finished_weasy=finish_html_timetable(timetable_styled_html, header_styling_list, title=page_title,
                                             for_weasyprint=True, box_characters=False)
    # Need an intermediate file in order to resolve the image references correctly
    # And Weasy can't handle inline SVG images, so we need external image references.
    weasy_html_pathname = output_pathname_before_suffix + '_weasy.html'
    with open( weasy_html_pathname , 'w' ) as outfile:
	    print(timetable_finished_html, file=outfile)
    # weasy_base_dir = os.path.realpath(os.path.dirname(__file__))
    # my_base_url = "file://" + weasy_base_dir + "/"
    # print (my_base_url)
    # html_for_weasy = weasyHTML(filename=weasy_html_pathname, base_url=my_base_url)
    html_for_weasy = weasyHTML(filename=weasy_html_pathname)
    html_for_weasy.write_pdf(output_pathname_before_suffix + ".pdf")

    # Finally rerun the main routine as plaintext for CSV...
    [timetable_txt, dummy_table, dummy_styling] = format_single_trip_timetable( stop_times,
                                    calendar=this_feed.calendar,
                                    infrequent=infrequent,
                                    doing_html=False,
                                    min_dwell=5,
                                    train_number=train_number,
                                    )
    timetable_txt.to_csv(output_pathname_before_suffix + ".csv", index=False)
    return

#### Subroutines for fill_tt_spec

def trip_from_trip_short_name(today_feed, trip_short_name):
    """
    Given a single train number (trip_short_name), and a feed containing only one day, produces the trip record.

    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)
    """
    # Note that reference_date and master_feed are globals.
    single_trip_feed = today_feed.filter_by_trip_short_names([trip_short_name])
    this_trip_today = single_trip_feed.get_single_trip() # Raises errors if not exactly one trip

    return this_trip_today

def stations_list_from_trip_short_name(today_feed, trip_short_name):
    """
    Given a single train number (trip_short_name), and a feed containing only one day, produces a dataframe with a stations list.

    Produces a station list dataframe.
    This is used in augment_tt_spec, and via the "stations" command.

    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)
    """

    trip_id = trip_from_trip_short_name(today_feed, trip_short_name).trip_id

    sorted_stop_times = today_feed.get_single_trip_stop_times(trip_id)
    sorted_station_list = sorted_stop_times['stop_id']
    # print (sorted_station_list)
    return sorted_station_list

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

def get_timepoint (today_feed, trip_short_name, station_code):
    """
    Given a single train number (trip_short_name),  station_code, and a feed containing only one day, extract a single timepoint.

    This returns the timepoint (as a Series) taken from the stop_times GTFS feed.

    Throw TwoStopsError if it stops here twice.

    Return "None" if it doesn't stop here.  This is not an error.
    (Used to throw NoStopError if it doesn't stop here.  Too common.)

    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)
    """
    trip_id = trip_from_trip_short_name(today_feed, trip_short_name).trip_id
    stop_times = today_feed.filter_by_trip_ids([trip_id]).stop_times # Unsorted
    timepoint_df = stop_times.loc[stop_times['stop_id'] == station_code]
    if (timepoint_df.shape[0] == 0):
        return None
        # raise NoStopError(' '.join(["Train number", trip_short_name,
        #                          "does not stop at station code",
        #                          station_code,
        #                         ]) )
    if (timepoint_df.shape[0] > 1):
        raise TwoStopsError(' '.join(["Train number", trip_short_name,
                                  "stops at station code",
                                  station_code,
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
    timepoint = get_timepoint(today_feed, trip_short_name, station_code)
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
    # Note that reference_date and master_feed are globals.
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
                  doing_html=False,
                  box_characters=False,
                  doing_multiline_text=True,
                  is_major_station="standard",
                  is_ardp_station="dwell", dwell_secs_cutoff=300,
                 ):
    """
    Fill a timetable from a tt-spec template using GTFS data

    The tt-spec must be complete (run augment_tt_spec first)
    doing_html: Produce HTML timetable.  Default is false (produce plaintext timetable).
    box_characters: Box every character in the time in an HTML box to make them line up.
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

    # Filter the feed to the relevant day.  master_feed and reference_date are globals.
    today_feed = master_feed.filter_by_dates(reference_date, reference_date)

    # To save time, here we must filter out all unwanted trains TODO

    tt = tt_spec.copy() # "deep" copy
    styler_t = tt_spec.copy() # another "deep" copy, parallel

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
    if not callable(is_ardp_station):
        raise TypeError ("Received is_ardp_station which is not callable: ", is_ardp_station)

    # Go through the trains to spot reversed trains

    # Go through the columns to get an ardp columns map -- cleaner than current implementation
    # FIXME.

    # Base CSS for every data cell.  We probably shouldn't do this but it tests that the styler works.
    base_cell_css=""

    # NOTE, border variations not implemented yet FIXME
    # borders_final_css="border-bottom-heavy"
    # borders_initial_css="border-top-heavy"
    # Have to add "initial" and "final" with heavy borders

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
            # A leading "-" in the trainspec means reversed column
            reverse = is_column_reversed(train_nums_str)
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
            else:
                # Blank to be filled in -- the usual case.
                if train_nums_str in ["station","stations"]: # Column for station names
                    cell_css_list.append("station-cell")
                    station_name_raw = lookup_station_name[station_code]
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
                    # print( ''.join(["Trains: ", str(train_nums), "; Stations:", station_code]) )
                    timepoint = get_timepoint(today_feed,train_num,station_code)
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

                        # If this is an infrequent train, MAYBE put use_daystring & calendar FIXME
                
                        cell_text = text_presentation.timepoint_str(
                                    timepoint,
                                    doing_html=doing_html,
                                    box_characters=box_characters,
                                    reverse=reverse,
                                    two_row = is_ardp_station(station_code),
                                    use_ar_dp_str=this_column_gets_ardp,
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
    # print ( "Dumping sys.path for clarity:")
    # print ( sys.path )
    # print ("Made it to the main program")

    my_arg_parser = make_tt_arg_parser()
    args = my_arg_parser.parse_args()
    # These have defaults; override from command line.
    # NOTE!  We are not in a function so don't need global keyword
    debug = args.debug
    if (args.gtfs_filename):
        gtfs_filename = args.gtfs_filename
    if (args.output_dirname):
        output_dirname = args.output_dirname

    if (args.reference_date):
        reference_date = int( args.reference_date.strip() )
    else:
        # Use tomorrow as the reference date.
        # After all, you aren't catching a train today, right?
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        reference_date = int( tomorrow.strftime('%Y%m%d') )
    print("Working with reference date ", reference_date, ".", sep="")

    initialize_feed() # This sets various globals

    # Create the station name lookup table, a global
    # Expects JSON stations to be downloaded already (go easy on Amtrak bandwidth!)
    lookup_station_name = amtrak.json_stations.make_station_name_lookup_table()
    # NOTE: redundant copy is present in text_presentation.py FIXME

    dumptable(master_feed.routes, "routes") # Generates routes.html

    if not (args.type):
        print ("No type of timetable specified.")
        quit()

    if (args.type == "stations"):
        # This one is working.
        tsn = args.trip_short_name
        if (not tsn):
            raise ValueError("Can't generate a station list without a specific trip.")
        tsn = tsn.strip() # Avoid whitespace problems

        # Filter the feed down to one date
        today_feed = master_feed.filter_by_dates(reference_date, reference_date)

        # And pull the station list -- NOTE, these are not in the right order!
        station_list_df = stations_list_from_trip_short_name(today_feed, tsn)
        output_filename = "".join([output_dirname, "/", "tt_", tsn, "_","stations.csv"])
        station_list_df.to_csv(output_filename,index=False)
        # Note: this will put "stop_id" in top row, which is OK
        quit()

    if (args.type == "single"):
        # Single timetable.
        # This is the old, one-train printer.
        # It works, but is not good.

        trip_short_name = args.trip_short_name
        today_feed = master_feed.filter_by_dates(reference_date, reference_date)
        trip = trip_from_trip_short_name(today_feed, trip_short_name)
        print_single_trip_tt(trip)
        quit()

    if (args.type == "make-spec"):
        # Make a tt_spec (work in progress)
        print ("unfinished")
        make_spec()
        quit()

    if (args.type == "compare"):
        route_long_name = args.route_long_name
        compare_similar_services(route_id(route_long_name))
        quit()

    if (args.type == "fill"):

        # Accept with or without .spec
        tt_filename_base = args.tt_spec_filename.removesuffix(".tt-spec")
        tt_spec_filename = tt_filename_base + ".tt-spec"

        tt_spec = load_tt_spec(tt_spec_filename)
        tt_spec = augment_tt_spec(tt_spec)
        print ("tt-spec loaded and augmented")

        # CSV version first:
        (timetable, styler_table, header_styling) = fill_tt_spec(tt_spec,
                      is_major_station=amtrak.special_data.is_standard_major_station,
                      is_ardp_station="dwell")
        # NOTE, need to add the header
        timetable.to_csv(tt_filename_base + ".csv", index=False, header=True)
        print ("CSV done")

        # HTML version next:
        (timetable, styler_table, header_styling_list) = fill_tt_spec(tt_spec,
                      is_major_station=amtrak.special_data.is_standard_major_station,
                      is_ardp_station="dwell",
                      doing_html=True,
                      box_characters=False,)

        # Temporary output, until styler work is done
        #tt_html = timetable.to_html()
        #with open(tt_filename_base + "-unstyled.html",'w') as outfile:
	    #    print(tt_html, file=outfile)

        # Style the timetable.
        timetable_styled_html = style_timetable_for_html(timetable, styler_table)

        print ("HTML styled")

        # Produce the final complete page...
        output_pathname_before_suffix = tt_filename_base
        page_title = "Timetable for " + tt_filename_base.capitalize() # FIXME
        timetable_finished_html = finish_html_timetable(timetable_styled_html, header_styling_list, title=page_title, box_characters=False,)
        with open( "tt_" + output_pathname_before_suffix + '.html' , 'w' ) as outfile:
            print(timetable_finished_html, file=outfile)

        print ("Finished HTML done")

        # Now rebuild the final complete page for Weasyprint...
        # (We will probably need to rerun the entire routine due to the annoying inline-image issue)
        timetable_finished_weasy=finish_html_timetable(timetable_styled_html, header_styling_list, title=page_title,
                                             for_weasyprint=True, box_characters=False,)
        # Need an intermediate file in order to resolve the image references correctly
        # And Weasy can't handle inline SVG images, so we need external image references.
        weasy_html_pathname = "tt_" + output_pathname_before_suffix + '_weasy.html'
        with open( weasy_html_pathname , 'w' ) as outfile:
            print(timetable_finished_html, file=outfile)
        # weasy_base_dir = os.path.realpath(os.path.dirname(__file__))
        # my_base_url = "file://" + weasy_base_dir + "/"
        # print (my_base_url)
        # html_for_weasy = weasyHTML(filename=weasy_html_pathname, base_url=my_base_url)
        html_for_weasy = weasyHTML(filename=weasy_html_pathname)
        html_for_weasy.write_pdf("tt_" + output_pathname_before_suffix + ".pdf")

        print ("Weasy done")
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
        tt_spec = augment_tt_spec(tt_spec)
        dwell_secs = get_dwell_secs("59","CDL")
        print("Dwell is", dwell_secs)
        quit()

        print(stations_list_from_tt_spec(new_tt_spec))
        name = lookup_station_name["BUF"]
        fancy_name = text_presentation.fancy_amtrak_station_name(name, major=True)
        print(fancy_name);
        quit()


