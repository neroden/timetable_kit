#! /usr/bin/python3
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
import operator # for opperator.not_

# Local module imports: note namespaces are separate for each file/module
import tt_parse_args
import gtfs_type_cleanup
import amtrak_agency_cleanup
import text_presentation
from text_presentation import TimeTuple
# This is the big styler routine, lots of CSS; keep out of main namespace
from timetable_styling import style_timetable_for_html

# GLOBAL VARIABLES
# Will be changed by command-line arguments, hopefully!
# The Amtrak GTFS feed file
gtfs_filename="./gtfs-amtrak.zip"
# The output directory
output_dirname="."
# The date we are preparing timetables for (overrideable on command line)
reference_date = 20211202

# GLOBAL VARIABLES
# The master variable for the feed; overwritten in initialize_feed
feed=None
# The enhanced agency list; likewise
enhanced_agency=None
# Lookup table from route name to route id, likewise
lookup_route_id=None
# Trip lookup table, currently unused
trip_lookup_table=None

# GLOBAL VARIABLES
# Known problems in Amtrak data
global_bad_service_ids = [2819372, # Cardinal one-day service when it doesn't run on that day
                         ]

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
    global feed
    global enhanced_agency
    global lookup_route_id
    # The following is read-only
    # global gtfs_filename

    path = Path(gtfs_filename)
    # Amtrak has no shapes file, so no distance units.  Check this if a shapes files appears.
    # Also affects display miles so default to mi.
    feed = gk.read_feed(path, dist_units='mi')

    feed.validate()

    # Fix types on every table in the feed
    gtfs_type_cleanup.fix(feed)

    # Clean up Amtrak agency list.  Includes fixing types.
    # This is non-reversible, so give it its own variable.
    enhanced_agency = amtrak_agency_cleanup.revised_amtrak_agencies(feed.agency)

    # Create lookup table from route name to route id. Amtrak only has long names, not short names.
    lookup_route_id = dict(zip(feed.routes.route_long_name, feed.routes.route_id))

    # Create a lookup table by trip id... all trips... belongs elsewhere
    indexed_trips = feed.trips.set_index('trip_id')
    global trip_lookup_table
    trip_lookup_table = indexed_trips.to_dict('index')
    # print(trip_lookup_table) # this worked

### END OF INITIALIZATION CODE

# Convenience function for the route_id lookup table
def route_id(route_name):
    "Given a route long name, return the ID."
    return lookup_route_id[route_name]

def filter_calendar_by_effective_date(calendar, effective_date: int):
    "Return version of the calendar DataFrame only containing rows with service_ids valid on the given date.  effective_date is a GTFS date string (YYYYMMDD) converted to an integer for fast comparison"
    # Remove expired schedules
    filtered_calendar = calendar[calendar.end_date >= effective_date]
    # Remove future schedules
    double_filtered_calendar = filtered_calendar[filtered_calendar.start_date <= effective_date]
    return double_filtered_calendar

def filter_calendar_by_service(calendar, service_ids):
    "Retun a much shorter version of the calendar DataFrame containing only the specified services."
    filtered_calendar = calendar[calendar.service_id.isin(service_ids)]
    return filtered_calendar

def filter_trips_by_route(trips, route_ids):
    "Return a much shorter version of the trips DataFrame containing only the specified routes."
    filtered_trips = trips[trips.route_id.isin(route_ids)]
    return filtered_trips

def filter_trips_for_garbage(trips, bad_service_ids):
    "Return version of the trips DataFrame without known-bad services."
    filtered_trips = trips[trips.service_id.isin(bad_service_ids).apply(operator.not_)]
    return filtered_trips

def filter_trips_by_service(trips, service_ids):
    "Return a much shorter version of the trips DataFrame containing only the specified services."
    filtered_trips = trips[trips.service_id.isin(service_ids)]
    return filtered_trips

def filter_trips_by_calendar(trips, calendar):
    "Return a much shorter version of the trips DataFrame containing only trips with service_ids in the specified calendar."
    service_ids = calendar["service_id"].array
    filtered_trips = trips[trips.service_id.isin(service_ids)]
    return filtered_trips

#def filter_trips_by_effective_date(trips, effective_date)
#    "Return version of the trips DataFrame only containing trips with service_ids valid on the given date."

def filter_stop_times_by_trip(stop_times, trip_ids):
    "Return a much shorter version of the stop_times DataFrame containing only the specified trips."
    filtered_stop_times = stop_times[stop_times.trip_id.isin(trip_ids)]
    return filtered_stop_times

# The following is probably unnecessary if we do it at the filter_trips_for_garbage level.
def filter_stop_times_for_garbage(stop_times, bad_service_ids):
    "Return version of the stop_times DataFrame without known-bad services."
    filtered_stop_times = stop_times[stop_times.service_id.isin(bad_service_ids).apply(operator.not_)]
    return filtered_stop_times

def single_trip_stop_times(trip_id):
    "Stop times sorted into correct order.  Depends on global variable feed."
    stop_times_1 = filter_stop_times_by_trip(feed.stop_times, [trip_id])
    stop_times_2 = stop_times_1.set_index("stop_sequence")
    stop_times_3 = stop_times_2.sort_index()
    return stop_times_3

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
    heading_extra_css = "align-vcenter align-center heading-font"
    heading_css      = " ".join([bg_color_css, "border-top-heavy border-bottom-heavy", heading_extra_css])
    data_css         = " ".join([bg_color_css, "border-top-light border-bottom-light", "align-top"])
    data_css_final   = " ".join([bg_color_css, "border-top-light border-bottom-heavy", "align-top"])
    data_css_initial = " ".join([bg_color_css, "border-top-heavy border-bottom-light", "align-top"])
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
    tt_dict["StationCode"] = ["Station Code"]
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

        # This is *not* order-dependent; the order is set by the first row, up above.
        tt_row_dict = {}
        tt_row_dict["NB"]          = [rd_str]
        tt_row_dict["ArDp"]        = [ardp_str]
        tt_row_dict["Time"]        = [arrival_departure_str]
        if (infrequent):
            tt_row_dict["Days"]    = [daystring]
        tt_row_dict["StationCode"] = [timepoint.stop_id]
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

#def generate_triplist_for_route(route_ids,
#                                 effective_date,
#                                 direction="twoway",
#                                 min_dwell=0,
#                                ):
#    '''
#    effective_date -- filter for the route on the given date (GTFS frequently has MANY dates)
#    min_dwell -- suppress arrival times where dwell time is less than min_dwell minutes
#
#    '''
#    route_filtered_trips = route_filter(feed.trips, route_ids)


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
    base_stop_times = single_trip_stop_times(base_trip["trip_id"])
    base_stop_times = base_stop_times.drop(["trip_id"], axis="columns")
    for trip in (trips.itertuples()):
        stop_times = single_trip_stop_times(trip.trip_id)
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

def compare_similar_services(route_id):
    '''
    Find time changes on a route between similar services.
    See how many services with different dates are actually the same service
    '''
    my_trips = filter_trips_by_route(feed.trips, [route_id])
    my_trips = filter_trips_for_garbage(my_trips, global_bad_service_ids)

    print("Downbound:")
    downbound_trips = my_trips[my_trips.direction_id == 0] # W for LSL
    print(downbound_trips)
    base_trip = downbound_trips.iloc[0, :] # row 0, all columns
    compare_stop_lists(base_trip,downbound_trips)

    print("Upbound:")
    upbound_trips = my_trips[my_trips.direction_id == 1] # E for LSL
    print(upbound_trips)
    base_trip = upbound_trips.iloc[0, :] # row 0, all columns
    compare_stop_lists(base_trip,upbound_trips)
    return


def filter_trips_for_timetable(trips, route_ids, direction=None, date=reference_date):
    '''
    Filter trips by:
        route_ids
        (single) calendar_date
        direction; 0, 1, or None for do-not-filter
        0 'upbound' for West LSL/Cardinal, and North CONO
        1 'downbound' for East LSL/Cardinal, and South CONO
    '''
    my_trips = filter_trips_by_route(trips, route_ids)
    todays_calendar = filter_calendar_by_effective_date(feed.calendar, reference_date)
    my_trips = filter_trips_by_calendar(my_trips, todays_calendar)
    if (direction in [0,1]):
        my_trips = my_trips[my_trips.direction_id == direction]
    return my_trips
    pass

def fix_known_errors(feed):
    '''
    Changes the feed in place to fix known errors.
    '''
    # Cardinal 1051 (DST switch date) with wrong direction ID

    # There's an error in the trips. Attempt to fix it.
    # THIS WORKS for fixing errors in a feed.  REMEMBER IT.
    my_trips = feed.trips
    problem_index = my_trips.index[my_trips["trip_short_name"] == 1051]
    # print (problem_index)
    # print (my_trips.iloc[problem_index])
    my_trips.at[problem_index,"direction_id"] = 0 # set in place
    # print (my_trips.iloc[problem_index])
    # Error fixed.  Put back into the feed.
    feed.trips = my_trips
    return

def parse_timetable_spec(filename):
    '''
    Parse a timetable spec file.
    The specs for this are still evolving, however:
    - First line: a list of train numbers in correct column order,
        with the word "station" (no quotes) for where the station names go
    - Remaining lines:
        List of station codes in order from top to bottom
    Returns:
    - (train number list, station code list)
    Whitespace is trimmed on the edges of each element.
    '''
    # First test file is cono.spec
    with open(filename, 'r') as spec_file:
        entire_file = spec_file.read()
    # Split the first line from the rest
    [trains_str, stations_str] = entire_file.split("\n",1)

    trains_list_raw = trains_str.split(",")
    trains_list = [element.strip() for element in trains_list_raw]

    stations_list_raw = stations_str.split("\n")
    stations_list = [element.strip() for element in stations_list_raw if element.strip() != '']

    return (trains_list, stations_list)

def compute_prototype_timetable(stations_list):
    '''
    Given a stations list as returned by parse_timetable_spec,
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

def main_func_future():

    # We need a prototype timetable.  If we aren't ready to prototype yet, we can do without it,
    # but we'll have to bail out partway through
    prototyping = True
    if prototyping:
        # FIXME -- hardwired to the CONO
        spec_pathname = ''.join([output_dirname, "/", "cono.spec"])
        [tt_trains_list, tt_stations_list] = parse_timetable_spec(spec_pathname)
        print ("we got this...")
        print (tt_trains_list)
        print ("and this...")
        tt_df = compute_prototype_timetable(tt_stations_list)
        print (tt_df)

    '''put to one side for testing purposes'''
    route_ids = [route_id("Illini"),route_id("Saluki"),route_id("City Of New Orleans")]

    fix_known_errors(feed)

    my_trips = feed.trips
    # reference_date is currently a global
    upbound_trips = filter_trips_for_timetable(my_trips, route_ids, direction=0, date=reference_date)
    print("Upbound:")
    print(upbound_trips)
    downbound_trips = filter_trips_for_timetable(my_trips, route_ids, direction=1, date=reference_date)
    print("Downbound:")
    print(downbound_trips)
    allbound_trips = filter_trips_for_timetable(my_trips, route_ids, date=reference_date)
    print("Allbound:")
    print(allbound_trips)


    # So.  In order to combine the timetables, we need a prior and exterior stop list
    # which specifies the order the stops will appear in *in the timetable*.
    # This has to be human-curated; consider Silver Service with the split in the Carolinas.
    # Which branch gets listed first?  Can't be automatically determined.
    # This is tt_df, from compute_prototype_timetable
    if prototyping:
        list_of_timetables = [tt_df]
    else:
        list_of_timetables = []
    list_of_train_numbers = []
    for trip in allbound_trips.itertuples(index=False):

        stop_times = single_trip_stop_times(trip.trip_id)
        stop_times.reset_index(inplace=True)
        train_number = trip.trip_short_name

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
    # Drop columns which are not important to the main merge algorithm, for readability
    trimmed_timetable = full_timetable
    for train_number in list_of_train_numbers:
        trimmed_timetable = trimmed_timetable.drop((train_number,'trip_id'),axis='columns')
        trimmed_timetable = trimmed_timetable.drop((train_number,'p'),axis='columns')
        trimmed_timetable = trimmed_timetable.drop((train_number,'d'),axis='columns')
        trimmed_timetable = trimmed_timetable.drop((train_number,'ar_t'),axis='columns')
        trimmed_timetable = trimmed_timetable.drop((train_number,'seq'),axis='columns')
    print(trimmed_timetable)

    quit()

def print_single_trip_tt(trip):
    '''
    Print a single trip timetable (including Cardinal and Sunset but not Texas Eagle)
    Probably not that useful, but proof of concept
    '''

    stop_times = single_trip_stop_times(trip.trip_id)
    train_number = trip.trip_short_name

    # Extract the service days of the week
    # Filter to the calendar for the specific service

    todays_calendar = filter_calendar_by_effective_date(feed.calendar, reference_date)
    # Unused, but should use
    # todays_service_ids = todays_calendar["service_id"].array
    calendar_for_service = filter_calendar_by_service(todays_calendar, [trip.service_id])
    # Should give exactly one calendar -- we don't test that here, though
    daystring = text_presentation.day_string(calendar_for_service)
    if (daystring == "Daily"):
        infrequent = False
    else:
        infrequent = True
        # This is not really correct; but it's good enough for once-a-day overnights.
        # Trains which don't run overnight should never be marked "infrequent", because
        # the days can be at the top of the column instead of next to the time.

    [timetable, styler_table] = format_single_trip_timetable( stop_times,
                                    calendar=calendar_for_service,
                                    infrequent=infrequent,
                                    doing_html=True,
                                    min_dwell=5,
                                    train_number=train_number)
    # Run the styler on the timetable...
    timetable_styled_html = style_timetable_for_html(timetable, styler_table)

    print_to_file(timetable_styled_html, ''.join([output_dirname, "/tt_",str(train_number)]) )

##########################
#### NEW MAIN PROGRAM ####
##########################
if __name__ == "__main__":
    print ("Made it to the main program")

    my_arg_parser = tt_parse_args.make_tt_arg_parser()
    args = my_arg_parser.parse_args()
    # These have defaults; override from command line.
    # NOTE!  We are not in a function so don't need global keyword
    if (args.gtfs_filename):
        gtfs_filename = args.gtfs_filename
    if (args.output_dirname):
        output_dirname = args.output_dirname
    if (args.reference_date):
        reference_date = args.reference_date

    initialize_feed() # This sets various globals
    dumptable(feed.routes, "routes") # Generates routes.html

    if not (args.type):
        print ("No type of timetable specified.")
        quit()

    if (args.type == "single"):
        # Single timetable.
        # This is the old, one-train printer.
        # It works, bit is not good.  Hardcoded to Cardinal.

        fix_known_errors(feed)

        route_ids = [route_id("Cardinal")]

        my_trips = feed.trips
        # reference_date is currently a global
        upbound_trips = filter_trips_for_timetable(my_trips, route_ids, direction=0, date=reference_date)
        print("Upbound:")
        print(upbound_trips)
        downbound_trips = filter_trips_for_timetable(my_trips, route_ids, direction=1, date=reference_date)
        print("Downbound:")
        print(downbound_trips)
        allbound_trips = filter_trips_for_timetable(my_trips, route_ids, date=reference_date)
        print("Allbound:")
        print(allbound_trips)

        for trip in allbound_trips.itertuples(index=False):
            print_single_trip_tt(trip)
            break
            # Doesn't actually work for multiple trips.  Oh dear.
        quit()

    if (args.type == "template"):
        # Make a template (work in progress)
        compare_similar_services(route_id("Cardinal"))

    if (args.type == "fancy"):
        # Use a template (work in progress)
        main_func_future();
        quit()

