# initialize.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Initalize the GTFS feed and related stuff

Used by multiple command-line programs
"""

# Other people's packages
from pathlib import Path
import gtfs_kit as gk

# My packages: Local module imports

# This one monkey-patches gk.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

from timetable_kit import gtfs_type_cleanup
from timetable_kit.debug import debug_print

#### INITIALIZATION CODE
def initialize_feed(gtfs):
    """
    Initialize the master_feed and related variables.

    gtfs: may be a filename or a Path.
    """

    debug_print(1, "Using GTFS file " + str(gtfs) )
    gtfs_path = Path(gtfs)
    # Amtrak has no shapes file, so no distance units.  Check this if a shapes files appears.
    # Also affects display miles so default to mi.
    master_feed = gk.read_feed(gtfs_path, dist_units='mi')
    debug_print(1, "Feed loaded.")
    # Don't waste time.
    # master_feed.validate()

    # Fix types on every table in the feed
    gtfs_type_cleanup.fix(master_feed)

    # This is Amtrak-specific
    fix_known_errors(master_feed)
    return master_feed

def fix_known_errors(feed):
    """
    Change the feed in place to fix known errors.
    """
    # Cardinal 1051 (DST switch date) with wrong direction ID

    # There's an error in the trips. Attempt to fix it.
    # THIS WORKS for fixing errors in a feed.  REMEMBER IT.
    # Revised for PANDAS 1.4.
    my_trips = feed.trips

    debug_print(2, my_trips[my_trips["trip_short_name"] == "1051"] )
    my_trips.loc[my_trips["trip_short_name"] == "1051","direction_id"] = 0
    debug_print(2, my_trips[my_trips["trip_short_name"] == "1051"] )

    # Error fixed.  Put back into the feed.
    feed.trips = my_trips
    return
