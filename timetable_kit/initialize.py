# initialize.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Initalize the GTFS feed and related stuff

Used by multiple command-line programs
"""

# Other people's packages
from pathlib import Path
import datetime

import gtfs_kit

# My packages: Local module imports

# This one monkey-patches gtfs_kit.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

from timetable_kit import gtfs_type_cleanup
from timetable_kit.debug import debug_print

#### INITIALIZATION CODE
def initialize_feed(gtfs):
    """
    Initialize the master_feed and related variables.

    Does some cleaning, and removal of the large shapes table which we don't use.

    gtfs: may be a filename or a Path.
    """

    debug_print(1, "Using GTFS file " + str(gtfs))
    gtfs_path = Path(gtfs)
    # The unit is only relevant if we read the shapes file; we currently don't.
    # Also affects display miles so default to mi.
    master_feed = gtfs_kit.read_feed(gtfs_path, dist_units="mi")
    debug_print(1, "Feed loaded")

    # We don't use the shapes file.  It takes up a LOT of memory.  Destroy it.
    master_feed.shapes = None

    # Need to clean up times to zero-pad them for sorting.
    master_feed = master_feed.clean_times()

    # Don't waste time.
    # master_feed.validate()

    # Fix types on every table in the feed
    # Also deals with blank entries (NaNs) correctly
    # Particularly tricky on timepoint, which defaults to 1
    gtfs_type_cleanup.fix(master_feed)

    debug_print(1, "Feed initialized")
    return master_feed


def filter_feed_for_utilities(feed, reference_date=None, day_of_week=None):
    """
    Filter the feed down based on command line arguments, for the auxiliary utility programs
    such as list_trains.py and list_stations.py

    Returns a new, filtered feed.
    """
    if reference_date is None:
        reference_date = datetime.date.today().strftime("%Y%m%d")
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")
    today_feed = feed.filter_by_dates(reference_date, reference_date)

    # Restrict by day of week if specified.
    if day_of_week is not None:
        day_of_week = day_of_week.lower()
        if day_of_week not in feed_enhanced.gtfs_days:
            print("Specifed day of week not understood.")
            exit(1)
        debug_print(1, "Restricting to ", day_of_week, ".", sep="")
        today_feed = today_feed.filter_by_day_of_week(day_of_week)

    return today_feed
