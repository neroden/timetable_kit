# via/gtfs_patches.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Patch known errors in VIA GTFS.

This should be reviewed every time VIA releases a new GTFS.
"""

from timetable_kit.debug import debug_print
from timetable_kit.feed_enhanced import FeedEnhanced


def patch_feed(feed: FeedEnhanced) -> FeedEnhanced:
    """
    Take an VIA feed and patch it for known errors.

    Return another feed.
    """

    new_feed = feed.copy()

    # Wheelchair access for VIA:
    # VIA uses "0" way too often: consider changing it to "2" (no access)
    new_stops = new_feed.stops
    for index in new_stops.index:
        # PARE has been fixed on 2023-01-19 !
        # if new_stops.loc[index, "stop_code"] == "PARE":
        # Parent (PARE) station on Jonquiere line is listed as wheelchair accessible
        # because the platform is accessible,
        # but VIA's station info says it's not possible to board the train in a wheelchair.
        # Oh come on, VIA.
        #    new_stops.loc[index, "wheelchair_boarding"] = 0
        #    debug_print(1, "Patched stop PARE"),
        if new_stops.loc[index, "stop_code"] == "CHUR":
            # Note that Churchill may have the same problem as Parent (unclear).
            debug_print(1, "Warning, Churchill wheelchair status questionable")
        # We have checked VIA's website: Thompson really has a wheelchair lift (as does Winnipeg).
        # We have checked VIA's website: Prince George, Prince Rupert, & Terrace really have wheelchair lifts.

    # And update with revised stops table
    new_feed.stops = new_stops

    return new_feed
