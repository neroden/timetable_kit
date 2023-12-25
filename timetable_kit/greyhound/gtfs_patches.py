# greyhound/gtfs_patches.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Patch known issues with Greyhound GTFS.

The big problem is that Greyhound doesn't have trip_short_name set -- at all. This
breaks the entire architecture of timetable_kit, so we set it.
"""
from timetable_kit.debug import debug_print
from timetable_kit.feed_enhanced import FeedEnhanced


def patch_feed(feed: FeedEnhanced) -> FeedEnhanced:
    """Take an Greyhound feed and patch it to be usable by timetable_kit.

    Return the new patched feed.
    """

    new_feed = feed.copy()
    assert new_feed.trips is not None  # Silence MyPy

    # Greyhound has no trip_short_name.
    new_trips = new_feed.trips
    debug_print(1, "Patching in trip_short_name values")
    # Fill in the trip short name from the trip_id to make this usable
    new_trips["trip_short_name"] = new_trips["trip_id"]
    debug_print(1, new_trips)

    # Unfortunately, the trip_id values are pretty hard to use too.
    # Ideally we'd patch in a more user-friendly trip_short_name,
    # probably based on the route_short_name with a distinguishing suffix
    # based on first departure time?
    # TODO.

    # And copy it back into the feed
    new_feed.trips = new_trips

    return new_feed
