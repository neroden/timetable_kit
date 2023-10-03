#! /usr/bin/env python3
# genric_agency.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Hooks for agency-specific data.

Currently, the only specific agency is Amtrak, which has its own submodule

However, this contains generic code which should be used for agencies which are not Amtrak

This is unused, obsolete and will be deleted later.
"""

import gtfs_kit
import timetable_kit.amtrak as amtrak


class Agency:
    """
    Contains agency-specific calls.

    Default implementation gets info from the GTFS.
    """

    # Instance attributes:
    # stop_name_dict

    def __init__(self, feed: gtfs_kit.Feed):
        self.stop_name_dict = dict(zip(feed.stops["stop_id"], feed.stops["stop_name"]))
        self.route_name_dict = dict(
            zip(feed.routes["route_id"], feed.routes["route_long_name"])
        )

    def get_station_name_pretty(
        self, stop_id: str, doing_multiline_text=False, doing_html=False
    ) -> str:
        """Given a stop_id, returns a stop_name from GTFS, with possible prettyprinting"""
        raw_name = self.stop_name_dict[stop_id]
        # FIXME -- need to do the prettyprinting
        return raw_name

    def get_route_name(self, route_id: str) -> str:
        """Given a route_id, return a route_long_name from GTFS"""
        return self.route_name_dict[route_id]

    def is_major_station(self, stop_id: str) -> bool:
        """Is this a major station?  Default implementation: no major stations"""
        return False


if __name__ == "__main__":
    from timetable_kit.initialize import initialize_feed

    gtfs_filename = (
        "/home/neroden/programming/timetable_kit/timetable_kit/amtrak/GTFS.zip"
    )
    master_feed = initialize_feed(gtfs=gtfs_filename)
    my_agency = Agency(master_feed)
    print(my_agency.get_stop_name("ALB"))
    # This works but is ugly / undesirable
    my_agency.get_station_name_pretty = amtrak.get_station_name_pretty
    print(my_agency.get_station_name_pretty("ALB"))
    print(my_agency.get_station_name_pretty("ALB", doing_multiline_text=True))
    print(my_agency.get_station_name_pretty("ALB", doing_html=True))
