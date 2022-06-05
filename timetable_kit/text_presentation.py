# text_presentation.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Module for presenting small bits of text for the timetable.

This produces strings like "MoWeFr" and "Ar D11:49P".
Some routines have HTML variants and plaintext variants.

All the "character twiddling" operations are in here.
"""

import pandas as pd
import gtfs_kit as gk
from collections import namedtuple

from datetime import datetime, timedelta  # for time zones
from zoneinfo import ZoneInfo  # still for time zones

# These are mine
from timetable_kit.errors import GTFSError, FutureCodeError
from timetable_kit.debug import debug_print
from timetable_kit.icons import get_baggage_icon_html
from timetable_kit.icons import get_accessible_icon_html
from timetable_kit.tsn import train_spec_to_tsn


def gtfs_date_to_isoformat(gtfs_date: str) -> str:
    """
    Given a GTFS date string, return an ISO format date string.

    This is a triviality: it converts 20220310 to 2022-03-10.
    """
    # Make sure it's a str in case we've been fooling around with these as numbers
    gtfs_date = str(gtfs_date)
    if len(gtfs_date) != 8:
        raise GTFSError("Datestr wrong length", gtfs_date)
    iso_str = "-".join([gtfs_date[:4], gtfs_date[4:6], gtfs_date[6:8]])
    return iso_str


def get_zonediff(local_zone, base_zone, reference_date):
    """
    Get the hour difference which must be applied to a time in base_zone to get a time in local_zone

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


# This is exceedingly US-centric, FIXME
tz_letter_dict = {
    "America/New_York": "ET",
    "America/Chicago": "CT",
    "America/Denver": "MT",
    "America/Phoenix": "MST",
    "America/Los_Angeles": "PT",
}


def get_zone_str(zone_name, doing_html=False):
    """Return a two-letter abbreviation for an IANA time zone, possibly with HTML wrap"""
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
    """
    Return "MoWeFr" style string for days of week.

    Given a calendar DataTable which contains only a single row for a single service, this
    returns a string like "Daily" or "MoWeFr" for the serviced days of the week.

    Use offset to get the string for stops which are more than 24 hours after initial depature.
    Beware of time zone changes!

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
    offset = offset % 7

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
TimeTuple = namedtuple("TimeTuple", ["day", "pm", "hour", "hour24", "min", "sec"])


def explode_timestr(timestr: str, zonediff: int = 0) -> TimeTuple:
    """
    Given a GTFS timestr, return a TimeTuple.

    TimeTuple is a namedtuple giving 'day', 'pm', 'hour' (12 hour), 'hour24' ,'min', 'sec'.

    zonediff is the number of hours to adjust to convert to local time before exploding.
    """
    try:
        longhours, mins, secs = [int(x) for x in timestr.split(":")]
        longhours += zonediff  # this is the timezone adjustment
    except:
        raise GTFSError("Timestr didn't parse right", timestr)
    # Note: the following does the right thing for negative hours
    # (which can be created by the timezone adjustment)
    # It will give -1 days and positive hours24.
    [days, hours24] = divmod(longhours, 24)
    [pm, hours] = divmod(hours24, 12)
    my_time = TimeTuple(day=days, pm=pm, hour=hours, hour24=hours24, min=mins, sec=secs)
    # could do as dict, but seems cleaner this way
    return my_time


def time_short_str_24(time: TimeTuple, box_time_characters=False) -> str:
    """
    Given an exploded TimeTuple, give a short version of the time suitable for a timetable.

    But do it in "military" format from 0:00 to 23:59.
    doing_html: Box each character in an html span, to simulate tabular numbers with non-tabular fonts.
    """
    # Note that this is very explicitly designed to be fixed width
    time_text = [
        "{: >2}".format(time.hour24),
        ":",
        "{:0>2}".format(time.min),
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
    return time_str


# Named constant useful for the next method:
ampm_str = ["A", "P"]  # index into this to get the am or pm string


def time_short_str_12(time: TimeTuple, box_time_characters=False) -> str:
    """
    Given an exploded TimeTuple, give a short version of the time suitable for a timetable.

    Do it with AM and PM.
    doing_html: Box each character in an html span, to simulate tabular numbers with non-tabular fonts.
    """
    # Note that this is very explicitly designed to be fixed width
    hour = time.hour
    if hour == 0:
        hour = 12
    time_text = [
        "{: >2}".format(hour),
        ":",
        "{:0>2}".format(time.min),
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


def get_rd_str(
    timepoint,
    doing_html=False,
    is_first_stop=False,
    is_last_stop=False,
    is_first_line=False,
    is_second_line=False,
    is_arrival_line=False,
    is_departure_line=False,
):
    """
    Return a single character (default " ") with receive-only / discharge-only annotation.
    "R" = Receive-only
    "D" = Discharge-only
    "L" = May leave early (unimplemented)
    "F" = Flag stop
    "*" = Not a regular passenger stop
    " " = Anything else

    Subroutine of timepoint_str.

    doing_html determines whether to produce this letter as HTML (boldfaced) or not.
    is_first_stop suppresses the R for "receive only"
    is_last_stop suppresses the D for "discharge only"

    If you are producing a two-line string,
    is_first_line,
    is_second_line,
    is_arrival_line, and
    is_departure_line
    determine which line gets the letter (it looks ugly for both to get it).
    These should all be false when producing a one-line string.
    """
    # Important note: there's currently no way to identify the infamous "L",
    # which means the train or bus is allowed to depart ahead of time
    rd_str = " "  # NOTE the default is one blank space, for plaintext output.

    match [timepoint.drop_off_type, timepoint.pickup_type, "timepoint" in timepoint]:
        case [1, 0, _]:
            if not is_first_stop:  # This is obvious at the first station
                if not is_arrival_line:  # put on departure line
                    rd_str = "R"  # Receive passengers only
        case [0, 1, _]:
            if not is_last_stop:  # This is obvious at the last station
                if not is_departure_line:  # put on arrival line
                    rd_str = "D"  # Discharge passengers only
        case [1, 1, _]:
            if not is_second_line:  # it'll be on the first line
                rd_str = "*"  # Not for ordinary passengers (staff only, perhaps)
        case [2 | 3, _, _] | [_, 2 | 3, _]:
            if not is_second_line:  # it'll be on the first line
                rd_str = "F"  # Flag stop of some type
        case [_, _, True]:
            # If the "timepoint" column has been supplied
            # IMPORTANT NOTE: Amtrak has not implemented this yet.
            # FIXME: request that Alan Burnstine implement this if possible
            # This seems to be the only way to identify the infamous "L",
            # which means that the train or bus is allowed to depart ahead of time
            print("timepoint column found")  # Should not happen with existing data
            if timepoint.timepoint == 0:  # and it says times aren't exact
                if not is_arrival_line:  # This goes on departure line, always
                    rd_str = "L"

    # Now: this is an utterly stupid hack used for HTML width testing:
    # Not for production code.  Enable if you need to recheck CSS span widths.
    # if (timepoint.stop_id=="CLF"):
    #    rd_str = "M"
    # if (timepoint.stop_id=="CVS"):
    #    rd_str = "M"

    if doing_html:
        if rd_str != " ":
            # Boldface it:
            rd_str = "".join(["<b>", rd_str, "</b>"])
        # Always wrap it in the span, even if it's a blank space:
        rd_str = "".join(['<span class="box-rd">', rd_str, "</span>"])
    return rd_str


baggage_box_prefix = '<span class="box-baggage">'
baggage_box_postfix = "</span>"


def get_baggage_str(doing_html=False):
    """
    Return a suitable string to indicate the presence of checked baggage.

    Currently the HTML implementation references an external checked baggage icon.
    There are inline alternatives to this but Weasyprint isn't nice about them.
    """
    if not doing_html:
        return "B"
    return "".join(
        [
            baggage_box_prefix,
            '<span class="baggage-symbol">',
            get_baggage_icon_html(),
            "</span>",
            baggage_box_postfix,
        ]
    )


def get_blank_baggage_str(doing_html=False):
    """
    Return a suitable string to indicate the absence of checked baggage.

    The HTML implementation boxes it to line things up properly.
    """
    if not doing_html:
        return " "
    return "".join([baggage_box_prefix, baggage_box_postfix])


def timepoint_str(
    timepoint,
    stop_tz,
    agency_tz,
    reference_date,
    doing_html=False,
    box_time_characters=False,
    reverse=False,
    two_row=False,
    use_ar_dp_str=False,
    bold_pm=True,
    use_24=False,
    use_daystring=False,
    long_days_box=False,
    short_days_box=False,
    calendar=None,
    is_first_stop=False,
    is_last_stop=False,
    use_baggage_str=False,
    has_baggage=False,
):
    """
    Produces a text or HTML string for display in a timetable, showing the time of departure, arrival, and extra symbols.

    This is quite complex: I would have used tables-within-tables but they're screen-reader-unfriendly.
    Trying to do it with fixed-width fonts was too ugly.

    So the the HTML version uses spans with inline-block layout.

    The CSS is elsewhere.

    The most excruciatingly complex variant looks like:
    Ar F 9:59P Daily
    Dp F10:00P WeFrSu

    Mandatory arguments:
    -- timepoint: a single row from stop_times.
    -- stop_tz: timezone for the stop
    -- agency_tz: timezone for the agency
    -- reference_date: reference date for time zone conversion (strictly speaking, needed only for Arizona)
    Options are many:
    -- two_row: This timepoint gets both arrival and departure rows (default is just one row)
    -- use_ar_dp_str: Use "Ar " and "Dp " or leave space for them (use only where appropriate)
    -- reverse: This piece of the timetable is running upward (departure time above arrival time)
    -- doing_html: output HTML (default is plaintext)
    -- box_time_characters: put each character in the time in an HTML box; default is False.
        For use with fonts which don't have tabular nums.  A nasty hack; best to use a font
        which does have tabular nums.
    -- use_24: use 24-hour military time (default is 12 hour time with "A" and "P" suffix)
    -- bold_pm: make PM times bold (even in 24-hour time; only with doing_html
    -- use_daystring: append a "MoWeFr" or "Daily" string.  Only used on infrequent services.
    -- long_days_box: Extra-long space for days, for SuMoTuWeTh five-day calendars.
    -- short_days_box: Extra-short space for days, for "Mo" one-day across-midnight trains.
    -- calendar: a calendar with a single row containing the correct calendar for the service.
           Required if use_daystring is True; pointless otherwise.
    -- is_first_stop: suppress "receive only" notation
    -- is_last_stop: suppress "discharge only" notation
    -- use_baggage_str: True/False: leave space for baggage symbol
    -- has_baggage: True/False: does this stop have checked baggage?
        Ignored if use_baggage_str is False.
    """

    if doing_html:
        linebreak = "<br>"
    else:
        linebreak = "\n"

    if not doing_html:
        box_time_characters = False

    # Pick function for the actual time printing
    if use_24:
        time_str = time_short_str_24
    else:
        time_str = time_short_str_12

    zonediff = get_zonediff(stop_tz, agency_tz, reference_date)

    # Fill the TimeTuple and prep string for actual departure time
    departure = explode_timestr(timepoint.departure_time, zonediff)
    departure_time_str = time_str(departure, box_time_characters=box_time_characters)
    if doing_html:
        if bold_pm and departure.pm == 1:
            departure_time_str = "".join(["<b>", departure_time_str, "</b>"])
        if use_24:
            departure_time_str = "".join(
                ['<span class="box-time24">', departure_time_str, "</span>"]
            )
        else:
            departure_time_str = "".join(
                ['<span class="box-time12">', departure_time_str, "</span>"]
            )

    # Fill the TimeTuple and prep string for actual time
    arrival = explode_timestr(timepoint.arrival_time, zonediff)
    arrival_time_str = time_str(arrival, box_time_characters=box_time_characters)
    if doing_html:
        if bold_pm and arrival.pm == 1:
            arrival_time_str = "".join(["<b>", arrival_time_str, "</b>"])
        if use_24:
            arrival_time_str = "".join(
                ['<span class="box-time24">', arrival_time_str, "</span>"]
            )
        else:
            arrival_time_str = "".join(
                ['<span class="box-time12">', arrival_time_str, "</span>"]
            )

    # Need this for lines just containing "Ar" or "Dp"
    blank_rd_str = ""
    blank_time_str = ""
    if doing_html:
        blank_rd_str = "".join(['<span class="box-rd">', "", "</span>"])
        if use_24:
            blank_time_str = "".join(['<span class="box-time24">', "", "</span>"])
        else:
            blank_time_str = "".join(['<span class="box-time12">', "", "</span>"])

    # Fill in the day strings, if we're using it
    departure_daystring = ""
    arrival_daystring = ""
    blank_daystring = ""
    if use_daystring:
        if long_days_box:
            days_box_class = "box-days-long"
        elif short_days_box:
            days_box_class = "box-days-short"
        else:
            days_box_class = "box-days"
        # Note that daystring is VARIABLE LENGTH, and is the only variable-length field
        # It must be last and the entire time field must be left-justified as a result
        departure_daystring = day_string(calendar, offset=departure.day)
        arrival_daystring = day_string(calendar, offset=arrival.day)
        if doing_html:
            departure_daystring = "".join(
                ['<span class="', days_box_class, '">', departure_daystring, "</span>"]
            )
            arrival_daystring = "".join(
                ['<span class="', days_box_class, '">', arrival_daystring, "</span>"]
            )
            blank_daystring = "".join(
                ['<span class="', days_box_class, '">', "", "</span>"]
            )
        else:
            # Add a necessary spacer: CSS does it for us in HTML
            departure_daystring = "".join([" ", departure_daystring])
            arrival_daystring = "".join([" ", arrival_daystring])
            blank_daystring = ""

    ar_str = ""  # If we are not adding the padding at all -- unwise with two_row
    dp_str = ""  # Again, if we are not adding the "Ar/Dp" at all
    if use_ar_dp_str:
        if doing_html:
            ar_str = '<span class="box-ardp">Ar</span>'
            dp_str = '<span class="box-ardp">Dp</span>'
        else:
            ar_str = "Ar "
            dp_str = "Dp "
            ardp_spacer = "   "

    # Determine whether we are looking at receive-only or discharge-only
    receive_only = False
    discharge_only = False
    if is_first_stop:
        receive_only = True
        # Logically speaking
    if is_last_stop:
        discharge_only = True
        # Logically speaking
    if timepoint.drop_off_type == 1 and timepoint.pickup_type == 0:
        receive_only = True
    elif timepoint.pickup_type == 1 and timepoint.drop_off_type == 0:
        discharge_only = True

    # One-row version: easier logic.  Returns early.
    if not two_row:
        rd_str = get_rd_str(
            timepoint,
            doing_html=doing_html,
            is_first_stop=is_first_stop,
            is_last_stop=is_last_stop,
        )

        ar_dp_str = ""  # If we are not adding the padding at all
        if use_ar_dp_str:
            if not doing_html:  # HTML spaces this using the boxes
                ar_dp_str = ardp_spacer  # Two spaces, like "Ar", on most stops
        if is_first_stop:
            ar_dp_str = dp_str  # Mark departure on first stop
        elif is_last_stop:
            ar_dp_str = ar_str  # Mark arrival on last stop

        if not use_baggage_str:
            baggage_str = ""
        elif has_baggage:
            baggage_str = get_baggage_str(doing_html=doing_html)
        else:
            baggage_str = get_blank_baggage_str(doing_html=doing_html)

        # Each element joined herein includes HTML annotations, and is completely blank if unused
        complete_line_str = "".join(
            [
                ar_dp_str,
                rd_str,
                arrival_time_str if discharge_only else departure_time_str,
                arrival_daystring if discharge_only else departure_daystring,
                baggage_str,
            ]
        )
        return complete_line_str

    # Two row version follows:
    else:  # two_row
        # Special handling for two-row stations with no dwell
        no_dwell = False
        if timepoint.departure_time == timepoint.arrival_time:
            no_dwell = True

        # Put baggage_str on line one, leave line two blank
        # Note, this won't work with a second timepoint (which isn't implemented anyway)
        if not use_baggage_str:
            arrival_baggage_str = ""
            departure_baggage_str = ""
            blank_baggage_str = ""
        else:
            blank_baggage_str = get_blank_baggage_str(doing_html=doing_html)
            departure_baggage_str = blank_baggage_str
            arrival_baggage_str = blank_baggage_str
            if has_baggage:
                if receive_only or (no_dwell and not discharge_only):
                    # On the only printed line
                    departure_baggage_str = get_baggage_str(doing_html=doing_html)
                elif discharge_only:
                    # On the only printed line
                    arrival_baggage_str = get_baggage_str(doing_html=doing_html)
                elif reverse:
                    # On the first of two printed lines
                    departure_baggage_str = get_baggage_str(doing_html=doing_html)
                else:
                    # On the first of two printed lines
                    arrival_baggage_str = get_baggage_str(doing_html=doing_html)

        # Start assembling the two lines.
        if receive_only or (no_dwell and not discharge_only):
            # This just prints the "Ar" but does the alignment (hopefully)
            arrival_line_str = "".join(
                [
                    ar_str,
                    blank_rd_str,
                    blank_time_str,
                    blank_daystring,
                    blank_baggage_str,
                ]
            )
        else:
            arrival_rd_str = get_rd_str(
                timepoint,
                doing_html=doing_html,
                is_first_stop=is_first_stop,
                is_last_stop=is_last_stop,
                is_first_line=(not reverse),  # arrival is first unless reversing
                is_second_line=(reverse),
                is_arrival_line=True,
            )
            arrival_line_str = "".join(
                [
                    ar_str,
                    arrival_rd_str,
                    arrival_time_str,
                    arrival_daystring,
                    arrival_baggage_str,
                ]
            )
        if discharge_only:
            # This just prints the "Dp" but does the alignment (hopefully)
            departure_line_str = "".join(
                [
                    dp_str,
                    blank_rd_str,
                    blank_time_str,
                    blank_daystring,
                    blank_baggage_str,
                ]
            )
        else:
            departure_rd_str = get_rd_str(
                timepoint,
                doing_html=doing_html,
                is_first_stop=is_first_stop,
                is_last_stop=is_last_stop,
                is_second_line=(reverse),  # departure is second unless reversing
                is_first_line=(not reverse),
                is_departure_line=True,
            )
            departure_line_str = "".join(
                [
                    dp_str,
                    departure_rd_str,
                    departure_time_str,
                    departure_daystring,
                    departure_baggage_str,
                ]
            )

        # Patch the two rows together.
        if not reverse:
            complete_line_str = linebreak.join([arrival_line_str, departure_line_str])
        else:  # reverse
            complete_line_str = linebreak.join([departure_line_str, arrival_line_str])
        return complete_line_str

    # We should not reach here; we should have returned earlier.
    assert False


# Used for get_time_column_header
# This is the *complete* list of valid GTFS codes
# Amtrak only uses 2 and 3, but why not?
route_number_prefix_map = {
    1: "Tram #",
    2: "Train #",
    3: "Bus #",
    4: "Ferry #",
    5: "Cable Car #",
    6: "Gondola #",
    7: "Funicular #",
    11: "Trolleybus #",
    12: "Monorail Train #",
}


def get_time_column_header(
    train_specs: list[str],
    route_from_train_spec,
    doing_html=False,
    train_numbers_side_by_side=False,
) -> str:
    """
    Return the header for a column of times.

    train_specs: should be a list of train_specs (ordered).

    Each train_spec is a trip_short_name, possibly followed by a space and a lowercase day of the week.

    route_from_train_spec: function taking train_spec and giving a route row from the GTFS routes table.
    train_numbers_side_by_side: List train numbers with a slash instead of on top of each other.
    """
    if not train_specs:
        raise InputError("No train_specs?")

    if not doing_html:
        # For plaintext, keep it simple: just the train specs
        return " / ".join(train_specs)

    if train_numbers_side_by_side:
        # Old algorithm.  For Empire Builder, Lake Shore Limited.

        # Strip the " monday" type suffixes, but add a comment to keep them unique:
        # PANDAS requires every column header to be unique
        tsns = [
            train_spec_to_tsn(train_spec, doing_html=True) for train_spec in train_specs
        ]

        # For HTML, let's get FANCY... May change this later.
        # Route types: 2 is a train, 3 is a bus
        route_types = [
            int(route_from_train_spec(train_spec).route_type)
            for train_spec in train_specs
        ]
        match route_types:
            case [2]:
                time_column_prefix = "Train #"
            case [3]:
                time_column_prefix = "Bus #"
            case [3, 2]:
                time_column_prefix = "Bus/Train #s"
            case [2, 3]:
                time_column_prefix = "Train/Bus #s"
            case _:
                route_set = set(route_types)
                if route_set == {2}:
                    time_column_prefix = "Train #s"
                elif route_set == {3}:
                    time_column_prefix = "Bus #s"
                elif route_set == {2, 3}:
                    # This is three or more routes in the same column, yeechburgers
                    time_column_prefix = "Train/Bus #s"
                else:
                    # Not train or bus.  Does not occur on Amtrak.
                    time_column_prefix = "Trip #s"

        time_column_header = "".join(
            [
                "<small>",
                time_column_prefix,
                "</small>",
                "<br>",
                "<strong>",
                " / ".join(tsns),  # Note! Works cleanly for single-element case
                "</strong>",
            ]
        )
        return time_column_header

    # New algorithm.
    # Numbers are stacked.
    # Putting slashes between the train and bus number has proven to make
    # overly-wide columns.  Aaargh!

    prefixed_route_numbers = [
        "".join(
            [
                "<small>",
                route_number_prefix_map[
                    int(route_from_train_spec(train_spec).route_type)
                ],
                "</small>",
                "<br>",
                "<strong>",
                # Strip the " monday" type suffix, but add a comment to keep them unique:
                # PANDAS requires every column header to be unique
                train_spec_to_tsn(train_spec, doing_html=True),
                "</strong>",
            ]
        )
        for train_spec in train_specs
    ]
    time_column_header = "<hr>".join(prefixed_route_numbers)
    return time_column_header


def get_station_column_header(doing_html=False):
    """
    Return the header for a column of station names.

    Currently just the word "Station".
    """
    return "Station"


def get_services_column_header(doing_html=False):
    """
    Return the header for a column of station services icons.

    Tricky because the column should be very narrow.
    Wraps with a special CSS div, so it can be rotated.
    """
    if doing_html:
        return '<div class="services-header-text">Station<br>Services</div>'
    else:
        return "Services"


def get_access_column_header(doing_html=False):
    """
    Return the header for a column of accessibility icons.

    Tricky because the column should be very narrow.

    Use the wheelchair icon.
    Wraps with a special CSS div, so it can be rotated.
    """
    if doing_html:
        accessible_icon_html = get_accessible_icon_html()
        return "".join(
            ['<div class="access-header-text">', " ", accessible_icon_html, "</div>"]
        )
    else:
        return "Access"


def get_timezone_column_header(doing_html=False):
    """
    Return the header for a column of station time zones.

    Tricky because the column should be very narrow.
    Wraps with a special CSS div, so it can be rotated.
    """
    if doing_html:
        # return '<div class="timezone-header-text">Time<br>Zone</div>'
        # Keep it one line, space is at a premium
        return '<div class="timezone-header-text">TZ</div>'
    else:
        return "Time Zone"


def style_route_name_for_column(route_name, doing_html=False):
    """
    Style a route name for HTML (or not) for a column header

    This is largely a matter of whitespace.  And quite tricky.
    """
    if not doing_html:
        return route_name

    # "Route name words" / "Route name lines"
    rnw = route_name.split()
    debug_print(2, rnw)
    # If four words, combine last two if one is really short
    if len(rnw) >= 4:
        if len(rnw[2]) <= 3 or len(rnw[3]) <= 3:
            rnw = [rnw[0], rnw[1], "".join([rnw[2], " ", rnw[3]]), *rnw[4:]]
    # Combine first two words if one is really short
    if len(rnw) >= 2:
        if len(rnw[0]) <= 3 or len(rnw[1]) <= 3:
            rnw = ["".join([rnw[0], " ", rnw[1]]), *rnw[2:]]

    linebroken_str = "<br>".join(rnw)
    final_str = "".join(['<div class="box-route-name">', linebroken_str, "</div>"])
    return final_str


def style_updown(reverse: bool, doing_html=False) -> str:
    """
    Style "Read Up" or "Read Down" column subheader
    """
    if reverse:
        text = "Read Up"
    else:
        text = "Read Down"

    if not doing_html:
        return text

    final_str = "".join(["<b>", text, "</b>"])
    return final_str
