# tsn.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Routines to convert between trip_id and trip_short_name.

In GTFS, trip_id is unique.  So a trip_id to trip_short_name map should be, too.
However, trip_short_name isn't unique.  But it is unique on a given calendar day,
so it should be possible to make a map from a restricted feed.

Also contains other routines which look up trips by tsn.
"""
from timetable_kit.errors import (GTFSError, NoTripError)
from timetable_kit.debug import debug_print

# This one monkey-patches gk.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

def make_trip_id_to_tsn_dict(feed):
    """
    Make and return a dict mapping from trip_id to trip_short_name.
    """
    trip_ids = feed.trips["trip_id"].array

    # the following should be used only when debugging; it's slow:
    # if len(trip_ids) != len(set(trip_ids)):
    #    # There's a duplicate!  Run away screaming!
    #    raise GTFSError("Duplicate trip_id found!")

    tsns = feed.trips["trip_short_name"].array
    trip_id_to_tsn = dict(zip(trip_ids, tsns))
    return trip_id_to_tsn

def make_tsn_to_trip_id_dict(feed):
    """
    Make and return a dict mapping from trip_short_name to trip_id.

    The feed must be filtered down to where this is unique.

    If there are duplicates, the *last* one will be chosen.

    This isn't ideal but deals with an Amtrak data problem where
    multiple completely-identical entries are present in GTFS.
    (So it doesn't matter which one we pick.)
    """

    tsns = feed.trips["trip_short_name"].array

    # Here, duplicates are likely so we should check every time.
    # This is slow-ish, but tells us which train gave us the dupe.
    tsn_set = set()
    for x in tsns:
        if x in tsn_set:
            # raise GTFSError("Duplicate trip_short_name found for ", x)
            debug_print(1, "Duplicate tsn found for", x)
        else:
            tsn_set.add(x)

    trip_ids = feed.trips["trip_id"].array
    # We have duplicates and will take the last one.
    # but hopefully they're total duplicates so it doesn't matter...
    tsn_to_trip_id = dict(zip(tsns, trip_ids))
    return tsn_to_trip_id

def find_tsn_dupes(feed):
    """
    Find trip_short_names which have multiple trip_ids.

    The calendar means that on a master feed this will happen with almost everything.
    Once you filter to a single day, there's a lot fewer.

    There's a fairly short list where the same train number has different trips on different days:
    ( Currently:
    79, 80, 1079, 20, 662, 88, 162, 89, 719,
    350, 351, 352, 353, 354, 355,
    6048, 6049, 6089, 6093, 6189, 6193,
    8721, 8722, 8821, 8822, 8748, 8205,
    8010, 8011, 8012, 8013, 8014, 8015, 8033,
    8042, 7203, )

    Then there's a list of Amtrak trains with GTFS errors, meaning actual duplicates.
    ( Currently:
    364, 365, 3911, 3915, 8040, 8041, 8671, )

    This will probably change in future GTFS feeds, so this finds these.
    """
    tsns = feed.trips["trip_short_name"].array

    # Here, duplicates are likely so we should check every time.
    # This is slow-ish, but tells us which train gave us the dupe.
    debug_print(1, "Finding duplicates, if any:")
    tsn_set = set()
    for x in tsns:
        if x in tsn_set:
            debug_print(1, "Duplicate tsn found for", x)
        else:
            tsn_set.add(x)
    return

### These two are used routinely in the main timetable generator
### And in the stations list generator

def trip_from_tsn(today_feed, trip_short_name):
    """
    Given a single train number (trip_short_name), and a feed containing only one day, produces the trip record.

    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)
    """
    single_trip_feed = today_feed.filter_by_trip_short_names([trip_short_name])
    try:
        this_trip_today = single_trip_feed.get_single_trip() # Raises errors if not exactly one trip
    except NoTripError:
        print ("Found no trips for ", trip_short_name)
        raise
    return this_trip_today

def stations_list_from_tsn(today_feed, trip_short_name):
    """
    Given a single train number (trip_short_name), and a feed containing only one day, produces a dataframe with a stations list -- IN THE RIGHT ORDER.

    Produces a station list dataframe.
    This is used in augment_tt_spec, and via the "stations" command.

    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)
    """

    trip_id = trip_from_tsn(today_feed, trip_short_name).trip_id

    sorted_stop_times = today_feed.get_single_trip_stop_times(trip_id)
    sorted_station_list = sorted_stop_times['stop_id']
    debug_print(3, sorted_station_list)
    return sorted_station_list

