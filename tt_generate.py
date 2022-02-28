#! /usr/bin/env python3
# tt_generate.py
# Part of timetable_kit
#
# This is the main program
#
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

# Other people's packages
import argparse
from pathlib import Path
import pandas as pd
import gtfs_kit as gk
from collections import namedtuple
# import operator # for operator.not_
from weasyprint import HTML as weasyHTML
from weasyprint import CSS as weasyCSS

# Local module imports: note namespaces are separate for each file/module
from tt_errors import GTFSError
from tt_errors import NoStopError
from tt_errors import TwoStopsError
from tt_errors import InputError
import tt_parse_args

# This one monkey-patches gk.Feed (sneaky) so must be imported early
import feed_enhanced

import gtfs_type_cleanup
import amtrak_agency_cleanup
import amtrak_json_stations
import amtrak_helpers

import text_presentation
from text_presentation import TimeTuple
# This is the big styler routine, lots of CSS; keep out of main namespace
from timetable_styling import (
    style_timetable_for_html,
    finish_html_timetable,
    amtrak_station_name_to_html,
    amtrak_station_name_to_multiline_text,
    amtrak_station_name_to_single_line_text,
    )

# GLOBAL VARIABLES
# Will be changed by command-line arguments, hopefully!
# Debugging on?
debug = True
# The Amtrak GTFS feed file
gtfs_filename="./gtfs-amtrak.zip"
# The output directory
output_dirname="."
# The date we are preparing timetables for (overrideable on command line)
reference_date = 20211202

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
    "Prints an table as HTML to a file, for debugging.  Directory and suffix are added."
    with open(''.join([output_dirname,'/',filename,'.html']),'w') as outfile:
	    print(table.to_html(), file=outfile)

def print_to_file(string, filename):
    "Prints a string, probably html, to a file, for output.  Directory and suffix are added."
    "Needs work, obviously, but good enough for now."
    with open(''.join([output_dirname, '/',filename,'.html']),'w') as outfile:
	    print(string, file=outfile)


#### INITIALIZATION CODE
def initialize_feed():
    global master_feed
    global enhanced_agency
    global lookup_route_id
    # The following is read-only
    # global gtfs_filename

    path = Path(gtfs_filename)
    # Amtrak has no shapes file, so no distance units.  Check this if a shapes files appears.
    # Also affects display miles so default to mi.
    master_feed = gk.read_feed(path, dist_units='mi')

    master_feed.validate()

    # Fix types on every table in the feed
    gtfs_type_cleanup.fix(master_feed)

    # Clean up Amtrak agency list.  Includes fixing types.
    # This is non-reversible, so give it its own variable.
    enhanced_agency = amtrak_agency_cleanup.revised_amtrak_agencies(master_feed.agency)

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
    '''
    Changes the feed in place to fix known errors.
    '''
    # Cardinal 1051 (DST switch date) with wrong direction ID

    # There's an error in the trips. Attempt to fix it.
    # THIS WORKS for fixing errors in a feed.  REMEMBER IT.
    my_trips = feed.trips
    problem_index = my_trips.index[my_trips["trip_short_name"] == "1051"]
    # print (problem_index)
    # print (my_trips.iloc[problem_index])
    my_trips.at[problem_index,"direction_id"] = 0 # set in place
    # print (my_trips.iloc[problem_index])
    # Error fixed.  Put back into the feed.
    feed.trips = my_trips
    return

### END OF INITIALIZATION CODE

# Convenience functions for the currently-global route_id and station_name lookup tables
def route_id(route_name):
    "Given a route long name, return the ID."
    return lookup_route_id[route_name]

def station_name(code):
    "Given a station code, return the printable name."
    return lookup_station_name[code]

### Template loading and parsing code

def load_template(csv_filename):
    '''
    Load a template from a CSV file
    '''
    template = pd.read_csv(csv_filename, index_col=False, header=None, dtype = str)
    return template

def augment_template(raw_template):
    '''
    Fill in the station list for a template if it has a key code.
    Cell 0,0 is normally blank.
    If it is "Stations of 59", then (a) assume there is only one template row;
    (b) get the stations for 59 and fill the rows in from that
    '''
    if (pd.isna(raw_template.iloc[0,0]) ):
        # No key code, nothing to do
        return template
    key_code = str(raw_template.iloc[0,0])
    if (debug):
        print("Key code: " + key_code)
    if key_code.startswith("stations of "):
        key_train_name = key_code[len("stations of "):]
        stations_df = stations_list_from_trip_short_name(key_train_name)
        new_template = raw_template.iloc[0:,] # Get first row
        new_template.iloc[0,0] = float("nan") # Blank out key_code
        newer_template = pd.concat([new_template,stations_df]) # Yes, this works
        return newer_template

    raise InputError("Key cell must be blank or 'stations of xxx', was ", key_code)
    return

def stations_list_from_template(template):
    '''
    Given a template dataframe, return the station list as a list of strings
    '''
    stations_df = template.iloc[1:,0]
    stations_list_raw = stations_df.to_list()
    stations_list_strings = [str(i) for i in stations_list_raw]
    stations_list = [i.strip() for i in stations_list_strings if i.strip() != '']
    return stations_list

def trains_list_from_template(template):
    '''
    Given a template dataframe, return the trains list as a list of strings
    '''
    trains_df = template.iloc[0,1:]
    trains_list_raw = trains_df.to_list()
    trains_list_strings = [str(i) for i in trains_list_raw]
    trains_list = [i.strip() for i in trains_list_strings]
    return trains_list

def split_trains_str (trains_str):
    '''
    Given a string like "59 / 174 / 22", return a list {"59, "174", "22"}
    Used to separate specs for multiple trains in the same timetable column.
    A single "59" will simply give {"59"}
    '''
    raw_list = trains_str.split("/")
    clean_list = [item.strip() for item in raw_list] # remove whitespace
    return clean_list

def flatten_trains_list(trains_list):
    '''
    Take a list of trains as specified in a template
    such as [NaN,'174','178/21','stations','23/1482']
    and make a flat list of all trains involved
    ['174','178','21','23','1482']
    '''
    flattened_trains_list = []
    for ts in trains_list:
        train_names = split_trains_str(ts) # Separates at the "/"
        flattened_trains_list = [*flattened_trains_list, *train_names]
    flattened_trains_set = set(flattened_trains_list)
    flattened_trains_set.discard("station")
    flattened_trains_set.discard("stations")
    flattened_trains_set.discard("")
    return flattened_trains_set

### "Compare" Debugging routines to check for changes in timetable

def compare_stop_lists(base_trip, trips):
    """
    Debugging routine.
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
    '''
    Find time changes on a route between similar services.
    See how many services with different dates are actually the same service
    '''
    route_feed = master_feed.filter_by_route_ids([route_id])
    feed = route_feed.filter_bad_service_ids(amtrak_helpers.global_bad_service_ids)

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

def prep_spec():
    # Creates a prototype timetable.  It will definitely need to be manipulated by hand.
    # Totally incomplete. FIXME
    '''put to one side for testing purposes'''
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
                                 min_dwell=0,
                                 reverse=False,
                                 train_number="" ):
    """
    Make a workable timetable for a single trip of the Cardinal or Sunset Limited.
    Assumes that stop_times has been indexed by stop_sequence, and sorted.

    doing_html: output text with HTML annotations rather than plaintext (newline vs. <br>, use of <b>, etc.)

    min_dwell: if dwell time is less than this number of minutes,
    only departure times are shown, and arrival times are unpublished.
    This is useful for shortening public timetables.

    reverse: reverses Ar/Dp -- an ugly hack for upside-down timetables.  The timetable must
    still be turned upside down manually afterwards.

    infrequent: if False (the default) the calendar is ignored.  (FOR NOW.  FIXME)
    calendar: a calendar with a single row containing the correct calendar for the service.  Optional.
    train_number: used as header for the times column
    """
    if (doing_html):
        linebreak = "<br>"
    else:
        linebreak = "\n"

    # CSS class "shortcuts"
    # in future, color will likely be changed
    bg_color_css     = "color-cornsilk"
    font_css = "font-sans-serif font-data-size"
    heading_extra_css = "align-vcenter align-center heading-font"
    heading_css      = " ".join([bg_color_css, font_css,
                                 "border-top-heavy border-bottom-heavy", heading_extra_css])
    data_css         = " ".join([bg_color_css, font_css,
                                 "border-top-light border-bottom-light", "align-top"])
    data_css_final   = " ".join([bg_color_css, font_css,
                                 "border-top-light border-bottom-heavy", "align-top"])
    data_css_initial = " ".join([bg_color_css, font_css,
                                 "border-top-heavy border-bottom-light", "align-top"])
    # left-right border shortcuts
    left_css = "border-left noborder-right"
    center_css = "noborder-left noborder-right"
    right_css = "noborder-left border-right"
    both_css = "border-left border-right"

    # Define the columns, in order, and create empty DataFrames for timetable & styler
    # By defining the columns first we avoid order dependency later
    timetable_columns = pd.Index(["NB","ArDp","Time","StationCode"])
    if (infrequent):
        timetable_columns = pd.Index(["NB","ArDp","Time","Days","StationCode"])
    timetable_base = pd.DataFrame(columns=timetable_columns)
    styler_base = pd.DataFrame(columns=timetable_columns)

    list_of_timetable_rows = [] # accumulate, then append to blank base
    list_of_styler_rows = [] # accumulate, then append to blank base

    # Use the train number as the column header for times
    time_column_prefix = "Train #"
    time_column_header = "".join([time_column_prefix, str(train_number)])
    if (doing_html):
        time_column_header = ''.join([time_column_prefix,"<br>","<strong>",str(train_number),"</strong>"])

    # This is the output table header row
    tt_dict = {}
    tt_dict["NB"] = [""]
    tt_dict["ArDp"] = [""]
    tt_dict["Time"] = [time_column_header]
    if (infrequent):
        tt_dict["Days"] = ["Days"]
    tt_dict["StationCode"] = ["Station"]
    # Stop_sequences is generally indexed 1+; so 0 is a safe index value, probably
    # Which is good because I don't know how to set any other index!
    tt_row = pd.DataFrame(tt_dict)
    list_of_timetable_rows.append(tt_row)

    # This is the parallel styler table (header row)
    # The styler table must be the exact same shape as the output table
    # -- styles will apply to each cell specifically
    styler_dict = {}
    styler_dict["NB"]            = [" ".join([heading_css, left_css])]
    styler_dict["ArDp"]          = [" ".join([heading_css, center_css])]
    if (infrequent):
        styler_dict["Time"]      = [" ".join([heading_css, center_css])]
        styler_dict["Days"]      = [" ".join([heading_css, right_css])]
    else:
        styler_dict["Time"]      = [" ".join([heading_css, right_css])]
    styler_dict["StationCode"]   = [" ".join([heading_css, both_css])]
    styler_row = pd.DataFrame(styler_dict)
    list_of_styler_rows.append(styler_row)

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

        # Prep string to print for time
        arrival = text_presentation.explode_timestr(timepoint.arrival_time)
        arrival_str = text_presentation.time_short_str(arrival)
        # HTML bold annotation for PM
        if (arrival.pm == 1 and doing_html):
            arrival_str = ''.join(["<b>",arrival_str,"</b>"])

        departure = text_presentation.explode_timestr(timepoint.departure_time)
        departure_str = text_presentation.time_short_str(departure)
        # HTML bold annotation for PM
        if (departure.pm == 1 and doing_html):
            departure_str = ''.join(["<b>",departure_str,"</b>"])

        # For infrequent services, get the "MoWeFr" string.
        daystring = ""
        if (infrequent):
          daystring = text_presentation.day_string(calendar, offset=departure.day)

        # Special treatment of first and last stops
        is_first_stop = False;
        is_last_stop = False;
        if (timepoint.Index == first_stop_number):
            is_first_stop = True;
        if (timepoint.Index == last_stop_number):
            is_last_stop = True;

        # Receive-only / Discharge-only annotation
        rd_str = ""
        receive_only = False;
        discharge_only = False;
        if (is_first_stop):
            receive_only = True; # Logically speaking... but don't annotate it
        if (is_last_stop):
            discharge_only = True; # Logically speaking... but don't annotate it
        if (timepoint.drop_off_type == 1 and timepoint.pickup_type == 0):
            if (not is_first_stop): # This is obvious at the first station
                receive_only = True;
                rd_str = "R" # Receive passengers only
                if (doing_html):
                    rd_str = "<b>R</b>"
        elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 0):
            if (not is_last_stop): # This is obvious at the last station
                discharge_only = True;
                rd_str = "D" # Discharge passengers only
                if (doing_html):
                    rd_str = "<b>D</b>"
        elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 1):
            rd_str = "*" # Not for ordinary passengers (staff only, perhaps)
        elif (timepoint.pickup_type >= 2 or timepoint.drop_off_type >= 2):
            rd_str = "F" # Flag stop of some type

        # Important note: there's currently no way to mark the infamous "L",
        # which means that the train or bus is allowed to depart ahead of time

        if (receive_only or suppress_dwell):
            # One row
            ardp_str = ""
            arrival_departure_str = departure_str
            styler_one_row = True
        elif (discharge_only):
            # One row
            ardp_str = ""
            arrival_departure_str = arrival_str
            styler_one_row = True
        elif (not reverse):
            # Dual row for time
            ardp_str = linebreak.join(["Ar","Dp"])
            arrival_departure_str = linebreak.join([arrival_str,departure_str])
            styler_one_row = False
        else: #reverse
            # Dual row for time, for reversing
            ardp_str = linebreak.join(["Dp","Ar"])
            arrival_departure_str = linebreak.join([departure_str,arrival_str])
            styler_one_row = False

        # Prettyprint the station name
        station_name_raw = lookup_station_name[timepoint.stop_id]
        if ( amtrak_helpers.is_standard_major_station(timepoint.stop_id) ):
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
        tt_row_dict["NB"]          = [rd_str]
        tt_row_dict["ArDp"]        = [ardp_str]
        tt_row_dict["Time"]        = [arrival_departure_str]
        if (infrequent):
            tt_row_dict["Days"]    = [daystring]
        tt_row_dict["StationCode"] = [station_name_str]
        tt_row = pd.DataFrame(tt_row_dict, index=[timepoint.Index])
        list_of_timetable_rows.append(tt_row)

        # Special top-bottom border treatment on first and last row
        my_data_css = data_css
        if (is_first_stop):
            my_data_css = data_css_initial
        if (is_last_stop):
            my_data_css = data_css_final
        # This is *not* order-dependent; the order is set by the first row, up above.
        sr_dict = {}
        sr_dict["NB"]           = [" ".join([my_data_css, "align-right", left_css])]
        sr_dict["ArDp"]         = [" ".join([my_data_css, "align-right", center_css])]
        if (infrequent):
            sr_dict["Time"]     = [" ".join([my_data_css, "align-right", center_css])]
            sr_dict["Days"]     = [" ".join([my_data_css, "align-left", right_css])]
        else:
            sr_dict["Time"]     = [" ".join([my_data_css, "align-right", right_css])]
        sr_dict["StationCode"]  = [" ".join([my_data_css, "align-left", both_css])]
        styler_row = pd.DataFrame(sr_dict, index=[timepoint.Index])
        list_of_styler_rows.append(styler_row)

    timetable = timetable_base.append(list_of_timetable_rows)
    print(timetable)
    styler = styler_base.append(list_of_styler_rows)
    return (timetable, styler)

def print_single_trip_tt(trip):
    '''
    Print a single trip timetable (including Cardinal and Sunset but not Texas Eagle)
    Probably not that useful, but proof of concept
    '''

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

    [timetable, styler_table] = format_single_trip_timetable( stop_times,
                                    calendar=this_feed.calendar,
                                    infrequent=infrequent,
                                    doing_html=True,
                                    min_dwell=5,
                                    train_number=train_number)
    # Run the styler on the timetable...
    timetable_styled_html = style_timetable_for_html(timetable, styler_table)
    page_title = "Timetable for Amtrak Train #" + str(train_number)
    timetable_finished_html = finish_html_timetable(timetable_styled_html, title=page_title)
    print_to_file(timetable_finished_html, ''.join([output_dirname, "/tt_",str(train_number)]) )

    # Now rerun it for weasyprint...
    html_str_for_weasy=finish_html_timetable(timetable_styled_html, title=page_title,
                                             for_weasyprint=True)
    html_for_weasy = weasyHTML(string=html_str_for_weasy)
    html_for_weasy.write_pdf(''.join([output_dirname, "/tt_",str(train_number),".pdf"]) )
    return

#### The muddle of work in progress

def trip_from_trip_short_name(trip_short_name):
    '''
    Given a single train number (trip_short_name)
    -- with an assumed global reference date
    -- and using the global master_feed.trips
    produces the trip record associated therewith.
    Raises an error if trip_short_name generates more than one trip for that date.
    '''
    # Note that reference_date and master_feed are globals.
    reduced_feed = master_feed.filter_by_trip_short_names([trip_short_name])
    today_feed = reduced_feed.filter_by_dates(reference_date, reference_date)

    # There should be only one trip.  This checks and raises errors.
    this_trip_today = today_feed.get_single_trip()
    return this_trip_today

def stations_list_from_trip_short_name(trip_short_name):
    '''
    Produces a station list from a single train number.
    This is generally used to make a template, not directly.
    '''

    trip_id = trip_from_trip_short_name(trip_short_name).trip_id

    stop_times = master_feed.filter_by_trip_ids([trip_id]).stop_times
    station_list = stop_times['stop_id']
    if (debug):
        print (station_list)
    return station_list

def get_timepoint (trip_short_name, station_code):
    '''
    Given a trip_short_name (Amtrak train number) and station_code,
    extract the single timepoint (as a Series) from the stop_times GTFS feed

    Throw TwoStopsError if it stops here twice.

    Throw NoStopError if it doesn't stop here.  This is expensive and should be changed.
    '''
    trip_id = trip_from_trip_short_name(trip_short_name).trip_id
    stop_times = master_feed.filter_by_trip_ids([trip_id]).stop_times
    timepoint_df = stop_times.loc[stop_times['stop_id'] == station_code]
    if (timepoint_df.shape[0] == 0):
        raise NoStopError(' '.join(["Train number", trip_short_name,
                                  "does not stop at station code",
                                  station_code,
                                 ]) )
    if (timepoint_df.shape[0] > 1):
        raise TwoStopsError(' '.join(["Train number", trip_short_name,
                                  "stops at station code",
                                  station_code,
                                  "more than once"
                                 ]) )
    timepoint = timepoint_df.iloc[0] # Pull out the one remaining row
    return timepoint

def get_dwell_secs (trip_short_name, station_code):
    '''
    Gets dwell time in seconds for a specific train at a specific station
    '''
    try:
        timepoint = get_timepoint(trip_short_name, station_code)
    except (NoStopError):
        # If the train doesn't stop there, the dwell time is zero;
        # and we need thie behavior for make_stations_max_dwell_map
        return 0

    departure_secs = gk.timestr_to_seconds(timepoint.departure_time)
    arrival_secs = gk.timestr_to_seconds(timepoint.arrival_time)
    dwell_secs = departure_secs - arrival_secs
    return dwell_secs

def make_stations_max_dwell_map (template, dwell_secs_cutoff):
    '''
    Extract list of stations and list of train names from template.
    Create a dict from station_code to dwell_secs
    If any train in train_names has a dwell time of dwell_secs or longer at a station,
    then the dict returns True, otherwise False
    '''
    stations_dict = {}
    stations_list = stations_list_from_template(template)

    trains_list = trains_list_from_template(template) # Note still contains "/" items
    flattened_trains_set = flatten_trains_list(trains_list)

    for s in stations_list:
        max_dwell_secs = 0
        for t in flattened_trains_set:
            max_dwell_secs = max( max_dwell_secs, get_dwell_secs(t, s) )
        if (max_dwell_secs >= dwell_secs_cutoff):
            stations_dict[s] = True
        else:
            stations_dict[s] = False
    return stations_dict

### Work for "fancy-two"

def return_true (station_code):
    '''
    Takes one argument; returns True
    '''
    return True

def return_false (station_code):
    '''
    Takes one argument; returns True
    '''
    return False

def fill_template(template,
                  doing_html=False,
                  doing_multiline_text=True,
                  is_major_station="standard",
                  is_ardp_station="dwell", dwell_secs_cutoff=300,
                 ):
    '''
    Fill a template using GTFS data
    Template must be complete (run augment_template first)
    doing_html: Produce HTML timetable.  Default is false (produce plaintext timetable).
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
        or higher for some train in the template
        Defaults to 300, meaning 5 minutes.
        Probably don't want to ever make it less than 1 minute.
    '''

    tt = template.copy() # "deep" copy
    dp_tt = template.copy()
    ar_tt = template.copy()

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
        is_major_station = return_false
    elif (is_major_station == "standard"):
        is_major_station = amtrak_helpers.is_standard_major_station
    if not callable(is_major_station):
        raise TypeError ("Received is_major_station which is not callable: ", is_major_station)

    if (is_ardp_station == False):
        is_ardp_station = return_false
    elif (is_ardp_station == True):
        is_ardp_station = return_true
    elif (is_ardp_station == "dwell"):
        # Prep max dwell map
        stations_max_dwell_map = make_stations_max_dwell_map (template, dwell_secs_cutoff)
        is_ardp_station = lambda station_code : stations_max_dwell_map[station_code]
    if not callable(is_ardp_station):
        raise TypeError ("Received is_ardp_station which is not callable: ", is_ardp_station)

    [row_count, column_count] = template.shape
    for x in range(1, column_count): # First (0) column is the station code
        train_names_str = str(template.iloc[0, x]).strip() # row 0, column x
        train_names = split_trains_str(train_names_str) # Separates at the "/"
        for y in range(1, row_count): # First (0) row is the header
            station_code = template.iloc[y, 0] # row y, column 0
            print ("We are at ", y, " ", x)
            # Consider, here, whether to build parallel tables.
            # This allows for the addition of extra rows.
            if (not pd.isna(tt.iloc[y,x])):
                # It already has a value.
                # This is probably special text like "to Chicago".
                # We keep this.  (But note: should we HTML-ize it? FIXME )
                pass
            else:
                # Blank to be filled in -- the usual case.
                if train_names_str in ["station","stations"]: # Column for station names
                    station_name_raw = lookup_station_name[station_code]
                    major = amtrak_helpers.is_standard_major_station(station_code)
                    station_name_str = prettyprint_station_name(station_name_raw, major)
                    tt.iloc[y,x] = station_name_str
                else: # It's a train number.
                    #
                    # For a slashed train spec ( 549 / 768 ) pull the *first* train's times,
                    # then the second train's times *if the first train doesn't stop there*
                    # If the first train terminates and the second train starts, we need to
                    # somehow make it an ArDp station with double lines... tricky, not done yet
                    print(train_names)
                    print(station_code)
                    placeholder = ' '.join([ train_names[0],
                                             station_code,
                                             ("M" if is_major_station(station_code) else ""),
                                             ("ArDp" if is_ardp_station(station_code) else ""),
                                           ])
                    print(placeholder)
                    tt.iloc[y,x] = placeholder

    return (tt, template) # This is all wrong, it should be tt, styler, but for testing FIXME

#### Work for "fancy-one"

def compute_prototype_timetable(stations_list):
    '''
    Given a stations list from a template,
    return a DataFrame with two columns, (0, stop_sequence) and (0, stop_id)
    reflecting how the timetable should be arranged.
    '''
    tt_stations_list = stations_list
    # Set up stations list in correct order
    tt_stations_list_df = pd.DataFrame(tt_stations_list, columns=[(0,"stop_id")])

    # Set up 1-indexed list for stop_sequence
    tt_stop_seq_list = [*range(1,len(tt_stations_list)+ 1, 1)] # Note * 'unpacks'
    tt_stop_seq_df = pd.DataFrame(tt_stop_seq_list, columns=[(0,"stop_sequence")])

    # Assemble the two and set the station code as the index (for future use)
    tt_df = pd.concat([tt_stop_seq_df, tt_stations_list_df], axis="columns")
    tt_df = tt_df.set_index((0, 'stop_id'))
    # This gives us the prototype timetable
    return tt_df

def compute_station_names_df(stations_list):
    '''
    Given a stations list from a template,
    return a DataFrame with three columns, (0, stop_sequence), (0, stop_id),
    and (0, station) containing the station names.
    Severe duplication with compute_prototype_timetable.  Oh well.
    '''
    tt_stations_list = stations_list
    # Set up parallel station names list
    tt_station_names_list = [station_name(code) for code in tt_stations_list]

    # Convert both to parallel DataFrames
    tt_stations_list_df = pd.DataFrame(tt_stations_list, columns=[(0,'stop_id')])
    tt_station_names_list_df = pd.DataFrame(tt_station_names_list, columns=[(0,"station")])

    # Assemble the two and set the station code as the index (for future use)
    tt_df = pd.concat([tt_stations_list_df, tt_station_names_list_df], axis="columns")
    tt_df = tt_df.set_index((0, 'stop_id'))
    # This gives us the prototype timetable
    return tt_df



def main_func_future(template):
    # In order to combine the timetables, we need a prior and exterior stop list
    # which specifies the order the stops will appear in *in the timetable*.
    # This has to be human-curated; consider Silver Service with the split in the Carolinas.
    # Which branch gets listed first?  Can't be automatically determined.
    #
    # So we need a prototype timetable, passed in.
    print(template)
    tt_trains_list = trains_list_from_template(template)
    print ("Trains in order:", tt_trains_list)
    tt_stations_list = stations_list_from_template(template)
    print ("Stations in order: ", tt_stations_list)
    print ("Recalculated timetable: ")
    tt_df = compute_prototype_timetable(tt_stations_list)
    print (tt_df)

    todays_feed = master_feed.filter_by_dates(reference_date, reference_date)
    reduced_feed = todays_feed # FIXME -- preemptively remove irrelevant data

    list_of_timetables = [tt_df]
    list_of_train_numbers = []
    for train_number in tt_trains_list:
        if (train_number in ["station","stations"]):
            tt_station_names_df = compute_station_names_df(tt_stations_list)
            # Sort by station ID...
            # tt_station_names_df = tt_station_names_df.set_index((0, 'stop_id'))
            # It's set as the index in compute_station_names; can't set it twice

            list_of_timetables.append(tt_station_names_df)
            list_of_train_numbers.append("station")
            print(tt_station_names_df)

        else: # column is not "stations"
            # In future this will be more complex with two trains in one column, but for now...
            desired_feed = reduced_feed.filter_by_trip_short_names([train_number])
            try:
                # This should now be a single-item list, so extract the item...
                my_trip = desired_feed.get_single_trip()
            except NoTripError:
                print( ''.join(["No trip for ",train_number,", skipping"]) )
            except TwoTripsError:
                raise TwoTripsError("Error: filter found two trips with the same train number:", desired_feed.trips)
            stop_times = desired_feed.get_single_trip_stop_times(my_trip.trip_id)
            stop_times.reset_index(inplace=True)

            # Sanity check:
            proper_train_number = my_trip.trip_short_name
            if (proper_train_number != train_number):
                raise GTFSError( ''.join(["Weirdness: trip for ", train_number," has train number ", proper_train_number]) )

            # Multi-index is clunky, so just use tuples as column names
            # which is completely valid
            # Use "0" to mean "shared between trains"
            # This worked but felt ugly.
            # For debugging reasons, massively shorten column names
            # new_index_map = { 'stop_sequence'  : (train_number, 'stop_sequence'),
            #                  'trip_id'        : (train_number, 'trip_id'),
            #                  'arrival_time'   : (train_number, 'arrival_time'),
            #                  'departure_time' : (train_number, 'departure_time'),
            #                  'pickup_type'    : (train_number, 'pickup_type'),
            #                  'drop_off_type'  : (train_number, 'drop_off_type'),
            #                  'stop_id'        : (0, 'stop_id')
            #                }

            # Rename columns to allow concat to work...
            new_index_map = { 'stop_sequence'  : (train_number, 'seq'),
                              'trip_id'        : (train_number, 'trip_id'),
                              'arrival_time'   : (train_number, 'ar_t'),
                              'departure_time' : (train_number, 'dp_t'),
                              'pickup_type'    : (train_number, 'p'),
                              'drop_off_type'  : (train_number, 'd'),
                              'stop_id'        : (0, 'stop_id')
                            }
            stop_times = stop_times.rename(new_index_map,axis='columns')

            # Sort by station ID...
            stop_times = stop_times.set_index((0, 'stop_id'))
            list_of_timetables.append(stop_times)
            list_of_train_numbers.append(train_number)
            print (stop_times)

    # Out of the for loop now.  Merge the pieces.
    # Note that this merges on the index, which is carefully set to be the same for all pieces
    # (namely, it's set on (0, 'stop_id')
    full_timetable = pd.concat(list_of_timetables,axis="columns")

    # NOTE!  This is a huge issue!  This works for the CONO, but if you try it for the Illini,
    # it will add back in all the CONO stations!  That is not what is wanted.
    # It becomes essential to filter out stops which have NaN in the stop_sequence column.
    proper_timetable = full_timetable[full_timetable[(0,'stop_sequence')].notna()]
    # FIXME

    # Drop columns which are not important to the main merge algorithm, for readability
    # Ignore errors if some of the columns to be dropped don't exist
    trimmed_timetable = proper_timetable
    for train_number in list_of_train_numbers:
        trimmed_timetable = trimmed_timetable.drop((train_number,'trip_id'),
                                                    axis='columns', errors='ignore')
        trimmed_timetable = trimmed_timetable.drop((train_number,'p'),
                                                    axis='columns', errors='ignore')
        trimmed_timetable = trimmed_timetable.drop((train_number,'d'),
                                                    axis='columns', errors='ignore')
        trimmed_timetable = trimmed_timetable.drop((train_number,'ar_t'),
                                                    axis='columns', errors='ignore')
        trimmed_timetable = trimmed_timetable.drop((train_number,'seq'),
                                                    axis='columns', errors='ignore')
    print(trimmed_timetable)

    quit()

##########################
#### NEW MAIN PROGRAM ####
##########################
if __name__ == "__main__":
    print ("Made it to the main program")

    my_arg_parser = tt_parse_args.make_tt_arg_parser()
    args = my_arg_parser.parse_args()
    # These have defaults; override from command line.
    # NOTE!  We are not in a function so don't need global keyword
    debug = args.debug
    if (args.gtfs_filename):
        gtfs_filename = args.gtfs_filename
    if (args.output_dirname):
        output_dirname = args.output_dirname
    if (args.reference_date):
        reference_date = args.reference_date

    initialize_feed() # This sets various globals

    # Create the station name lookup table, a global
    # Expects JSON stations to be downloaded already (go easy on Amtrak bandwidth!)
    lookup_station_name = amtrak_json_stations.make_station_name_lookup_table()
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

        station_list_df = stations_list_from_trip_short_name(tsn)
        output_filename = "".join([output_dirname, "/", "tt_", tsn, "_","stations.csv"])
        station_list_df.to_csv(output_filename,index=False)
        # Note: this will put "stop_id" in top row, which is OK
        quit()

    if (args.type == "single"):
        # Single timetable.
        # This is the old, one-train printer.
        # It works, but is not good.

        trip_short_name = args.trip_short_name
        trip = trip_from_trip_short_name(trip_short_name)
        print_single_trip_tt(trip)
        quit()

    if (args.type == "updown"):
        # Single-service "up down" timetable.
        # Work in progress
        # prep_spec was an attempt to do this which failed... FIXME
        print("unimplemented")
        quit()

    if (args.type == "template"):
        # Make a template (work in progress)
        print ("unfinished")
        quit()

    if (args.type == "compare"):
        route_long_name = args.route_long_name
        compare_similar_services(route_id(route_long_name))
        quit()

    if (args.type == "fancy-one"):
        # Use a template (work in progress)
        template = load_template(args.template_filename)
        template = augment_template(template)
        main_func_future(template);
        quit()

    if (args.type == "fancy-two"):
        template = load_template(args.template_filename)
        template = augment_template(template)
        print (template)
        (timetable, styler_table) = fill_template(template,
                      is_major_station=amtrak_helpers.is_standard_major_station,
                      is_ardp_station="dwell")
        timetable.to_csv("test_out.csv", index=False, header=False)
        print ("getting going")
        print (timetable)
        # timetable_styled_html = style_timetable_for_html(timetable, styler_table)
        # print_to_file(timetable_styled_html, ''.join([output_dirname, "/tt_",str(train_number)]
        quit()

    if (args.type == "test"):
        template = load_template(args.template_filename)
        template = augment_template(template)
        dwell_secs = get_dwell_secs("59","CDL")
        print("Dwell is", dwell_secs)
        # print(stations_list_from_template(new_template))
        # name = lookup_station_name["BUF"]
        # fancy_name = text_presentation.fancy_amtrak_station_name(name, major=True)
        # print(fancy_name);
        quit()

