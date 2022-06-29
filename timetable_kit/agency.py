#! /usr/bin/env python3
# agency.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Hooks for agency-specific data.

Currently the only specific agency is Amtrak, which has its own submodule

However, this contains generic code which should be used for agencies which are not Amtrak
"""

import gtfs_kit

class Agency:
    """
    Contains agency-specific calls.

    Default implementation gets info from the GTFS.
    """

    # Instance attributes:
    # stop_name_dict

    def __init__(self, feed: gtfs_kit.Feed):
        stops = feed.stops
        self.stop_name_dict = dict(zip(stops["stop_id"],stops["stop_name"]))

    def get_stop_name(self, stop_id: str) -> str:
        """ Given a stop_id, returns a stop_name from GTFS """
        return self.stop_name_dict[stop_id];

if __name__ == "__main__":
    from timetable_kit.initialize import initialize_feed
    gtfs_filename = "/home/neroden/programming/timetable_kit/timetable_kit/amtrak/GTFS.zip"
    master_feed = initialize_feed(gtfs=gtfs_filename)
    my_agency = Agency(master_feed)
    print( my_agency.get_stop_name("ALB") )
