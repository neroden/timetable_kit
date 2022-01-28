#! /usr/bin/python3
# text_presentation.py
# Part of timetable_kit
# Copyright 2021 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

import pandas as pd
import gtfs_kit as gk
from collections import namedtuple

class DataError(ValueError):
    """Exception for unexpected data in the GTFS feed."""
    pass

def day_string(calendar, offset=0):
    '''Given a calendar DataTable which contains only a single row for a single service, this
    returns a string like "Daily" or "MoWeFr" for the serviced days of the week.
    Use offset to get the string for stops which are more than 24 hours after initial depature.
    '''
    days_of_service_list = calendar.to_dict('records')
    # if there are zero or duplicate service records, we error out.
    if (len(days_of_service_list) == 0):
        raise DataError("daystring() can't handle an empty calendar")
    elif (len(days_of_service_list) >= 2):
        raise DataError("daystring() can't handle two calendars for service_id: ", days_of_service_list)
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
TimeTuple = namedtuple('TimeTuple', ['day', 'pm', 'hour', 'min', 'sec'])
def explode_timestr(timestr: str) -> TimeTuple:
    """
    Given a GTFS timestr, return a namedtuple giving 'day', 'pm', 'hour', 'min', 'sec'
    """
    try:
        longhours, mins, secs = [int(x) for x in timestr.split(":")]
    except:
        raise DataError("Timestr didn't parse right", timestr)
    [days, hours24] = divmod(longhours, 24)
    [pm, hours] = divmod(hours24, 12)
    my_time = TimeTuple(day=days,pm=pm,hour=hours,min=mins,sec=secs)
    # return {'day':days, 'hour':hours, 'min':mins, 'sec':secs} -- dict alternative
    return my_time

# Named constant useful for the next method:
ampm_str = ["A", "P"] # index into this to get the am or pm string
def time_short_str(time: TimeTuple) -> str:
    """
    Given an exploded TimeTuple, give a short version of the time suitable for a timetable.
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

