# amtrak/gtfs_cleanup.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Patch known errors in Amtrak GTFS.

This should be reviewed every time Amtrak releases a new GTFS.
"""

# TODO: all the Amtrak-specific stuff needs to be made object oriented in an "Amtrak object" perhaps

from timetable_kit import feed_enhanced


def patch_feed(feed):
    """
    Take an Amtrak feed and patch it for known errors.

    Return another feed.
    """
    new_feed = feed.copy()
    new_calendar = new_feed.calendar

    # Coast Starlight: bogus Saturday calendar,
    # and everything-but-Saturday calendar which is the same
    for index in new_calendar.index:
        # First patch the everything-but-Saturday calendar to be every-day-of-the-week:
        # (This is the good calendar)
        if new_calendar.loc[index, "service_id"] == "2841905":
            new_calendar.loc[index, "saturday"] = 1
            break
    # Now find and drop the bogus Saturday calendar:
    for index in new_calendar.index:
        if new_calendar.loc[index, "service_id"] == "2841906":
            new_calendar = new_calendar.drop(labels=[index], axis="index")
            break

    # And update with the new calendar, just in case it hadn't
    new_feed.calendar = new_calendar
    return new_feed
