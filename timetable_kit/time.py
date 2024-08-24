# time.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023, 2024 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Module for processing GTFS times and producing strings.
"""
from __future__ import annotations

from datetime import datetime, timedelta  # for time zones
from functools import total_ordering
from typing import NamedTuple  # for TimeTuple
from zoneinfo import ZoneInfo  # still for time zones

# These are mine
from timetable_kit.errors import GTFSError
from timetable_kit.utils import span_enclose


def gtfs_date_to_isoformat(gtfs_date: str | int) -> str:
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
        return span_enclose("box-tz", letter)
    else:
        return letter


# Timestr functions
@total_ordering
class TimeTuple(NamedTuple):
    """Class with time broken into pieces for printing."""

    day: int
    pm: bool
    hour12: int
    hour24: int
    min: int
    sec: int

    @classmethod
    def from_gtfs_time_string(
        cls, timestr: str | TimeTuple, zonediff: int = 0
    ) -> TimeTuple:
        """Given a GTFS timestr, return a TimeTuple.

        TimeTuple is a namedtuple giving 'day', 'pm', 'hour' (12 hour), 'hour24' ,'min',
        'sec'.

        zonediff is the number of hours to adjust to convert to local time before exploding.
        """
        if isinstance(timestr, TimeTuple):
            return timestr
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
        my_time = TimeTuple(
            day=days, pm=bool(pm), hour12=hours, hour24=hours24, min=mins, sec=secs
        )
        # could do as dict, but seems cleaner this way
        return my_time

    def __lt__(self, other: TimeTuple) -> bool:
        return self.modulo24_str() < other.modulo24_str()

    def __eq__(self, other: TimeTuple) -> bool:
        return self.modulo24_str() == other.modulo24_str()

    def modulo24_str(self) -> str:
        return f"{self.hour24: >2}:{self.min:0>2}:{self.sec:0>2}"


def modulo24(raw_timestr: str) -> str:
    """Given a departure_time GTFS str, subtract full days and get a departure *time*.

    Used to sort trains by departure time in list_trains.py.
    """
    time = TimeTuple.from_gtfs_time_string(raw_timestr)
    return time.modulo24_str()
