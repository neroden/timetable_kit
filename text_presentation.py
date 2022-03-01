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

def get_rd_str( timepoint,
                doing_html=False,
                is_first_stop=False,
                is_last_stop=False,
                is_first_line=False,
                is_second_line=False,
                is_arrival_line=False,
                is_departure_line=False
              ):
    '''
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
    '''
    # Important note: there's currently no way to identify the infamous "L",
    # which means the train or bus is allowed to depart ahead of time
    rd_str = " " # NOTE the default is one blank space, for plaintext output.

    if (timepoint.drop_off_type == 1 and timepoint.pickup_type == 0):
        if (not is_first_stop): # This is obvious at the first station
            if (not is_arrival_line): # put on departure line
                rd_str = "R" # Receive passengers only
    elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 0):
        if (not is_last_stop): # This is obvious at the last station
            if (not is_departure_line): # put on arrival line
                rd_str = "D" # Discharge passengers only
    elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 1):
        if (not is_second_line): # it'll be on the first line
            rd_str = "*" # Not for ordinary passengers (staff only, perhaps)
    elif (timepoint.pickup_type >= 2 or timepoint.drop_off_type >= 2):
        if (not is_second_line): # it'll be on the first line
            rd_str = "F" # Flag stop of some type
    elif ("timepoint" in timepoint):
        # If the "timepoint" column has been supplied
        # IMPORTANT NOTE: Amtrak has not implemented this yet.
        # FIXME: request that Alan Burnstine implement this if possible
        # This seems to be the only way to identify the infamous "L",
        # which means that the train or bus is allowed to depart ahead of time
        print ("timepoint column found") # Should not happen with existing data
        if (timepoint.timepoint == 0): # and it says times aren't exact
            if (not is_arrival_line): # This goes on departure line, always
                rd_str = "L"

    # Now: this is an utterly stupid hack used for HTML width testing:
    # Not for production code.  Enable if you need to recheck CSS span widths.
    # if (timepoint.stop_id=="CLF"):
    #     rd_str = "M"
    # if (timepoint.stop_id=="CVS"):
    #     rd_str = "M"

    if (doing_html):
        if (rd_str != " "):
            # Boldface it:
            rd_str = ''.join(['<b>',rd_str,'</b>'])
        # Always wrap it in the span, even if it's a blank space:
        rd_str = ''.join([ '<span class="box-rd">', rd_str, '</span>' ])
    return rd_str

def timepoint_str ( timepoint,
                    two_row=False,
                    second_timepoint=None,
                    use_ar_dp_str=False,
                    reverse=False,
                    doing_html=False,
                    bold_pm=True,
                    use_24=False,
                    use_daystring=False,
                    calendar=None,
                    is_first_stop=False,
                    is_last_stop=False,
                   ):
    '''
    Produces a text or HTML string for display in a timetable, showing the time of departure, arrival, and extra symbols.
    This is quite complex: I would have used tables-within-tables but they're screen-reader-unfriendly.

    It MUST be printed in a fixed-width font and formatting MUST be preserved: quite ugly work really

    The most excruciatingly complex variant looks like:
    Ar F 9:59P Daily
    Dp F10:00P WeFrSu

    Mandatory argument:
    -- timepoint: a single row from stop_times.
    Options are many:
    -- two_row: This timepoint gets both arrival and departure rows (default is just one row)
    -- second_timepoint: Used for a very tricky thing with connecting trains to show them in the
        same column at the same station; normally None, specified at that particular station
    -- use_ar_dp_str: Use "Ar " and "Dp " or leave space for them (use only where appropriate)
    -- reverse: This piece of the timetable is running upward (departure time above arrival time)
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
    departure_time_str = time_str(departure)
    if doing_html:
        if (bold_pm and departure.pm == 1):
            departure_time_str = ''.join(["<b>",departure_time_str,"</b>"])
        if (use_24):
            departure_time_str = ''.join([ '<span class="box-time24">', departure_time_str, '</span>' ])
        else:
            departure_time_str = ''.join([ '<span class="box-time12">', departure_time_str, '</span>' ])

    # Fill the TimeTuple and prep string for actual time
    arrival = explode_timestr(timepoint.arrival_time)
    arrival_time_str = time_str(arrival)
    # HTML bold annotation for PM
    if doing_html:
        if (bold_pm and arrival.pm == 1):
            arrival_time_str = ''.join(["<b>",arrival_time_str,"</b>"])
        if (use_24):
            arrival_time_str = ''.join([ '<span class="box-time24">', arrival_time_str, '</span>' ])
        else:
            arrival_time_str = ''.join([ '<span class="box-time12">', arrival_time_str, '</span>' ])

    # Fill in the day strings, if we're using it
    departure_daystring = ""
    arrival_daystring = ""
    if (use_daystring):
        # Note that daystring is VARIABLE LENGTH, and is the only variable-length field
        # It must be last and the entire time field must be left-justified as a result
        departure_daystring = day_string(calendar, offset=departure.day)
        arrival_daystring = day_string(calendar, offset=arrival.day)
        if (doing_html):
            departure_daystring= ''.join([ '<span class="box-days">', departure_daystring, '</span>' ])
            arrival_daystring= ''.join([ '<span class="box-days">', arrival_daystring, '</span>' ])
        else:
            # Add a necessary spacer: CSS does it for us in HTML
            departure_daystring = ''.join([" ", departure_daystring])
            arrival_daystring = ''.join([" ", arrival_daystring])


    ar_str = "" # If we are not adding the padding at all -- unwise with two_row
    dp_str = "" # Again, if we are not adding the "Ar/Dp" at all
    if (use_ar_dp_str):
        if doing_html:
            ar_str='<span class="box-ardp">Ar</span>'
            dp_str='<span class="box-ardp">Dp</span>'
        else:
            ar_str = "Ar "
            dp_str = "Dp "
            ardp_spacer = "   "

    # Determine whether we are looking at receive-only or discharge-only
    receive_only = False;
    discharge_only = False;
    if (is_first_stop):
        receive_only = True; # Logically speaking
    if (is_last_stop):
        discharge_only = True; # Logically speaking
    if (timepoint.drop_off_type == 1 and timepoint.pickup_type == 0):
        receive_only = True;
    elif (timepoint.pickup_type == 1 and timepoint.drop_off_type == 0):
        discharge_only = True;

    # One-row version: easier logic.  Returns early.
    if (not two_row):
        rd_str = get_rd_str( timepoint,
                             doing_html=doing_html,
                             is_first_stop=is_first_stop,
                             is_last_stop=is_last_stop,
                           )

        ar_dp_str = "" # If we are not adding the padding at all
        if (use_ar_dp_str):
            if not doing_html: # HTML spaces this using the boxes
                ar_dp_str = ardp_spacer # Two spaces, like "Ar", on most stops
        if (is_first_stop):
            ar_dp_str = dp_str # Mark departure on first stop
        elif (is_last_stop):
            ar_dp_str = ar_str # Mark arrival on last stop

        # Each element joined herein includes HTML annotations, and is completely blank if unused
        complete_line_str = ''.join([ ar_dp_str,
                                      rd_str,
                                      arrival_time_str if discharge_only else departure_time_str,
                                      arrival_daystring if discharge_only else departure_daystring,
                                    ])
        return complete_line_str

    # Two row version follows:
    else: # two_row

        # Start assembling the two lines.
        if (receive_only):
            arrival_line_str = ''
        else:
            arrival_rd_str  = get_rd_str( timepoint,
                                          doing_html=doing_html, is_first_stop=is_first_stop, is_last_stop=is_last_stop,
                                          is_first_line=(not reverse), #arrival is first unless reversing
                                          is_second_line=(reverse),
                                          is_arrival_line=True,
                                        )
            arrival_line_str = ''.join([ ar_str,
                                         arrival_rd_str,
                                         arrival_time_str,
                                         arrival_daystring,
                                        ])
        if (discharge_only):
            departure_line_str = ''
        else:
            departure_rd_str = get_rd_str( timepoint,
                                           doing_html=doing_html, is_first_stop=is_first_stop, is_last_stop=is_last_stop,
                                           is_second_line=(reverse),    #departure is second unless reversing
                                           is_first_line=(not reverse),
                                           is_departure_line=True,
                                          )
            departure_line_str = ''.join([ dp_str,
                                           departure_rd_str,
                                           departure_time_str,
                                           departure_daystring,
                                          ])

        if (discharge_only and (not reverse) and second_timepoint):
            # Fill the second line from a different train service.
            # Shamefully untested.  FIXME
            departure_line_str = timepoint_str( second_timepoint,
                                                two_row=False,
                                                second_timepoint=None,
                                                use_ar_dp_str=use_ar_dp_str,
                                                doing_html=doing_html,
                                                bold_pm=bold_pm,
                                                use_24=use_24,
                                                use_daystring=use_daystring,
                                                calendar=None, # would need to be calendar for second timepoint; FIXME
                                                is_first_stop=True, # Suppress "R"; effectively first stop of connecting train
                                                is_last_stop=False,
                                               )

        if (receive_only and (reverse) and second_timepoint):
            # Fill the second line from a different train service.
            # Shamefully untested.  FIXME
            arrival_line_str = timepoint_str( second_timepoint,
                                              two_row=False,
                                              second_timepoint=None,
                                              use_ar_dp_str=use_ar_dp_str,
                                              doing_html=doing_html,
                                              bold_pm=bold_pm,
                                              use_24=use_24,
                                              use_daystring=use_daystring,
                                              calendar=None, # would need to be calendar for second timepoint; FIXME
                                              is_first_stop=True,
                                              is_last_stop=True, # Suppress "D"; effectively last stop of connecting-from train
                                             )

        # Patch the two rows together.
        if (not reverse):
            complete_line_str = linebreak.join([arrival_line_str, departure_line_str])
        else: # reverse
            complete_line_str = linebreak.join([departure_line_str, arrival_line_str])
        return complete_line_str

    # We should not reach here; we should have returned earlier.
    assert False
    return
