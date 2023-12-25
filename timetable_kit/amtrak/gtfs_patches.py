# amtrak/gtfs_patches.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Patch known errors in Amtrak GTFS.

This should be reviewed every time Amtrak releases a new GTFS.
"""
# TODO: all the Amtrak-specific stuff needs to be made object oriented in an "Amtrak object" perhaps

from timetable_kit.debug import debug_print
from timetable_kit.feed_enhanced import FeedEnhanced

# Add the wheelchair boarding information from JSON into the GTFS
from timetable_kit.amtrak.access import patch_add_wheelchair_boarding

arizona_stops_list = [
    # Sunset Limited
    "YUM",  # Yuma
    "TUS",  # Tucson
    "MRC",  # Maricopa
    "BEN",  # Benson
    # Southwest Chief
    "WLO",  # Winslow
    "FLG",  # Flagstaff
    "KNG",  # Kingman
    # Grand Canyon stuff
    "WMH",  # Williams Holiday Inn
    "WMA",  # Williams Grand Canyon Railroad
    "TSY",  # Tusayan / Grand Canyon Village
    "GCB",  # Grand Canyon Village / Maswik Lodge
    "GCN",  # Grand Canyon Grand Canyon Railroad
]


def patch_arizona(feed: FeedEnhanced):
    """Patch for Arizona timezone problems.

    Fix feed in place.
    """
    assert feed.stops is not None  # Silence MyPy
    stops = feed.stops
    for index in stops.index:
        if stops.loc[index, "stop_id"] in arizona_stops_list:
            if stops.loc[index, "stop_timezone"] == "America/Denver":
                stops.loc[index, "stop_timezone"] = "America/Phoenix"
                debug_print(
                    1,
                    "Found Arizona station with wrong timezone: patched stop_timezone",
                )
    # Patch feed in place
    feed.stops = stops
    return


train_agencies = [
    "Grand Canyon Railway",  # 44 -- in routes.txt as Thruway Connecting
    "Altamont Corridor Express",  # 99 -- in routes.txt as Thruway Connecting
    "Shore Line East",  # 1230 -- in routes.txt as Commuter Rail
    "Placeholder train number for CTrail",  # 1234 -- in routes.txt as Thruway Connecting
    "Virginia Railway Express",  # 1237 -- in routes.txt as Commuter Rail
    "MARC",  # 1238 -- in routes.txt as Commuter Rail
]


def patch_buses(feed: FeedEnhanced):
    """Bus services incorrectly listed as trains.

    Fix feed in place
    """
    assert feed.routes is not None  # Silence MyPy
    assert feed.agency is not None  # Silence MyPy
    routes = feed.routes
    for index in routes.index:
        if routes.loc[index, "route_long_name"] == "Amtrak Thruway Connecting Service":
            if routes.loc[index, "route_type"] == 2:
                # Supposed train.  Is it really?
                agency_id = routes.loc[index, "agency_id"]
                agency_name = feed.agency.loc[
                    feed.agency["agency_id"] == agency_id, "agency_name"
                ].item()
                if agency_name in train_agencies:
                    # we're good
                    pass
                else:
                    debug_print(
                        1, "Patched bus route listed as train for: " + agency_name
                    )
                    routes.loc[index, "route_type"] = 3
    feed.routes = routes


def patch_coast_starlight(feed: FeedEnhanced):
    """Patch an old Coast Starlight bug.

    The bug appears to be fixed as of July 7, 2023, So this is unused code now
    """
    assert feed.routes is not None  # Silence MyPy
    assert feed.trips is not None  # Silence MyPy
    assert feed.calendar is not None  # Silence MyPy
    # Coast Starlight fix
    new_calendar = feed.calendar
    # Coast Starlight: two bogus errors!
    # 11 is missing Saturday and has two other identical calendars;
    # 14 has three identical calendars

    # First find the route id:
    for index in feed.routes.index:
        if feed.routes.loc[index, "route_long_name"] == "Coast Starlight":
            cs_route_id = feed.routes.loc[index, "route_id"]
            break
    debug_print(1, "Coast Starlight route_id: ", cs_route_id)
    # Then find the service ids:
    service_ids = set()
    for index in feed.trips.index:
        if feed.trips.loc[index, "route_id"] == cs_route_id:
            service_ids.add(feed.trips.loc[index, "service_id"])
    # Now cycle through the calendars.
    # First find and drop the bogus calendars:
    for index in new_calendar.index:
        if new_calendar.loc[index, "service_id"] in service_ids:  # Coast Starlight
            if new_calendar.loc[index, "wednesday"] == 0:  # Not on Wednesday
                new_calendar = new_calendar.drop(labels=[index], axis="index")
                debug_print(
                    1, "Patched not-on-wednesday special out of Coast Starlight"
                ),
    for index in new_calendar.index:
        # Now patch the Wednesday calendars to be every-day-of-the-week:
        # (This is the good calendar)
        if new_calendar.loc[index, "service_id"] in service_ids:  # Coast Starlight
            new_calendar.loc[index, "sunday"] = 1
            new_calendar.loc[index, "monday"] = 1
            new_calendar.loc[index, "tuesday"] = 1
            new_calendar.loc[index, "wednesday"] = 1
            new_calendar.loc[index, "thursday"] = 1
            new_calendar.loc[index, "friday"] = 1
            new_calendar.loc[index, "saturday"] = 1
            debug_print(1, "Patched full week into Coast Starlight calendar")

    # And update with the new calendar, just in case it hadn't
    feed.calendar = new_calendar


def patch_toronto(feed: FeedEnhanced):
    """
    Toronto: has "no pickups" / "no dropoffs" mixed up.

    Patch feed in place.
    """
    assert feed.stop_times is not None  # Silence MyPy
    # Toronto: incorrectly listed as "no pickups" in stop one.
    new_stop_times = feed.stop_times
    for index in new_stop_times.index:
        if new_stop_times.loc[index, "stop_id"] == "TWO":
            if new_stop_times.loc[index, "stop_sequence"] == 1:
                new_stop_times.loc[index, "pickup_type"] = 0
                debug_print(1, "Found Toronto in position 1: patched pickup_type")
            if new_stop_times.loc[index, "stop_sequence"] in [19, 20]:
                new_stop_times.loc[index, "drop_off_type"] = 0
                debug_print(
                    1, "Found Toronto in position 19 or 20: patched drop_off_type"
                )
    # Update with new stop times
    feed.stop_times = new_stop_times


def patch_cardinal_direction(feed: FeedEnhanced):
    """Patch Cardinal #1051 (DST switch date) with wrong direction ID.

    Patch feed in place. Unused since we don't care about direction.
    """
    assert feed.trips is not None  # Silence MyPy
    my_trips = feed.trips
    debug_print(1, "Patching Cardinal #1051 direction")
    my_trips.loc[my_trips["trip_short_name"] == "1051", "direction_id"] = 0
    # Update with new trips data
    feed.trips = my_trips


def patch_feed(feed: FeedEnhanced):
    """Take an Amtrak feed and patch it for known errors.

    Return another feed.
    """

    new_feed = feed.copy()

    # Arizona time zone problems
    patch_arizona(new_feed)

    # Buses listed as trains fixes
    patch_buses(new_feed)

    # Toronto pickup-only / dropoff-only problem
    patch_toronto(new_feed)

    # Patch accessibility information into GTFS
    patch_add_wheelchair_boarding(new_feed)

    return new_feed
