# time.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023, 2024 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Module for processing GTFS times and producing strings.
"""

from typing import NamedTuple  # for TimeTuple

from datetime import datetime, timedelta  # for time zones
from zoneinfo import ZoneInfo  # still for time zones

import pandas as pd  # Used for DataFrame

# These are mine
from timetable_kit.errors import GTFSError
from timetable_kit.debug import debug_print


def gtfs_date_to_isoformat(gtfs_date: str) -> str:
    """Given a GTFS date string, return an ISO format date string.

    This is a triviality: it converts 20220310 to 2022-03-10.
    """
    # Make sure it's a str in case we've been fooling around with these as numbers
    gtfs_date = str(gtfs_date)
    if len(gtfs_date) != 8:
        raise GTFSError("Datestr wrong length", gtfs_date)
    iso_str = "-".join([gtfs_date[:4], gtfs_date[4:6], gtfs_date[6:8]])
    return iso_str


def get_zonediff(local_zone, base_zone, reference_date):
    """Get the hour difference which must be applied to a time in base_zone to get a
    time in local_zone.

    While I hate to reimplement time calculations, GTFS time data is really wacky.
    It may be easiest to hard code this, but this is the "clean" implementation...

    The messiest part is Arizona.  Because of Arizona, which does not observe DST,
    we have to use the right base date, which should be the reference date.
    """
    base = ZoneInfo(base_zone)
    local = ZoneInfo(local_zone)

    # GTFS dates are in YYYYMMDD format, as a string.
    # This can be decrypted in python with the "%Y%m%d" format string.
    dt = datetime.strptime(reference_date, "%Y%m%d")

    diff_timedelta = local.utcoffset(dt) - base.utcoffset(dt)
    one_hour = timedelta(hours=1)
    no_time = timedelta(hours=0)
    [diff_hours, diff_seconds] = divmod(diff_timedelta, one_hour)
    if diff_seconds != no_time:
        raise ValueError(
            "Can't handle timezone diffs which are not multiples of an hour"
        )
    return diff_hours


# This is exceedingly North-America-centric, FIXME
tz_letter_dict = {
    # US zones used by Amtrak:
    "America/New_York": "ET",
    "America/Chicago": "CT",
    "America/Denver": "MT",
    "America/Phoenix": "MST",
    "America/Los_Angeles": "PT",
    # Canadian zones used by VIA (in addition to America/New_York):
    "America/Halifax": "AT",
    "America/Toronto": "ET",
    "America/Winnipeg": "CT",
    "America/Regina": "CST",
    "America/Edmonton": "MT",
    "America/Vancouver": "PT",
}


def get_zone_str(zone_name, doing_html=False):
    """Return a two-letter abbreviation for an IANA time zone, possibly with HTML
    wrap."""
    letter = tz_letter_dict[zone_name]
    if doing_html:
        return "".join(['<span class="box-tz">', letter, "</span>"])
    else:
        return letter


# This dictionary of special cases for daystring is easier to read
# than hand-writing all the if-thens.
# The special cases are ones which don't need the "rotation trick"
# (or, in the case of SaSu, where we want to *avoid* it)
daystring_special_cases = {
    (1, 1, 1, 1, 1, 1, 1): "Daily",
    # Missing only one day
    (1, 1, 1, 1, 1, 1, 0): "Mo-Sa",
    (0, 1, 1, 1, 1, 1, 1): "Tu-Su",
    (1, 0, 1, 1, 1, 1, 1): "We-Mo",
    (1, 1, 0, 1, 1, 1, 1): "Th-Tu",
    (1, 1, 1, 0, 1, 1, 1): "Fr-We",
    (1, 1, 1, 1, 0, 1, 1): "Sa-Th",
    (1, 1, 1, 1, 1, 0, 1): "Su-Fr",
    # Missing two consecutive days (including Mo-Fr)
    (1, 1, 1, 1, 1, 0, 0): "Mo-Fr",
    (0, 1, 1, 1, 1, 1, 0): "Tu-Sa",
    (0, 0, 1, 1, 1, 1, 1): "We-Su",
    (1, 0, 0, 1, 1, 1, 1): "Th-Mo",
    (1, 1, 0, 0, 1, 1, 1): "Fr-Tu",
    (1, 1, 1, 0, 0, 1, 1): "Sa-We",
    (1, 1, 1, 1, 0, 0, 1): "Su-Th",
    # Missing three consecutive days
    (1, 1, 1, 1, 0, 0, 0): "Mo-Th",
    (0, 1, 1, 1, 1, 0, 0): "Tu-Fr",
    (0, 0, 1, 1, 1, 1, 0): "We-Sa",
    (0, 0, 0, 1, 1, 1, 1): "Th-Su",
    (1, 0, 0, 0, 1, 1, 1): "Fr-Mo",
    (1, 1, 0, 0, 0, 1, 1): "Sa-Tu",
    (1, 1, 1, 0, 0, 0, 1): "Su-We",
    # Missing four consecutive days
    (1, 1, 1, 0, 0, 0, 0): "Mo-We",
    (0, 1, 1, 1, 0, 0, 0): "Tu-Th",
    (0, 0, 1, 1, 1, 0, 0): "We-Fr",
    (0, 0, 0, 1, 1, 1, 0): "Th-Sa",
    (0, 0, 0, 0, 1, 1, 1): "Fr-Su",
    (1, 0, 0, 0, 0, 1, 1): "Sa-Mo",
    (1, 1, 0, 0, 0, 0, 1): "Su-Tu",
    # Only running two consecutive days
    # (including SaSu, which we need to avoid SuSa in -1 offset cases)
    (1, 1, 0, 0, 0, 0, 0): "MoTu",
    (0, 1, 1, 0, 0, 0, 0): "TuWe",
    (0, 0, 1, 1, 0, 0, 0): "WeTh",
    (0, 0, 0, 1, 1, 0, 0): "ThFr",
    (0, 0, 0, 0, 1, 1, 0): "FrSa",
    (0, 0, 0, 0, 0, 1, 1): "SaSu",
    (1, 0, 0, 0, 0, 0, 1): "SuMo",
    # Only running on one day a week
    (1, 0, 0, 0, 0, 0, 0): "Mo",
    (0, 1, 0, 0, 0, 0, 0): "Tu",
    (0, 0, 1, 0, 0, 0, 0): "We",
    (0, 0, 0, 1, 0, 0, 0): "Th",
    (0, 0, 0, 0, 1, 0, 0): "Fr",
    (0, 0, 0, 0, 0, 1, 0): "Sa",
    (0, 0, 0, 0, 0, 0, 1): "Su",
}


def day_string(calendar, offset: int = 0) -> str:
    """Return "MoWeFr" style string for days of week.

    Given a calendar DataTable which contains only a single row for a single service,
    this returns a string like "Daily" or "MoWeFr" for the serviced days of the week.

    Use offset to get the string for stops which are more than 24 hours after initial
    depature. Beware of time zone changes!

    I have had more requests for tweaks to this format than anything else!
    """
    days_of_service_list = calendar.to_dict("records")
    # if there are zero or duplicate service records, we error out.
    if len(days_of_service_list) == 0:
        raise GTFSError("daystring() can't handle an empty calendar")
    if len(days_of_service_list) >= 2:
        raise GTFSError(
            "daystring() can't handle two calendars for service_id: ",
            days_of_service_list,
        )
    days_of_service = days_of_service_list[0]

    # Use modulo to correct the offset to the range 0:6
    # Note timezone differences can lead to -1 offset.
    # Later stations on the route lead to positive offset.
    offset %= 7

    # OK.  Fast encoding version here as a list of 1s and 0s.
    days_of_service_vector = [
        days_of_service["monday"],
        days_of_service["tuesday"],
        days_of_service["wednesday"],
        days_of_service["thursday"],
        days_of_service["friday"],
        days_of_service["saturday"],
        days_of_service["sunday"],
    ]

    # Do the offset rotation.
    def rotate_right(l, n):
        return l[-n:] + l[:-n]

    days_of_service_vector = rotate_right(days_of_service_vector, offset)

    # Try the lookup-table path.
    try:
        daystring = daystring_special_cases[tuple(days_of_service_vector)]
        return daystring
    except KeyError:
        pass

    # Lookup-table path failed.
    # Now we have to do it the hard way, by just patching days of the week together.
    # This probably means the days of non-operation are non-consecutive (MWF or whatever).

    # Now we get tricky.  We want the days of the week to line up as they cycle around the clock.
    # This is kind of messy!  We always use the order of the original, zero-offset day.
    # That's slightly wacky for the -1 offsets -- Su is first instead of Mo -- but that is OK.
    daystring = ""
    if days_of_service["monday"]:
        daystring += ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"][offset]
    if days_of_service["tuesday"]:
        daystring += ["Tu", "We", "Th", "Fr", "Sa", "Su", "Mo"][offset]
    if days_of_service["wednesday"]:
        daystring += ["We", "Th", "Fr", "Sa", "Su", "Mo", "Tu"][offset]
    if days_of_service["thursday"]:
        daystring += ["Th", "Fr", "Sa", "Su", "Mo", "Tu", "We"][offset]
    if days_of_service["friday"]:
        daystring += ["Fr", "Sa", "Su", "Mo", "Tu", "We", "Th"][offset]
    if days_of_service["saturday"]:
        daystring += ["Sa", "Su", "Mo", "Tu", "We", "Th", "Fr"][offset]
    if days_of_service["sunday"]:
        daystring += ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"][offset]

    if daystring == "":
        raise GTFSError("No days of operation?!?")

    # Generic case
    return daystring


# Timestr functions
class TimeTuple(NamedTuple):
    """Class with time broken into pieces for printing."""

    day: int
    pm: int
    hour: int
    hour24: int
    min: int
    sec: int


def explode_timestr(timestr: str, zonediff: int = 0) -> TimeTuple:
    """Given a GTFS timestr, return a TimeTuple.

    TimeTuple is a namedtuple giving 'day', 'pm', 'hour' (12 hour), 'hour24' ,'min',
    'sec'.

    zonediff is the number of hours to adjust to convert to local time before exploding.
    """
    try:
        longhours, mins, secs = [int(x) for x in timestr.split(":")]
        longhours += zonediff  # this is the timezone adjustment
    except Exception as exc:
        # Winnipeg-Churchill timetable has NaNs -- don't let it get here!
        raise GTFSError("Timestr didn't parse right", timestr) from exc
        # Return all-zeroes to identify where it happened
        # return TimeTuple(day=0,pm=0,hour=0,hour24=0,min=0,sec=0)
    # Note: the following does the right thing for negative hours
    # (which can be created by the timezone adjustment)
    # It will give -1 days and positive hours24.
    [days, hours24] = divmod(longhours, 24)
    [pm, hours] = divmod(hours24, 12)
    my_time = TimeTuple(day=days, pm=pm, hour=hours, hour24=hours24, min=mins, sec=secs)
    # could do as dict, but seems cleaner this way
    return my_time


def time_short_str_24(time: TimeTuple, box_time_characters=False) -> str:
    """Given an exploded TimeTuple, give a short version of the time suitable for a
    timetable.

    But do it in "military" format from 0:00 to 23:59.
    doing_html: Box each character in a html span, to simulate tabular numbers with non-tabular fonts.
    """
    # Note that this is very explicitly designed to be fixed width
    time_text = [
        f"{time.hour24 : >2}",
        ":",
        f"{time.min    :0>2}",
    ]
    time_str = "".join(time_text)  # String suitable for plaintext
    if box_time_characters:
        # There are exactly five characters, by construction.  23:59 is largest.
        html_time_str = "".join(
            [
                '<span class="box-digit">',
                time_str[0],
                "</span>",
                '<span class="box-digit">',
                time_str[1],
                "</span>",
                '<span class="box-colon">',
                time_str[2],
                "</span>",
                '<span class="box-digit">',
                time_str[3],
                "</span>",
                '<span class="box-digit">',
                time_str[4],
                "</span>",
            ]
        )
        time_str = html_time_str
    return time_str


# Named constant useful for the next method:
ampm_str = ["A", "P"]  # index into this to get the am or pm string


def time_short_str_12(time: TimeTuple, box_time_characters=False) -> str:
    """Given an exploded TimeTuple, give a short version of the time suitable for a
    timetable.

    Do it with AM and PM.
    doing_html: Box each character in a html span, to simulate tabular numbers with non-tabular fonts.
    """
    # Note that this is very explicitly designed to be fixed width
    hour = time.hour
    if hour == 0:
        hour = 12
    time_text = [
        f"{hour     : >2}",
        ":",
        f"{time.min :0>2}",
        ampm_str[time.pm],
    ]
    time_str = "".join(time_text)  # String suitable for plaintext
    if box_time_characters:
        # There are exactly six characters, by construction. 12:59P is largest.
        html_time_str = "".join(
            [
                '<span class="box-1">',
                time_str[0],
                "</span>",
                '<span class="box-digit">',
                time_str[1],
                "</span>",
                '<span class="box-colon">',
                time_str[2],
                "</span>",
                '<span class="box-digit">',
                time_str[3],
                "</span>",
                '<span class="box-digit">',
                time_str[4],
                "</span>",
                '<span class="box-ap">',
                time_str[5],
                "</span>",
            ]
        )
        time_str = html_time_str
    return time_str


def modulo24(raw_timestr: str) -> str:
    """Given a departure_time GTFS str, subtract full days and get a departure *time*.

    Used to sort trains by departure time in list_trains.py.
    """
    time = explode_timestr(raw_timestr)
    return f"{time.hour24: >2}:{time.min:0>2}:{time.sec:0>2}"
