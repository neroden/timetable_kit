# amtrak/gtfs_cleanup.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Patch known errors in Amtrak GTFS.

This should be reviewed every time Amtrak releases a new GTFS.
"""

# TODO: all the Amtrak-specific stuff needs to be made object oriented in an "Amtrak object" perhaps

from timetable_kit import feed_enhanced
from timetable_kit.debug import debug_print

def patch_feed(feed):
    """
    Take an Amtrak feed and patch it for known errors.

    Return another feed.
    """

    new_feed = feed.copy()
    new_calendar = new_feed.calendar

    # Coast Starlight: bogus Saturday calendar,
    # and everything-but-Saturday calendar which is the same

    # First find the route id:
    for index in new_feed.routes.index:
        if new_feed.routes.loc[index, "route_long_name"] == "Coast Starlight":
            cs_route_id = new_feed.routes.loc[index, "route_id"]
            break
    debug_print(1, "Coast Starlight route_id: ", cs_route_id)
    # Then find the service ids:
    service_ids = set()
    for index in new_feed.trips.index:
        if new_feed.trips.loc[index, "route_id"] == cs_route_id:
            service_ids.add(new_feed.trips.loc[index,"service_id"])
    # Now cycle through the calendars.
    # First find and drop the bogus Saturday calendar:
    # Now find and drop the bogus Saturday calendar:
    for index in new_calendar.index:
        if new_calendar.loc[index, "service_id"] in service_ids: # Coast Starlight
            if new_calendar.loc[index, "monday"] == 0: # Not on Monday
                if new_calendar.loc[index, "saturday"] == 1: # On Saturday
                    new_calendar = new_calendar.drop(labels=[index], axis="index")
                    debug_print(1, "Patched saturday special out of Coast Starlight"),
                    break
    for index in new_calendar.index:
        # Now patch the everything-but-Saturday calendar to be every-day-of-the-week:
        # (This is the good calendar)
        if new_calendar.loc[index, "service_id"] in service_ids: # Coast Starlight
            if new_calendar.loc[index, "saturday"] == 0: # Not on Saturday
                new_calendar.loc[index, "saturday"] = 1
                debug_print(1, "Patched saturday into Coast Starlight general")
                break

    # And update with the new calendar, just in case it hadn't
    new_feed.calendar = new_calendar

    # Toronto: incorrectly listed as "no pickups" in stop one.
    new_stop_times = new_feed.stop_times
    for index in new_stop_times.index:
        if new_stop_times.loc[index, "stop_id"] == "TWO":
            if new_stop_times.loc[index, "stop_sequence"] == 1:
                new_stop_times.loc[index, "pickup_type"] = 0
                debug_print(1, "Found Toronto in position 1: patched pickup_type")
            if new_stop_times.loc[index, "stop_sequence"] in [19, 20]:
                new_stop_times.loc[index, "drop_off_type"] = 0
                debug_print(1, "Found Toronto in position 19 or 20: patched drop_off_type")

    # Update with new stop times
    new_feed.stop_times = new_stop_times

    return new_feed
