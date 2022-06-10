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
import os  # for os.getenv
import os.path  # for os.path abilities
import sys  # Solely for sys.path and solely for debugging
import shutil  # To copy files
import json

import pandas as pd
import gtfs_kit as gk
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
    InputError,
)
from timetable_kit.debug import set_debug_level, debug_print
from timetable_kit.timetable_argparse import make_tt_arg_parser

# This one monkey-patches gk.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

from timetable_kit.feed_enhanced import gtfs_days

# To intialize the feed -- does type changes
from timetable_kit.initialize import initialize_feed

# For reversing the type changes to output GTFS again
from timetable_kit import gtfs_type_cleanup

from timetable_kit import amtrak  # so we don't have to say "timetable_kit.amtrak"

# To make it easier to isolate Amtrak dependencies in the main code, we always explicitly call:
# amtrak.special_data
# amtrak.json_stations

from timetable_kit import text_presentation
from timetable_kit import icons

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
    train_spec_to_tsn,
    make_trip_id_to_tsn_dict,
    find_tsn_dupes,
    make_tsn_to_trip_id_dict,
    make_tsn_and_day_to_trip_id_dict,
    stations_list_from_tsn,
)

### tt-spec loading and parsing code

### Constant set for the special column names.
### These should not be interpreted as trip_short_names or train numbers.
special_column_names = {
    "",
    "station",
    "stations",
    "services",
    "access",
    "timezone",
}


def load_ttspec_json(filename):
    """Load the JSON file for the tt-spec"""
    path = Path(filename)
    if path.is_file():
        with open(path, "r") as f:
            auxfile_str = f.read()
            aux = json.loads(auxfile_str)
            debug_print(1, "tt-spec JSON file loaded")
            return aux
        print("Shouldn't get here, file load failed.")
    else:
        # Make it blank, basically
        debug_print(1, "No tt-spec JSON file.")
        return {}


def load_ttspec_csv(filename):
    """Load a tt-spec CSV file"""
    ttspec_csv = pd.read_csv(filename, index_col=False, header=None, dtype=str)
    return ttspec_csv


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
    if pd.isna(raw_tt_spec.iloc[0, 0]):
        # No key code, nothing to do
        return raw_tt_spec
    key_code = str(raw_tt_spec.iloc[0, 0])
    debug_print(3, "Key code: " + key_code)
    if key_code.startswith("stations of "):
        # Filter the feed down to a single date...
        today_feed = feed.filter_by_dates(date, date)

        # Find the train name and possibly filter by day...
        key_train_name = key_code.removeprefix("stations of ")
        for day in gtfs_days:
            if key_train_name.endswith(day):
                key_train_name = key_train_name.removesuffix(day).strip()
                today_feed = today_feed.filter_by_day_of_week(day)
                break

        # And pull the stations list
        stations_df = stations_list_from_tsn(today_feed, key_train_name)
        new_tt_spec = raw_tt_spec.copy()  # Copy entire original spec
        new_tt_spec.iloc[0, 0] = float("nan")  # Blank out key_code
        newer_tt_spec = pd.concat([new_tt_spec, stations_df])  # Yes, this works
        # The problem is that it leads to duplicate indices (ugh!)
        # So fully reset the index
        newest_tt_spec = newer_tt_spec.reset_index(drop=True)
        debug_print(1, newest_tt_spec)
        return newest_tt_spec

    raise InputError("Key cell must be blank or 'stations of xxx', was ", key_code)


def stations_list_from_tt_spec(tt_spec):
    """Given a tt_spec dataframe, return the station list as a list of strings"""
    stations_df = tt_spec.iloc[1:, 0]
    stations_list_raw = stations_df.to_list()
    stations_list_strings = [str(i) for i in stations_list_raw]
    stations_list = [i.strip() for i in stations_list_strings if i.strip() != ""]
    return stations_list


def train_specs_list_from_tt_spec(tt_spec):
    """Given a tt_spec dataframe, return the trains list as a list of strings"""
    train_specs_df = tt_spec.iloc[0, 1:]
    train_specs_list_raw = train_specs_df.to_list()
    train_specs_list = [str(i).strip() for i in train_specs_list_raw]
    return train_specs_list


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
        return s

    if str(tt_spec.iloc[1, 0]).lower() not in ["column-options", "column_options"]:
        column_count = tt_spec.shape[1]
        # What, there weren't any?  Make a list containing blank lists:
        column_options = [[]] * column_count
        return column_options
    # Now for the main version
    column_options_df = tt_spec.iloc[1, 0:]  # second row, all of it
    column_options_raw_list = column_options_df.to_list()
    column_options_clean_list = [nan_to_blank(s) for s in column_options_raw_list]
    column_options_nested_list = [str(i).split() for i in column_options_clean_list]
    debug_print(1, column_options_nested_list)
    return column_options_nested_list


def get_cell_codes(code_text: str, train_specs: list[str]) -> dict[str, str]:
    """
    Given special code text in a cell, decipher it

    The code leads with a train_spec (train number or train number + day of week), followed by a space,
    followed by one or more of the following (space-separated):
    "first" (first station for train, show departure only)
    "last" (last station for train, show arrival only)

    It really makes no sense to specify both.
    Specifying neither may give strange results, though it is supported.

    OR, if the code is "blank", return that information.

    Returns None if there was no code in the cell (the usual case)

    Otherwise returns a dict:
    train_spec: the train_spec
    first: True or False
    last: True or False
    blank: True or False
    """
    if code_text == "" or pd.isna(code_text):
        return None

    code_text = code_text.strip()
    if code_text == "blank":
        return {"blank": True}

    if code_text.endswith("last"):
        train_spec = code_text.removesuffix("last").strip()
        if train_spec not in train_specs:
            return None
        return {"train_spec": train_spec, "last": True, "first": False, "blank": False}

    if code_text.endswith("first"):
        train_spec = code_text.removesuffix("first").strip()
        if train_spec not in train_specs:
            return None
        return {"train_spec": train_spec, "first": True, "last": False, "blank": False}

    train_spec = code_text
    if train_spec not in train_specs:
        return None
    return {"train_spec": train_spec, "first": False, "last": False, "blank": False}


def split_trains_spec(trains_spec):
    """
    Given a string like "59 / 174 / 22", return a structured list:

    [["59, "174", "22"], True]

    Used to separate specs for multiple trains in the same timetable column.
    A single "59" will simply give {"59"}.

    This also processes specs like "59 monday".
    These require exact spacing; this routine should probably clean up the spacing, but does not.

    """
    # Remove leading whitespace and possible leading minus sign
    clean_trains_spec = trains_spec.lstrip()

    raw_list = clean_trains_spec.split("/")
    clean_list = [item.strip() for item in raw_list]  # remove whitespace again
    return clean_list


def flatten_train_specs_list(train_specs_list):
    """
    Take a nested list of trains and make a flat list of trains.

    Take a list of trains as specified in a tt_spec such as [NaN,'174 monday','178/21','stations','23/1482']
    and make a flat list of all trains involved ['174 monday','178','21','23','1482']
    without the special keywords like "station".

    Leaves the '91 monday' type entries.
    """
    flattened_ts_list = []
    for ts in train_specs_list:
        train_specs = split_trains_spec(ts)  # Separates at the "/"
        flattened_ts_list = [*flattened_ts_list, *train_specs]
    flattened_ts_set = set(flattened_ts_list)
    flattened_ts_set = flattened_ts_set - special_column_names
    return flattened_ts_set


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


def get_timepoint_from_trip_id(feed, trip_id, station_code):
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
    timepoint_df = feed.stop_times[
        (feed.stop_times["trip_id"] == trip_id)
        & (feed.stop_times["stop_id"] == station_code)
    ]
    if timepoint_df.shape[0] == 0:
        return None
    if timepoint_df.shape[0] > 1:
        # This is a bail-out error, it can afford to be slow:
        # Note: the train number lookup only works if the feed is limited to one day,
        # thus making the reverse lookup unique.
        # It will throw an error otherwise.
        trip_id_to_tsn_dict = make_trip_id_to_tsn_dict(feed)
        tsn = trip_id_to_tsn_dict[trip_id]
        raise TwoStopsError(
            " ".join(
                [
                    "Train number",
                    tsn,
                    "with trip id",
                    trip_id,
                    "stops at station code",
                    station_code,
                    "more than once",
                ]
            )
        )
    timepoint = timepoint_df.iloc[0]  # Pull out the one remaining row
    return timepoint


def get_dwell_secs(today_feed, trip_id, station_code):
    """
    Gets dwell time in seconds for a specific trip_id at a specific station

    today_feed: a feed
    trip_id: relevant trip_id
    station_code: station code

    Used primarily to determine whether to put both arrival and departure times
    in the timetable for this station.
    """
    timepoint = get_timepoint_from_trip_id(today_feed, trip_id, station_code)

    if timepoint is None:
        # If the train doesn't stop there, the dwell time is zero;
        # and we need thie behavior for make_stations_max_dwell_map
        return 0

    # There's a catch!  If this station is "discharge only" or "receive only",
    # it effectively has no official dwell time, and should not get two lines
    if timepoint.drop_off_type == 1 or timepoint.pickup_type == 1:
        return 0

    # Normal case:
    departure_secs = gk.timestr_to_seconds(timepoint.departure_time)
    arrival_secs = gk.timestr_to_seconds(timepoint.arrival_time)
    dwell_secs = departure_secs - arrival_secs
    return dwell_secs


def make_stations_max_dwell_map(
    today_feed, tt_spec, dwell_secs_cutoff, trip_from_train_spec_fn
):
    """
    Return a dict from station_code to True/False, based on the trains in the tt_spec.

    This is used to decide whether a station should get a "double line" or "single line" format in the timetable.

    today_feed: a feed filtered to a single date (so tsns are unique)
    tt_spec: the tt_spec
    dwell_secs_cutoff: below this, we don't bother to list arrival and departure times both
    trip_from_train_spec_fn: a function which maps train_spec to trip_id and provides error raising

    Expects a feed already filtered to a single date.
    The feed *may* be restricted to the relevant trains (but must contain all relevant trains).

    First we extract the list of stations and the list of train names from the tt_spec.

    If any train in tsns has a dwell time of dwell_secs or longer at a station,
    then the dict returns True for that station_code; otherwise False.
    """
    # First get stations and trains list from tt_spec.
    stations_list = stations_list_from_tt_spec(tt_spec)
    train_specs_list = train_specs_list_from_tt_spec(tt_spec)
    # Note train_specs_list still contains "/" items
    flattened_train_spec_set = flatten_train_specs_list(train_specs_list)
    # Note that "91 monday" is a perfectly valid spec here

    # Prepare the dict to return
    stations_dict = {}
    for station_code in stations_list:
        max_dwell_secs = 0
        for train_spec in flattened_train_spec_set:
            debug_print(3, "debug dwell map:", train_spec, station_code)
            trip_id = trip_from_train_spec_fn(train_spec).trip_id
            max_dwell_secs = max(
                max_dwell_secs, get_dwell_secs(today_feed, trip_id, station_code)
            )
        if max_dwell_secs >= dwell_secs_cutoff:
            stations_dict[station_code] = True
        else:
            stations_dict[station_code] = False
    return stations_dict


def raise_error_if_not_one_row(trips):
    """
    Given a PANDAS DataFrame, raise an error if it has either 0 or more than 1 rows.

    The error text is based on the assumption that this is a GTFS trips frame.
    This returns nothing if successful; it is solely sanity-check code.

    For speed we have to work with trips directly rather than modifying the feed,
    which is why this is needed for fill_tt_spec, rather than merely in feed_enhanced.
    """
    num_rows = trips.shape[0]
    if num_rows == 0:
        raise NoTripError(
            "Expected single trip: no trips in filtered trips table", trips
        )
    if num_rows > 1:
        print(trips)
        raise TwoTripsError(
            "Expected single trip: too many trips in filtered trips table", trips
        )
    return


def fill_tt_spec(
    tt_spec,
    *,
    today_feed,
    reference_date,
    doing_html=False,
    box_time_characters=False,
    doing_multiline_text=True,
    train_numbers_side_by_side=False,
    is_major_station="standard",
    is_ardp_station="dwell",
    dwell_secs_cutoff=300,
):
    """
    Fill a timetable from a tt-spec template using GTFS data

    The tt-spec must be complete (run augment_tt_spec first)
    today_feed: GTFS feed to work with.  Mandatory.
        This should be filtered to a single representative date.  This is not checked.
        This *may* be filtered to relevant trains only.  It must contain all relevant trains.
    reference_date: Reference date to get timetable for.  Also used for Arizona timezone conversion.

    doing_html: Produce HTML timetable.  Default is false (produce plaintext timetable).
    box_time_characters: Box every character in the time in an HTML box to make them line up.
        For use with fonts which don't have tabular nums.
        Default is False.  Avoid if possible; fragile.
    doing_multiline_text: Produce multiline text in cells.  Ignored if doing_html.
        Default is True.
        If False, stick with single-line text (and never print arrival times FIXME)
    train_numbers_side_by_side: For column headers for a column with multiple trains, put train numbers side by side.
        Default is to stack them top to bottom.
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
    # We have a filtered feed.  We're going to have to map from tsns to trip_ids, repeatedly.
    # This was the single slowest step in earlier versions of the code, using nearly all the runtime.
    # So we generate a dict for it.
    tsn_to_trip_id = make_tsn_to_trip_id_dict(today_feed)
    # Because of the problem of "same tsn, different day", we have to add the "91 monday" indices.
    tsn_and_day_to_trip_id = make_tsn_and_day_to_trip_id_dict(today_feed)
    # Merger of both dictionaries:
    train_spec_to_trip_id = tsn_and_day_to_trip_id | tsn_to_trip_id

    # Create an inner function to get the trip from the tsn, using the dict we just made
    # Also depends on the today_feed
    def trip_from_train_spec_local(train_spec: str):
        try:
            my_trip_id = train_spec_to_trip_id[train_spec]
        except KeyError as e:
            raise InputError("No trip_id for ", train_spec) from e
        my_trips = today_feed.trips[today_feed.trips.trip_id == my_trip_id]
        raise_error_if_not_one_row(my_trips)
        my_trip = my_trips.iloc[0]
        return my_trip

    # Now, we need to determine whether the tsn is a bus.  This is actually in GTFS.
    # However, it has to be looked up by trip_id, so this needs to use the local version
    # of trip_from_train_spec_local, *and* should use the local reduced feed, so it has to be
    # subordinate to this particular run of the timetable generator!
    # So create another inner function to pull the line from the route table.
    def route_from_train_spec_local(train_spec: str):
        my_trip = trip_from_train_spec_local(train_spec)
        my_routes = today_feed.routes[today_feed.routes.route_id == my_trip.route_id]
        if my_routes.shape[0] == 0:
            raise GTFSError("Missing route_id for train_spec", train_spec)
        my_route = my_routes.iloc[0]
        return my_route

    # Extract a list of column options, if provided in the spec
    # This must be in the second row (row 1) and first column (column 0)
    # It ends up as a list (indexed by column number) of lists of options.
    column_options = get_column_options(tt_spec)
    if str(tt_spec.iloc[1, 0]).lower() in ["column-options", "column_options"]:
        # Delete the problem line before further work.
        # This drops by index and not by actual row number, irritatingly
        # Thankfully they're currently the same
        tt_spec = tt_spec.drop(1, axis="index")

    # Load variable function for station name printing
    prettyprint_station_name = None
    if doing_html:
        prettyprint_station_name = amtrak_station_name_to_html
    elif doing_multiline_text:
        prettyprint_station_name = amtrak_station_name_to_multiline_text
    else:
        prettyprint_station_name = amtrak_station_name_to_single_line_text
    if not callable(prettyprint_station_name):
        raise TypeError(
            "Received prettyprint_station_name which is not callable: ",
            prettyprint_station_name,
        )

    # Load variable functions for is_ardp_station and is_major_station
    match is_major_station:
        case False:
            is_major_station = lambda station_code: False
        case "standard":
            is_major_station = amtrak.special_data.is_standard_major_station
    if not callable(is_major_station):
        raise TypeError(
            "Received is_major_station which is not callable: ", is_major_station
        )

    match is_ardp_station:
        case False:
            is_ardp_station = lambda station_code: False
        case True:
            is_ardp_station = lambda station_code: True
        case "dwell":
            # Prep max dwell map.  This is the second-slowest part of the program.
            stations_max_dwell_map = make_stations_max_dwell_map(
                today_feed=today_feed,
                tt_spec=tt_spec,
                dwell_secs_cutoff=dwell_secs_cutoff,
                trip_from_train_spec_fn=trip_from_train_spec_local,
            )
            is_ardp_station = lambda station_code: stations_max_dwell_map[station_code]
            debug_print(1, "Dwell map prepared.")
    if not callable(is_ardp_station):
        raise TypeError(
            "Received is_ardp_station which is not callable: ", is_ardp_station
        )

    # We used to do deep copies here.  Really we just want to copy the STRUCTURE.
    # tt = tt_spec.copy()  # "deep" copy
    [row_index, column_index] = tt_spec.axes
    tt = pd.DataFrame(
        index=row_index.copy(deep=True), columns=column_index.copy(deep=True)
    )
    # styler_t = tt_spec.copy()  # another "deep" copy, parallel
    styler_t = pd.DataFrame(
        index=row_index.copy(deep=True), columns=column_index.copy(deep=True)
    )
    debug_print(1, "Copied tt-spec.")

    # Go through the columns to get an ardp columns map -- cleaner than current implementation
    # FIXME.

    # Base CSS for every data cell.  We probably shouldn't do this but it tests that the styler works.
    base_cell_css = ""

    # NOTE, border variations not implemented yet FIXME
    # borders_final_css="border-bottom-heavy"
    # borders_initial_css="border-top-heavy"
    # Have to add "initial" and "final" with heavy borders

    # Pick out the agency timezone.  Although theoretically each agency has its own timezone,
    # The dataset is not allowed by GTFS to have multiple agency timezones,
    # so the feed is sufficient to specity the agency timezone
    any_agency_row = today_feed.agency.iloc[0]
    agency_tz = any_agency_row.agency_timezone
    debug_print(1, "Agency time zone", agency_tz)

    # Now for the main routine, which is a giant double loop, and therefore quite slow.
    [row_count, column_count] = tt_spec.shape

    header_replacement_list = []  # list, will fill in as we go
    header_styling_list = []  # list, to match column numbers.  Will fill in as we go
    for x in range(1, column_count):  # First (0) column is the station code
        column_key_str = str(tt_spec.iloc[0, x]).strip()  # row 0, column x
        # Create blank train_specs list so we can call get_cell_codes on a special column without crashing
        train_specs = []

        column_header_styling = ""  # default
        match column_key_str.lower():
            case "station" | "stations":
                column_header = text_presentation.get_station_column_header(
                    doing_html=doing_html
                )
            case "services":
                column_header = text_presentation.get_services_column_header(
                    doing_html=doing_html
                )  # in a span
            case "access":
                column_header = text_presentation.get_access_column_header(
                    doing_html=doing_html
                )  # in a span
            case "timezone":
                column_header = text_presentation.get_timezone_column_header(
                    doing_html=doing_html
                )  # in a span
            case _:
                # it's actually a train, or several trains
                # Check column options for reverse, days, ardp:
                reverse = "reverse" in column_options[x]
                use_daystring = "days" in column_options[x]
                long_days_box = "long-days-box" in column_options[x]
                short_days_box = "short-days-box" in column_options[x]
                this_column_gets_ardp = "ardp" in column_options[x]

                # Separate train numbers by "/", and create the train_spec list
                train_specs = split_trains_spec(column_key_str)
                column_header = text_presentation.get_time_column_header(
                    train_specs,
                    route_from_train_spec_local,
                    doing_html=doing_html,
                    train_numbers_side_by_side=train_numbers_side_by_side,
                )
                if doing_html:
                    # Style the header with the color & stylings for the first tsn.
                    # ...because I don't know how to do multiples! FIXME
                    column_header_styling = get_time_column_stylings(
                        train_specs[0],
                        route_from_train_spec_local,
                        output_type="attributes",
                    )
        # Now fill in the column header, as chosen earlier
        header_replacement_list.append(column_header)
        header_styling_list.append(column_header_styling)

        for y in range(1, row_count):  # First (0) row is the header
            station_code = tt_spec.iloc[y, 0]  # row y, column 0
            # NaNs are notoriously hard to match, so convert them.
            if pd.isna(station_code):
                station_code = ""

            # Also convert NaNs to empty string in individual cells.
            if pd.isna(tt_spec.iloc[y, x]):
                tt_spec.iloc[y, x] = ""

            # Reset the styler string:
            cell_css_list = [base_cell_css]
            # Check for cell_codes like "28 last".  This *usually* returns None.
            cell_codes = get_cell_codes(tt_spec.iloc[y, x], train_specs)
            if cell_codes and cell_codes["blank"]:
                # This is a longhand for passing through a blank space.
                # Makes it easier to read the source file.
                tt_spec.iloc[y, x] = " "
                cell_codes = None

            # This is effectively matching row, column, cell contents in spec
            match [station_code.lower(), column_key_str.lower(), tt_spec.iloc[y, x]]:
                case ["", _, ""]:
                    # Make sure blanks become *string* blanks in this line.
                    tt.iloc[y, x] = ""
                case ["", _, raw_text]:
                    # This is probably special text like "to Chicago".
                    cell_css_list.append("special-cell")
                    # Copy the handwritten text over.
                    tt.iloc[y, x] = raw_text
                case ["route-name", ck, _] if ck in special_column_names:
                    cell_css_list.append("route-name-cell")
                    tt.iloc[y, x] = ""
                case ["route-name", _, _]:
                    # Line for route names.
                    cell_css_list.append("route-name-cell")
                    route_names = []
                    styled_route_names = []
                    for train_spec in train_specs:
                        my_trip = trip_from_train_spec_local(train_spec)
                        route_id = my_trip.route_id
                        # Clean this interface up later.  For now highly Amtrak-specific FIXME
                        route_name = amtrak.get_route_name(today_feed, route_id)
                        styled_route_name = (
                            text_presentation.style_route_name_for_column(
                                route_name, doing_html=doing_html
                            )
                        )
                        if not route_names or route_names[-1] != route_name:
                            # Don't duplicate if same route as previous train in slashed list
                            route_names.append(route_name)
                            styled_route_names.append(styled_route_name)
                    if doing_html:
                        separator = "<hr>"
                    else:
                        separator = "\n"
                    full_styled_route_names = separator.join(styled_route_names)
                    tt.iloc[y, x] = full_styled_route_names
                    cell_css_list.append(
                        get_time_column_stylings(
                            train_specs[0],
                            route_from_train_spec_local,
                            output_type="class",
                        )
                    )
                case ["updown", ck, _] if ck in special_column_names:
                    cell_css_list.append("updown-cell")
                    tt.iloc[y, x] = ""
                case ["updown", _, _]:
                    # Special line just to say "Read Up" or "Read Down"
                    cell_css_list.append("updown-cell")
                    tt.iloc[y, x] = text_presentation.style_updown(
                        reverse, doing_html=doing_html
                    )
                case ["days" | "days-of-week", ck, _] if ck in special_column_names:
                    cell_css_list.append("days-of-week-cell")
                    tt.iloc[y, x] = ""
                case ["days" | "days-of-week", _, ""]:
                    cell_css_list.append("days-of-week-cell")
                    # No reference stop?  Maybe this should be blank.
                    # Useful if one train runs across midnight.
                    tt.iloc[y, x] = ""
                    # Color this cell
                    # FIXME, currently using color from first tsn only
                    cell_css_list.append(
                        get_time_column_stylings(
                            train_specs[0],
                            route_from_train_spec_local,
                            output_type="class",
                        )
                    )
                case ["days" | "days-of-week", _, reference_stop_id]:
                    # Days of week -- best for a train which doesn't run across midnight
                    cell_css_list.append("days-of-week-cell")
                    # We can only show the days for one station.
                    # So get the reference stop_id / station code to use; user-specified
                    if len(train_specs) > 1:
                        raise InputError(
                            "Can't have a days header for a column with two or more trains"
                        )
                    my_trip = trip_from_train_spec_local(train_specs[0])
                    timepoint = get_timepoint_from_trip_id(
                        today_feed, my_trip.trip_id, reference_stop_id
                    )
                    # Pull out the timezone for the reference_stop_id (should precache as dict, TODO)
                    stop_df = today_feed.stops[
                        today_feed.stops.stop_id == reference_stop_id
                    ]
                    stop_tz = stop_df.iloc[0].stop_timezone
                    zonediff = text_presentation.get_zonediff(
                        stop_tz, agency_tz, reference_date
                    )
                    # Get the day change for the reference stop (format is explained in text_presentation)
                    departure = text_presentation.explode_timestr(
                        timepoint.departure_time, zonediff
                    )
                    offset = departure.day
                    # Finally, get the calendar (must be unique)
                    calendar = today_feed.calendar[
                        today_feed.calendar.service_id == my_trip.service_id
                    ]
                    # And fill in the actual string
                    daystring = text_presentation.day_string(calendar, offset=offset)
                    # TODO: add some HTML styling here
                    tt.iloc[y, x] = daystring
                    # Color this cell
                    # FIXME, currently using color from first tsn only
                    cell_css_list.append(
                        get_time_column_stylings(
                            train_specs[0],
                            route_from_train_spec_local,
                            output_type="class",
                        )
                    )
                case [_, _, raw_text] if raw_text != "" and not cell_codes:
                    # Line led by a station code, but cell already has a value.
                    # and the value isn't one of the special codes we check later.
                    cell_css_list.append("special-cell")
                    # This is probably special text like "to Chicago".
                    # Copy the handwritten text over.
                    tt.iloc[y, x] = raw_text
                case [_, "station" | "stations", _]:
                    # Line led by a station code, column for station names
                    cell_css_list.append("station-cell")
                    station_name_raw = amtrak.get_station_name(station_code)
                    major = amtrak.special_data.is_standard_major_station(station_code)
                    station_name_str = prettyprint_station_name(station_name_raw, major)
                    tt.iloc[y, x] = station_name_str
                case [_, "services", _]:
                    # Column for station services codes.  Currently completely vacant.
                    cell_css_list.append("services-cell")
                    services_str = ""
                    tt.iloc[y, x] = services_str
                case [_, "access", _]:
                    cell_css_list.append("access-cell")
                    access_str = ""
                    # Currently Amtrak-specific.
                    if amtrak.station_has_accessible_platform(station_code):
                        access_str += icons.get_accessible_icon_html()
                    elif amtrak.station_has_inaccessible_platform(station_code):
                        access_str += icons.get_inaccessible_icon_html()
                    tt.iloc[y, x] = access_str
                case [_, "timezone", _]:
                    # Pick out the stop timezone -- TODO, precache this as a dict
                    stop_df = today_feed.stops[today_feed.stops.stop_id == station_code]
                    stop_tz = stop_df.iloc[0].stop_timezone
                    cell_css_list.append("timezone-cell")
                    tt.iloc[y, x] = text_presentation.get_zone_str(
                        stop_tz, doing_html=doing_html
                    )
                case [_, _, _]:
                    # Line led by station code, column led by train numbers,
                    # cell empty or has a "cell code": the normal case -- we need to fill in a time.

                    # For a slashed train spec ( 549 / 768 ) pull the *first* train's times,
                    # then the second train's times *if the first train doesn't stop there*

                    # For connecting trains, use two different rows and use cell codes.

                    # Pick out the stop timezone -- TODO, precache this as a dict
                    stop_df = today_feed.stops[today_feed.stops.stop_id == station_code]
                    stop_tz = stop_df.iloc[0].stop_timezone

                    debug_print(
                        3,
                        "Trainspecs: " + str(train_specs) + "; Station:" + station_code,
                    )

                    # Extract my_trip, timepoint (and later calendar)
                    # Note that in Python variables defined in a loop "hang around"

                    if cell_codes:
                        # Specific train_spec was requested.
                        debug_print(2, "cell codes found")
                        train_specs_to_check = [cell_codes["train_spec"]]
                    else:
                        train_specs_to_check = train_specs

                    for train_spec in train_specs_to_check:
                        my_trip = trip_from_train_spec_local(train_spec)
                        debug_print(2, "debug trip_id:", train_spec, my_trip.trip_id)
                        timepoint = get_timepoint_from_trip_id(
                            today_feed, my_trip.trip_id, station_code
                        )
                        if timepoint is not None:
                            # Use the FIRST one which returns a timepoint
                            break

                    if timepoint is None:
                        # This train does not stop at this station
                        # Blank cell -- need to be cleverer about this FIXME
                        # Only assign the stylings if the train hasn't ended.  Tricky!  Dunno how to do it!
                        # Probably requires that earlier pass through the table.  Or CELL CODES FIXME
                        tt.iloc[y, x] = ""
                        cell_css_list.append("blank-cell")
                        # Confusing: we want to style some of these and not others.  FIXME.
                        # For now, we style if we have a single train.
                        # Otherwise not, because it's hard to know what color to use.
                        if len(train_specs) == 1:
                            cell_css_list.append(
                                get_time_column_stylings(
                                    train_specs[0],
                                    route_from_train_spec_local,
                                    output_type="class",
                                )
                            )
                    else:
                        # MAIN ROUTINE FOR PUTTING A TIME IN A CELL
                        # We have a station code, and a specific tsn
                        cell_css_list.append("time-cell")
                        cell_css_list.append(
                            get_time_column_stylings(
                                train_spec,
                                route_from_train_spec_local,
                                output_type="class",
                            )
                        )

                        calendar = None  # if not use_daystring, save time
                        if use_daystring:
                            calendar = today_feed.calendar[
                                today_feed.calendar.service_id == my_trip.service_id
                            ]

                        has_baggage = bool(
                            amtrak.train_has_checked_baggage(
                                train_spec_to_tsn(train_spec)
                            )
                            and amtrak.station_has_checked_baggage(station_code)
                        )

                        # Normally we are two_row if the station calls for it,
                        # but (hackishly) we allow the cell_codes to override it.
                        # This isn't quite right as it should be station specific.
                        two_row = is_ardp_station(station_code)

                        # MUST figure first_stop and last_stop
                        # ...which means we need to make earlier passes through the table FIXME
                        # But for now we can handle it with manual annotation in the spec
                        is_first_stop = False
                        is_last_stop = False
                        if cell_codes:
                            is_first_stop = cell_codes["first"]
                            is_last_stop = cell_codes["last"]
                            if is_first_stop or is_last_stop:
                                two_row = False

                        cell_text = text_presentation.timepoint_str(
                            timepoint,
                            stop_tz=stop_tz,
                            agency_tz=agency_tz,
                            reference_date=reference_date,
                            doing_html=doing_html,
                            box_time_characters=box_time_characters,
                            reverse=reverse,
                            two_row=two_row,
                            use_ar_dp_str=this_column_gets_ardp,
                            use_daystring=use_daystring,
                            calendar=calendar,
                            long_days_box=long_days_box,
                            short_days_box=short_days_box,
                            is_first_stop=is_first_stop,
                            is_last_stop=is_last_stop,
                            use_baggage_str=amtrak.train_has_checked_baggage(
                                train_spec_to_tsn(train_spec)
                            ),
                            has_baggage=has_baggage,
                        )
                        tt.iloc[y, x] = cell_text
            # Fill the styler.  We MUST overwrite every single cell of the styler.
            styler_t.iloc[y, x] = " ".join(cell_css_list)

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


def produce_timetable(
    *,
    do_csv,
    do_html,
    do_pdf,
    do_jpg,
    master_feed,
    author,
    command_line_reference_date,
    input_dirname,
    spec_file,
    output_dirname,
):
    """
    Produce a single timetable HTML file.  Assumes setup has been done.

    Intended to allow multiple timetables to be processed at once.
    do_csv: produce a CSV timetable
    do_html: produce an HTML timetable
    do_pdf: produce a PDF timetable
    master_feed: initialized master GTFS feed
    author: author name
    command_line_reference_date: reference date passed at command line, might be None
    input_dirname: find the spec_name.csv and spec_name.json files here
    spec_file: root of filename for the .csv and .json files specifying the timetable
    output_dirname: Put the output timetables here
    """
    # Accept the spec name with or without a suffix, for convenience
    spec_filename_base = spec_file.removesuffix(".csv").removesuffix(".json")
    ttspec_csv_filename = spec_filename_base + ".csv"
    ttspec_json_filename = spec_filename_base + ".json"

    if input_dirname:
        input_dir = Path(input_dirname)
        ttspec_csv_path = input_dir / ttspec_csv_filename
        ttspec_json_path = input_dir / ttspec_json_filename
    else:
        # Might be None, if it wasn't passed at the command line
        ttspec_csv_path = ttspec_csv_filename
        ttspec_json_path = ttspec_json_filename
    debug_print(
        1, "ttspec_csv_path", ttspec_csv_path, "/ ttspec_json_path", ttspec_json_path
    )

    # Load the .tt-aux file first, as it determines high-level stuff
    aux = load_ttspec_json(ttspec_json_path)

    if output_dirname:
        output_dir = Path(output_dirname)
    else:
        output_dir = Path(".")

    if "output_subdir" in aux:
        output_subdir = aux["output_subdir"]
        output_dir = output_dir / output_subdir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    if "output_filename" in aux:
        # The aux file may specify the output filename
        output_filename_base = aux["output_filename"]
    else:
        # Or, make it the same as the input filename
        output_filename_base = spec_filename_base

    if "for_rpa" in aux:
        for_rpa = aux["for_rpa"]
    else:
        for_rpa = False

    if "train_numbers_side_by_side" in aux:
        train_numbers_side_by_side = aux["train_numbers_side_by_side"]
    else:
        train_numbers_side_by_side = False

    # Copy the icons and fonts to the output dir.
    # This is memoized so it won't duplicate work if you do multiple tables.
    copy_supporting_files_to_output_dir(output_dir, for_rpa)

    if command_line_reference_date:
        reference_date = str(command_line_reference_date)
    elif "reference_date" in aux:
        # We're currently converting GTFS dates to ints; FIXME
        reference_date = str(aux["reference_date"])
    else:
        raise InputError("No reference date in .tt-aux or at command line!")
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")

    if "programmers_warning" in aux:
        print("WARNING: ", aux["programmers_warning"])

    # Now we're ready to load the .tt-spec file, finally
    tt_spec_raw = load_ttspec_csv(ttspec_csv_path)
    tt_spec = augment_tt_spec(tt_spec_raw, feed=master_feed, date=reference_date)
    debug_print(1, "tt-spec", spec_filename_base, "loaded and augmented")

    # Filter the feed to the relevant day.  Required.
    today_feed = master_feed.filter_by_dates(reference_date, reference_date)
    debug_print(1, "Feed filtered by reference date.")

    # Reduce the feed, by eliminating stuff from other trains.
    # By reducing the stop_times table to be much smaller,
    # this hopefully makes each subsequent search for a timepoint faster.
    # This cuts a testcase runtime from 23 seconds to 20.
    train_specs_list = train_specs_list_from_tt_spec(
        tt_spec
    )  # Note still contains "/" items
    flattened_train_specs_set = flatten_train_specs_list(train_specs_list)

    # Note still contains "91 monday" and similar specs: remove the day suffixes here
    flattened_tsn_list = [
        train_spec_to_tsn(train_spec) for train_spec in flattened_train_specs_set
    ]

    reduced_feed = today_feed.filter_by_trip_short_names(flattened_tsn_list)
    debug_print(1, "Feed filtered by trip_short_name.")

    # Uniqueness sanity check -- check for two rows in reduced_feed.trips with the same tsn.
    # This will make it impossible to map from tsn to trip_id.
    # HOWEVER, Amtrak has some weird duplicates with duplicate trip_ids and identical timings,
    # so this might not be a fatal error.
    if find_tsn_dupes(reduced_feed):
        debug_print(
            1,
            "Warning, tsn duplicates!  Random trip will be picked!  Usually a bad idea!",
        )

    # Print the calendar for debugging
    debug_print(1, "Calendar:")
    debug_print(1, reduced_feed.calendar)

    # Debugging for the reduced feed.  Seems to be fine.
    # with open( Path("./dump-stop-times.csv"),'w') as outfile:
    #    print(reduced_feed.stop_times.to_csv(index=False), file=outfile)

    # Collect pairs of validity dates.
    # Note that the feed has been filtered by train_specs,
    # so will *only* include relevant train_specs in the calendar!
    start_dates = reduced_feed.calendar["start_date"]
    latest_start_date = start_dates.max()
    end_dates = reduced_feed.calendar["end_date"]
    earliest_end_date = end_dates.min()

    debug_print(1, "Believed valid from", latest_start_date, "to", earliest_end_date)

    # This will eventually get used, but for now just emit it as a debug message

    # Note that due to the inline images issue we may need to run
    # a completely separate HTML version for weasyprint.  We avoid this so far.
    # TODO
    # Consider using the SpartanTT font to handle this.  We can make the font
    # quasi-legit for screen readers by using correct Unicode code points.

    if do_csv:
        # Note that there is a real danger of overwriting the source file.
        # Avoid this by adding an extra suffix to the timetable name.
        (timetable, styler_table, header_styling) = fill_tt_spec(
            tt_spec,
            today_feed=reduced_feed,
            reference_date=reference_date,
            is_major_station=amtrak.special_data.is_standard_major_station,
            is_ardp_station="dwell",
        )
        # NOTE, need to add the header
        path_for_csv = output_dir / Path(output_filename_base + "-out.csv")
        timetable.to_csv(path_for_csv, index=False, header=True)
        debug_print(1, "CSV output done")

    if do_jpg:
        do_pdf = True
    if do_pdf:
        do_html = True

    if do_html:
        # Main timetable, same for HTML and PDF
        (timetable, styler_table, header_styling_list) = fill_tt_spec(
            tt_spec,
            today_feed=reduced_feed,
            reference_date=reference_date,
            is_major_station=amtrak.special_data.is_standard_major_station,
            is_ardp_station="dwell",
            doing_html=True,
            box_time_characters=False,
            train_numbers_side_by_side=train_numbers_side_by_side,
        )
        timetable_styled_html = style_timetable_for_html(timetable, styler_table)
        debug_print(1, "HTML styled")

        # Produce the final complete page...
        timetable_finished_html = finish_html_timetable(
            timetable_styled_html,
            header_styling_list,
            author=author,
            aux=aux,
            box_time_characters=False,
            start_date=str(latest_start_date),
            end_date=str(earliest_end_date),
        )
        path_for_html = output_dir / Path(output_filename_base + ".html")
        with open(path_for_html, "w") as outfile:
            print(timetable_finished_html, file=outfile)
        debug_print(1, "Finished HTML done")

    if do_pdf:
        # Pick up already-created HTML, convert to PDF
        weasy_html_pathname = str(path_for_html)
        html_for_weasy = weasyHTML(filename=weasy_html_pathname)
        path_for_weasy = output_dir / Path(output_filename_base + ".pdf")
        html_for_weasy.write_pdf(path_for_weasy)
        debug_print(1, "Weasy done")

    if do_jpg:
        # Convert PDF to JPG
        path_for_jpg = output_dir / Path(output_filename_base + ".jpg")
        vips_command = "".join(
            ["vips copy ", str(path_for_weasy), "[dpi=300] ", str(path_for_jpg)]
        )
        os.system(vips_command)


# This is a module-level global
prepared_output_dirs = []
prepared_output_dirs_for_rpa = []


def copy_supporting_files_to_output_dir(output_dirname, for_rpa=False):
    """
    Copy supporting files (icons, fonts) to the output directory.

    Necessary for Weasyprint, and for the HTML to display right.
    """
    # Copy the image files to the destination directory.
    # Necessary for weasyprint to work right!

    output_dir = Path(output_dirname)

    # Note!  If we do multiple timetables with output_subdir,
    # we would like to save trouble by caching the fact that we've done it.
    # for_rpa adds an extra file (a superset of the other version)
    global prepared_output_dirs_for_rpa
    global prepared_output_dirs
    if str(output_dir) in prepared_output_dirs_for_rpa:
        return
    if not for_rpa and str(output_dir) in prepared_output_dirs:
        return

    source_dir = Path(__file__).parent

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.samefile(source_dir, output_dir):
        debug_print(1, "Working in module directory, not copying fonts and icons")
        return

    icons_dir = output_dir / "icons"
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    icon_filenames = ["accessible.svg", "inaccessible-ncn.svg", "baggage-ncn.svg"]
    if for_rpa:
        icon_filenames.append("rpa-logo.svg")
    for icon_filename in icon_filenames:
        icon_file_source_path = source_dir / "icons" / icon_filename
        icon_file_dest_path = icons_dir / icon_filename
        # Note, this overwrites
        shutil.copy2(icon_file_source_path, icon_file_dest_path)

    fonts_dir = output_dir / "fonts"
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    # Each font has its own directory
    font_subdir_names = ["SpartanTT"]
    for font_subdir_name in font_subdir_names:
        font_subdir = fonts_dir / font_subdir_name
        if not os.path.exists(font_subdir):
            os.makedirs(font_subdir)
    # And font files within the directory
    font_filenames = ["SpartanTT/SpartanTT-Bold.ttf", "SpartanTT/SpartanTT-Medium.ttf"]
    for font_filename in font_filenames:
        font_file_source_path = source_dir / "fonts" / font_filename
        font_file_dest_path = fonts_dir / font_filename
        # Note, this overwrites
        shutil.copy2(font_file_source_path, font_file_dest_path)

    debug_print(1, "Fonts and icons copied to", output_dir)
    if for_rpa:
        prepared_output_dirs_for_rpa.append(str(output_dir))
    prepared_output_dirs.append(str(output_dir))
    return


##########################
#### NEW MAIN PROGRAM ####
##########################
if __name__ == "__main__":

    debug_print(3, "Dumping sys.path for clarity:", sys.path)

    my_arg_parser = make_tt_arg_parser()
    args = my_arg_parser.parse_args()

    # Make sure user has provided at least one argument when running program
    # Otherwise, provide help
    if len(sys.argv) <= 1:
        my_arg_parser.print_help()
        sys.exit(1)

    spec_file_list = args.tt_spec_files
    if spec_file_list is None:
        print(
            "You need to specify at least one spec file.  Use the --help option for help."
        )
        my_arg_parser.print_usage()
        sys.exit(1)

    set_debug_level(args.debug)

    output_dirname = args.output_dirname
    if not output_dirname:
        output_dirname = os.getenv("TIMETABLE_KIT_OUTPUT_DIR")
    if not output_dirname:
        output_dirname = "."
    debug_print(1, "Using output_dir", output_dirname)

    input_dirname = args.input_dirname
    if not input_dirname:
        input_dirname = os.getenv("TIMETABLE_KIT_INPUT_DIR")
    debug_print(1, "Using input_dir", input_dirname)

    gtfs_filename = args.gtfs_filename
    master_feed = initialize_feed(gtfs=gtfs_filename)

    # Amtrak-specific patches.  Bleah!  FIXME
    master_feed = amtrak.patch_feed(master_feed)
    debug_print(1, "Feed patched, hopefully")

    author = args.author
    if not author:
        author = os.getenv("TIMETABLE_KIT_AUTHOR")
    if not author:
        author = os.getenv("AUTHOR")
    if not author:
        print("--author is mandatory!")
        sys.exit(1)

    command_line_reference_date = args.reference_date  # Does not default, may be None

    for spec_file in spec_file_list:
        debug_print(1, "Producing timetable for", spec_file)
        produce_timetable(
            do_csv=args.do_csv,
            do_html=args.do_html,
            do_pdf=args.do_pdf,
            do_jpg=args.do_jpg,
            master_feed=master_feed,
            author=author,
            command_line_reference_date=command_line_reference_date,
            input_dirname=input_dirname,
            spec_file=spec_file,
            output_dirname=output_dirname,
        )
        debug_print(1, "Done producing timetable for", spec_file)
    sys.exit(0)
