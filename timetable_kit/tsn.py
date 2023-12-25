# tsn.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Routines to convert between trip_id and trip_short_name.

In GTFS, trip_id is unique.  So a trip_id to trip_short_name map should
be, too. However, trip_short_name isn't unique.  But it is usually
unique on a given calendar day, so it should be possible to make a map
from a restricted feed.

Unfortunately, the same trip_short_name can have different schedules on
different days of the week.  So we may need to map for days of the week
as well.

Also contains other routines which look up trips by tsn.
"""
from timetable_kit.errors import NoTripError
from timetable_kit.debug import debug_print
from timetable_kit.runtime_config import agency
from timetable_kit.runtime_config import agency_singleton

# import gtfs_kit

# List of days which are GTFS column headers
from timetable_kit.feed_enhanced import GTFS_DAYS, FeedEnhanced


def train_spec_to_tsn(train_spec: str) -> str:
    """Takes a train_spec, and returns the tsn alone.

    A train_spec is either a tsn or a tsn followed by a space and a day
    of the week, possibly followed by "noheader".
    """
    train_spec = train_spec.removesuffix("noheader").strip()
    for day in GTFS_DAYS:
        tentative_tsn = train_spec.removesuffix(" " + day)
        if tentative_tsn != train_spec:
            # Only remove one suffix!
            return tentative_tsn
    # No suffixes found
    return train_spec


def make_trip_id_to_tsn_dict(feed: FeedEnhanced) -> dict[str, str]:
    """Make and return a dict mapping from trip_id to trip_short_name."""
    assert feed.trips is not None  # Silence MyPy
    trip_ids = feed.trips["trip_id"].array

    # the following should be used only when debugging; it's slow:
    # if len(trip_ids) != len(set(trip_ids)):
    #    # There's a duplicate!  Run away screaming!
    #    raise GTFSError("Duplicate trip_id found!")

    tsns = feed.trips["trip_short_name"].array
    trip_id_to_tsn = dict(zip(trip_ids, tsns))
    return trip_id_to_tsn


def make_tsn_to_trip_id_dict(feed: FeedEnhanced) -> dict[str, str]:
    """Make and return a dict mapping from trip_short_name to trip_id.

    The feed should be filtered down to where this is unique.

    If there are duplicates, the *last* one will be chosen.

    This isn't ideal but deals with an Amtrak data problem where
    multiple completely-identical entries are present in GTFS. (So it
    doesn't matter which one we pick.)
    """
    assert feed.trips is not None  # Silence MyPy
    tsns = feed.trips["trip_short_name"].array

    # Here, duplicates are likely, so we should check every time.
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
    # but hopefully they're total duplicates, so it doesn't matter...
    tsn_to_trip_id = dict(zip(tsns, trip_ids))
    return tsn_to_trip_id


def make_tsn_and_day_to_trip_id_dict(feed: FeedEnhanced) -> dict[str, str]:
    """Make and return a dict mapping from trip_short_name + " " + day_of_week
    to trip_id.

    The feed should be filtered down to where this is unique.

    This is designed for situations where a single tsn has different
    schedules on different days of the week.  Annoying, and bad
    practice, but allowed by GTFS.
    """
    total_dict = dict()
    # tsns = feed.trips["trip_short_name"].array
    for day in GTFS_DAYS:
        day_suffix = " " + day
        # We need to filter calendar and trips for the day of the week.
        # This filters stop_times too, which is overkill;
        # if it's slow, try not doing that.
        day_feed = feed.filter_by_day_of_week(day)
        assert day_feed.trips is not None  # Silence MyPy

        # Collect the tsns (eg "91")...
        tsns = day_feed.trips["trip_short_name"].array
        # This is slow-ish, but tells us which train gave us the dupe.
        tsn_set = set()
        for x in tsns:
            if x in tsn_set:
                # raise GTFSError("Duplicate trip_short_name found for ", x)
                debug_print(1, "Duplicate tsn found for", x, "on", day)
            else:
                tsn_set.add(x)

        # Now, preserving order, prep the indices (eg "91 monday"):
        suffixed_tsns = [tsn + day_suffix for tsn in tsns]
        # And prep the trip_ids:
        trip_ids = day_feed.trips["trip_id"].array
        # And zip it up:
        tsn_to_trip_id = dict(zip(suffixed_tsns, trip_ids))
        # Then add to the larger dict:
        total_dict.update(tsn_to_trip_id)
    return total_dict


def find_tsn_dupes(feed: FeedEnhanced) -> set[str]:
    """Find trip_short_names which have multiple trip_ids.  Returns the set of
    duplicate tsns.

    The calendar means that on a master feed this will happen with
    almost everything. Once you filter to a single day, there's a lot
    fewer.

    There's a fairly short list where the same train number has
    different trips on different days: ( Currently: 79, 80, 1079, 20,
    662, 88, 162, 89, 719, 350, 351, 352, 353, 354, 355, 6048, 6049,
    6089, 6093, 6189, 6193, 8721, 8722, 8821, 8822, 8748, 8205, 8010,
    8011, 8012, 8013, 8014, 8015, 8033, 8042, 7203, )

    Then there's a list of Amtrak trains with GTFS errors, meaning
    actual duplicates. ( Currently: 364, 365, 3911, 3915, 8040, 8041,
    8671, )

    This will probably change in future GTFS feeds, so this finds these.
    """
    assert feed.trips is not None  # Silence MyPy
    tsns = feed.trips["trip_short_name"].array

    # Here, duplicates are likely, so we should check every time.
    # This is slow-ish, but tells us which train gave us the dupe.
    debug_print(1, "Finding duplicate tsns, if any:")

    # Accumulate tsns which are found in the tsns array
    tsn_set = set()
    # Accumulate tsns which are found in the tsns array *twice*
    tsn_dupes_set = set()
    for x in tsns:
        if x in tsn_set:
            debug_print(1, "Duplicate tsn found for", x)
            tsn_dupes_set.add(x)
        else:
            tsn_set.add(x)
    return tsn_dupes_set


# These two are used routinely in the main timetable generator
# And in the stations list generator


def trip_from_tsn(today_feed: FeedEnhanced, trip_short_name):
    """Given a single train number (trip_short_name), and a feed containing
    only one day, produces the trip record.

    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)

    The naive (i.e. current) implementation of this takes nearly the
    entire program runtime. Avoid using this.  Do the work another way.
    See trip_from_tsn_local in timetable.py

    This is still used in stations_list_from_tsn, however.
    """
    single_trip_feed = today_feed.filter_by_trip_short_names([trip_short_name])
    try:
        this_trip_today = (
            single_trip_feed.get_single_trip()
        )  # Raises errors if not exactly one trip
    except NoTripError:
        print("Found no trips for ", trip_short_name)
        raise
    return this_trip_today


def stations_list_from_trip_id(today_feed: FeedEnhanced, trip_id):
    """Given a trip_id, produces a dataframe with a stations list -- IN THE
    RIGHT ORDER.

    Produces a station list dataframe. This variant is used to implement
    "origin" and "destination".
    """
    # Cannot be put into feed_enhanced due to the reliance on agency_singleton().  FIXME?

    sorted_stop_times = today_feed.get_single_trip_stop_times(trip_id)  # Sorted.
    # For VIA rail, the stop_id is not the same as the stop_code.
    # Add the stop_code.  (For Amtrak, this is a no-op)
    sorted_stop_times["stop_code"] = sorted_stop_times["stop_id"].apply(
        agency_singleton().stop_id_to_stop_code
    )

    debug_print(3, sorted_stop_times)
    sorted_stop_codes = sorted_stop_times["stop_code"]
    return sorted_stop_codes


def stations_list_from_tsn(today_feed: FeedEnhanced, trip_short_name):
    """Given a single train number (trip_short_name), and a feed containing
    only one day, produces a dataframe with a stations list -- IN THE RIGHT
    ORDER.

    Produces a station list dataframe. This is used in augment_tt_spec,
    and via the "stations" command.

    Raises an error if trip_short_name generates more than one trip
    (probably because the feed has multiple dates in it)
    """

    trip_id = trip_from_tsn(today_feed, trip_short_name).trip_id

    return stations_list_from_trip_id(today_feed, trip_id)
