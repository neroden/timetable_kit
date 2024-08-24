# initialize.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Initialize the GTFS feed and related stuff.

Used by multiple command-line programs
"""

# Other people's packages
from pathlib import Path

import gtfs_kit  # type: ignore # Tell MyPy this has no type stubs

# My packages: Local module imports
from timetable_kit import gtfs_type_cleanup
from timetable_kit.debug import debug_print
from timetable_kit.feed_enhanced import FeedEnhanced

# For the Agency singleton
from timetable_kit.timetable_class import TTConfig


# INITIALIZATION CODE
def initialize_feed(config: TTConfig) -> FeedEnhanced:
    """Initialize the master_feed and related variables.

    Does some cleaning, and removal of the large shapes table which we don't use.

    Also does agency-specific patching -- optionally.

    Also initializes the agency singleton from the feed *after* that.
    NOTE, this is a side effect, not great coding style, FIXME

    config: TTConfig instance for configuring output
    """

    debug_print(1, "Using GTFS file " + str(config.gtfs_filename))
    gtfs_path = Path(config.gtfs_filename)
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
    if config.patch_the_feed:
        master_feed = config.agency.patch_feed(master_feed)
        debug_print(1, "Feed patched, hopefully")
    else:
        # Have to patch in the wheelchair access info regardless
        master_feed = config.agency.patch_feed_wheelchair_access_only(master_feed)
        debug_print(1, "Feed patched for wheelchair access only")

    # Initialize the singleton from the feed
    # (This has side effects, note, not pass-by-value semantics)
    config.agency.init_from_feed(master_feed)

    return master_feed
