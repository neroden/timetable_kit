# generic_agency/agency.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.generic_agency.agency module

This holds a class for "Agency" intended to be used as a singleton.
It has an interface; Amtrak and others need to provide the same interface.
This should be made easier by class inheritance.
"""
from __future__ import annotations

from timetable_kit.feed_enhanced import FeedEnhanced
from timetable_kit.debug import debug_print


# Intended to be used both directly and by subclasses
class Agency:
    """Agency-specific code for interpreting specs and GTFS feeds for a generic agency"""

    def __init__(
        self: Agency,
    ) -> None:
        self.feed = None

    def init_from_feed(self, feed: FeedEnhanced):
        """Initalize certain agency tables from a GTFS feed.  Used for translating stop_code to and from stop_id."""
        """We don't want to do this at object creation for multiple reasons."""
        """1. We need to call agency routines on the feed before using it."""
        """2. We may not need to use this agency object at all, but it may need to be created in initialization."""
        """3. We may not need to initialize these tables in subclasses."""
        """4. This is expensive in both memory usage and time."""
        # Query whether this should be based on FeedEnhanced or on basic Feed.
        if self.feed is not None:
            debug_print(
                1,
                "Warning: resetting feed on agency when it has already been set once: this is discouraged",
            )
        self.feed = feed


# Establish the singleton
_singleton = Agency()


def get_singleton():
    """Get singleton for generic agency"""
    global _singleton
    return _singleton
