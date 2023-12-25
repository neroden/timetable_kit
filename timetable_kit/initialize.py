# initialize.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Initialize the GTFS feed and related stuff.

Used by multiple command-line programs
"""

# Other people's packages
from pathlib import Path
import datetime

import gtfs_kit  # type: ignore # Tell MyPy this has no type stubs


# My packages: Local module imports


from timetable_kit import gtfs_type_cleanup
from timetable_kit.debug import debug_print
from timetable_kit.feed_enhanced import FeedEnhanced, GTFS_DAYS

# For the Agency singleton
from timetable_kit.runtime_config import agency_singleton as agency_singleton


# INITIALIZATION CODE
def initialize_feed(gtfs, patch_the_feed: bool = True) -> FeedEnhanced:
    """Initialize the master_feed and related variables.

    Does some cleaning, and removal of the large shapes table which we don't use.

    Also does agency-specific patching -- optionally.

    Also initializes the agency singleton from the feed *after* that.
    NOTE, this is a side-effect, not great coding style, FIXME

    gtfs: may be a filename or a Path.
    """

    debug_print(1, "Using GTFS file " + str(gtfs))
    gtfs_path = Path(gtfs)
    # The unit is only relevant if we read the shapes file; we currently don't.
    # Also affects display miles so default to "mi".
    plain_feed = gtfs_kit.read_feed(gtfs_path, dist_units="mi")
    debug_print(1, "Feed loaded")

    # Need to clean up times to zero-pad them for sorting.
    plain_feed = FeedEnhanced.clean_times(plain_feed)

    # Don't waste time.
    # plain_feed.validate()

    # Fix types on every table in the feed
    # Also deals with blank entries (NaNs) correctly
    # Particularly tricky on timepoint, which defaults to 1
    gtfs_type_cleanup.fix(plain_feed)
    debug_print(1, "Feed initialized")

    # Type-convert to FeedEnhanced (blowing away shapes data)
    master_feed = FeedEnhanced.enhance(plain_feed)

    # Patch the feed in an agency-specific fashion.
    if patch_the_feed:
        master_feed = agency_singleton().patch_feed(master_feed)
        debug_print(1, "Feed patched, hopefully")
    else:
        # Have to patch in the wheelchair access info regardless
        master_feed = agency_singleton().patch_feed_wheelchair_access_only(master_feed)
        debug_print(1, "Feed patched for wheelchair access only")

    # Initialize the singleton from the feed
    # (This has side-effects, note, not pass-by-value semantics)
    agency_singleton().init_from_feed(master_feed)

    return master_feed


def filter_feed_for_utilities(
    feed: FeedEnhanced, reference_date=None, day_of_week=None
):
    """Filter the feed down based on command line arguments, for the auxiliary
    utility programs such as list_trains.py and list_stations.py.

    Returns a new, filtered feed.

    day_of_week is as given in command line argument --day: either a GTFS day,
    "weekend", or "weekday"
    """
    if reference_date is None:
        reference_date = datetime.date.today().strftime("%Y%m%d")
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")
    today_feed = feed.filter_by_dates(reference_date, reference_date)

    # Restrict by day(s) of week if specified.
    match day_of_week:
        case "weekday":
            days_list = ["monday", "tuesday", "wednesday", "thursday", "friday"]
            debug_print(1, "Restricting to weekdays.")
            today_feed = today_feed.filter_by_days_of_week(days_list)
        case "weekend":
            days_list = ["saturday", "sunday"]
            debug_print(1, "Restricting to weekends.")
            today_feed = today_feed.filter_by_days_of_week(days_list)
        case None:
            # No filtering necessary
            pass
        case _:
            if day_of_week not in GTFS_DAYS:
                print("Specified day of week not understood.")
                exit(1)
            debug_print(1, "Restricting to ", day_of_week, ".", sep="")
            today_feed = today_feed.filter_by_day_of_week(day_of_week)

    return today_feed
