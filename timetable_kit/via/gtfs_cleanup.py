# via/gtfs_cleanup.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Patch known errors in VIA GTFS.

This should be reviewed every time VIA releases a new GTFS.
"""

from timetable_kit import feed_enhanced
from timetable_kit.debug import debug_print


def patch_feed(feed):
    """
    Take an VIA feed and patch it for known errors.

    Return another feed.
    """

    new_feed = feed.copy()
    new_stops = new_feed.stops
    for index in new_stops.index:
        if new_stops.loc[index, "stop_code"] == "PARE":
            # Parent (PARE) station on Jonquiere line is listed as wheelchair accessible
            # because the platform is accessible,
            # but VIA's station info says it's not possible to board the train in a wheelchair.
            # Oh come on, VIA.
            new_stops.loc[index, "wheelchair_boarding"] = 0
            debug_print(1, "Patched stop PARE"),

    # And update with revised stops table
    new_feed.stops = new_stops

    return new_feed
