# text_presentation.py
# Part of timetable_kit
# Copyright 2021 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

import pandas as pd
import gtfs_kit as gk
from collections import namedtuple

# These are mine
from tt_errors import GTFSError

def day_string(calendar, offset=0):
    '''Given a calendar DataTable which contains only a single row for a single service, this
    returns a string like "Daily" or "MoWeFr" for the serviced days of the week.
    Use offset to get the string for stops which are more than 24 hours after initial depature.
    '''
    days_of_service_list = calendar.to_dict('records')
    # if there are zero or duplicate service records, we error out.
    if (len(days_of_service_list) == 0):
        raise GTFSError("daystring() can't handle an empty calendar")
    elif (len(days_of_service_list) >= 2):
        raise GTFSError("daystring() can't handle two calendars for service_id: ", days_of_service_list)
    days_of_service = days_of_service_list[0]

    # print(days_of_service)
    # Fast exit: don't go through all the work if it's daily
    if (days_of_service['sunday'] and
        days_of_service['monday'] and
        days_of_service['tuesday'] and
        days_of_service['wednesday'] and
        days_of_service['thursday'] and
        days_of_service['friday'] and
        days_of_service['saturday'] and
        days_of_service['sunday']
       ):
        return "Daily";

    while (offset > 0):
        # Roll the days of service forward one: train started MoWeFr but it's now TuThSa
        new_monday = days_of_service['sunday']
        days_of_service['sunday'] = days_of_service['saturday']
        days_of_service['saturday'] = days_of_service['friday']
        days_of_service['friday'] = days_of_service['thursday']
        days_of_service['thursday'] = days_of_service['wednesday']
        days_of_service['wednesday'] = days_of_service['tuesday']
        days_of_service['tuesday'] = days_of_service['monday']
        days_of_service['monday'] = new_monday
        offset = offset-1

    daystring = ""
    if (days_of_service['monday']):
        daystring += "Mo"
    if (days_of_service['tuesday']):
        daystring += "Tu"
    if (days_of_service['wednesday']):
        daystring += "We"
    if (days_of_service['thursday']):
        daystring += "Th"
    if (days_of_service['friday']):
        daystring += "Fr"
    if (days_of_service['saturday']):
        daystring += "Sa"
    if (days_of_service['sunday']):
        daystring += "Su"
    if (daystring == "MoTuWeThFrSaSu"):
        daystring = "Daily" #Bypassed by fast path
    if (daystring == "MoTuWeThFr"):
        daystring = "Mo-Fr"
    if (daystring == "MoTuWeTh"):
        daystring = "Mo-Th"
    return daystring

# Timestr functions
TimeTuple = namedtuple('TimeTuple', ['day', 'pm', 'hour', 'hour24', 'min', 'sec'])
def explode_timestr(timestr: str) -> TimeTuple:
    """
    Given a GTFS timestr, return a namedtuple giving 'day', 'pm', 'hour', 'min', 'sec'
    and also 'hour24' for 24-hour time
    """
    try:
        longhours, mins, secs = [int(x) for x in timestr.split(":")]
    except:
        raise GTFSError("Timestr didn't parse right", timestr)
    [days, hours24] = divmod(longhours, 24)
    [pm, hours] = divmod(hours24, 12)
    my_time = TimeTuple(day=days,pm=pm,hour=hours,hour24=hours24,min=mins,sec=secs)
    # could do as dict, but seems cleaner this way
    return my_time

def time_short_str_24(time: TimeTuple) -> str:
    """
    Given an exploded TimeTuple, give a short version of the time suitable for a timetable.
    But do it in "military" format from 0:00 to 23:59.
    """
    # Note that this is very explicitly designed to be fixed width
    time_text = ["{: >2}".format(time.hour24),
                 ":",
                 "{:0>2}".format(time.min)
                ]
    time_str = ''.join(time_text) # No separator!
    return time_str

# Named constant useful for the next method:
ampm_str = ["A", "P"] # index into this to get the am or pm string
def time_short_str(time: TimeTuple) -> str:
    """
    Given an exploded TimeTuple, give a short version of the time suitable for a timetable.
    Do it with AM and PM.
    """
    # Note that this is very explicitly designed to be fixed width
    hour = time.hour
    if (hour == 0) :
        hour = 12
    time_text = ["{: >2}".format(hour),
                 ":",
                 "{:0>2}".format(time.min),
                 ampm_str[time.pm]
                ]
    time_str = ''.join(time_text) # No separator!
    return time_str

def timepoint_str ( timepoint,
                    two_row=False,
                    second_timepoint=None,
                    doing_html=False,
                    bold_pm=True,
                    use_24=False,
                    use_daystring=False,
                    calendar=None,
                    is_first_stop=False,
                    is_last_stop=False,
                   )
    '''
    Produces a text or HTML string for display in a timetable, showing the time of departure, arrival, and extra symbols.
    This is quite complex: I would have used tables-within-tables but they're screen-reader-unfriendly.

    It MUST be printed in a fixed-width font and formatting MUST be preserved: quite ugly work really

    The most excrutiatingly complex variant looks like:
    Ar F 9:59P Daily
    Dp F10:00P WeFrSu

    Mandatory argument:
    -- timepoint: a single row from stop_times.
    Options are many:
    -- two_row: This timepoint gets both arrival and departure rows (default is just one row)
    -- second_timepoint: Used for a very tricky thing with connecting trains to show them in the
        same column at the same station; normally None, specified at that particular station
    -- doing_html: output HTML (default is plaintext)
    -- use_24: use 24-hour military time (default is 12 hour time with "A" and "P" suffix)
    -- bold_pm: make PM times bold (even in 24-hour time; only with doing_html
    -- use_daystring: append a "MoWeFr" or "Daily" string.  Only used on infrequent services.
    -- calendar: a calendar with a single row containing the correct calendar for the service.
           Required if use_daystring is True; pointless otherwise.
    -- is_first_stop: suppress "receive only" notation
    -- is_last_stop: suppress "discharge only" notation
    '''

    if (doing_html):
        linebreak = "<br>"
    else:
        linebreak = "\n"

    # Pick function for the actual time printing
    if (use_24):
        time_str = time_short_str_24
    else:
        time_str = time_short_str

    # Fill the TimeTuple and prep string for actual departure time
    departure = explode_timestr(timepoint.departure_time)
    departure_str = time_str(departure)
    # HTML bold annotation for PM (even in 24-hour case)
    if (departure.pm == 1 and doing_html):
        departure_str = ''.join(["<b>",departure_str,"</b>"])
    if (use_daystring):
        # Note that daystring is VARIABLE LENGTH, and is the only variable-length field
        # It must be last and the entire time field must be left-justified as a result
        departure_daystring = day_string(calendar, offset=departure.day)
        departure_str = ''.join([departure_str," ",departure_daystring])

    # Fill the TimeTuple and prep string for actual time
    arrival = explode_timestr(timepoint.arrival_time)
    arrival_str = time_str(arrival)
    # HTML bold annotation for PM
    if (arrival.pm == 1 and doing_html):
        arrival_str = ''.join(["<b>",arrival_str,"</b>"])
    if (use_daystring):
        arrival_daystring = day_string(calendar, offset=arrival.day)
        arrival_str = ''.join([arrival_str," ",arrival_daystring])

    # Receive-only / Discharge-only annotation
    # Important note: there's currently no way to mark the infamous "L",
    # which means the train or bus is allowed to depart ahead of time
    rd_str = " " # NOTE the default is one blank space, to support fixed width.
    receive_only = False;
    discharge_only = False;
    if (is_first_stop):
        receive_only = True; # Logically speaking... but don't annotate it
    if (is_last_stop):
        discharge_only = True; # Logically speaking... but don't annotate it

    if (timepoint.drop_off_type == 1 and timepoint.pickup_type == 0):
        receive_only = True;
        if (not is_first_stop): # This is obvious at the first station
            rd_str = "R" # Receive passengers only
            if (doing_html):
                rd_str = "<b>R</b>"
    elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 0):
        discharge_only = True;
        if (not is_last_stop): # This is obvious at the last station
            rd_str = "D" # Discharge passengers only
            if (doing_html):
                rd_str = "<b>D</b>"
    elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 1):
        rd_str = "*" # Not for ordinary passengers (staff only, perhaps)
    elif (timepoint.pickup_type >= 2 or timepoint.drop_off_type >= 2):
        rd_str = "F" # Flag stop of some type

    # IMPORTANT NOTE: Amtrak has not implemented this yet.
    # FIXME: request that Alan Burnstine implement this if possible
    # This seems to be the only way to identify the infamous "L",
    # which means that the train or bus is allowed to depart ahead of time
    if ("timepoint" in timepoint):  # The "timepoint" column has been supplied
        print ("timepoint column found") # Should not happen with existing data
        if (timepoint.timepoint = 0): # and it says times aren't exact
            rd_str = "L"

    # WORK IN PROGRESS
    return
