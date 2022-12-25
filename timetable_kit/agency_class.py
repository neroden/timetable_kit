#! /usr/bin/env python3
# genric_agency.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Hooks for agency-specific data.

Currently the only specific agency is Amtrak, which has its own submodule

However, this contains generic code which should be used for agencies which are not Amtrak
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

    def get_stop_name(
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

    def station_has_checked_baggage(self, stop_id: str) -> bool:
        """Does this station have checked baggage?  Default implemention: no station does"""
        return False

    def train_has_checked_baggage(self, tsn: str) -> bool:
        """Does this trip_short_name carry checked baggage?  Default implementation: no"""
        return False

    def station_has_inaccessible_platform(self, stop_id: str) -> bool:
        """Does this station have an explicitly inaccessible platform?  Default implementation: no"""
        # FIXME: pull from GTFS
        return False

    def station_has_accessible_platform(self, stop_id: str) -> bool:
        """Does this station have an explicitly accessible platform?  Default implementation: no"""
        # FIXME: pull from GTFS
        return False

    def is_connecting_service(self, tsn: str) -> bool:
        """Is this trip_short_name a connecting service?  Default implementation: no"""
        return False

    def is_sleeper_train(self, tsn: str) -> bool:
        """Is this trip_short_name a sleeper train?  Default implementation: no"""
        return False

def amtrak_get_stop_name (
        stop_id: str, doing_multiline_text=False, doing_html=False
    ) -> str:
        raw_stop_name = amtrak.get_station_name(stop_id)
        major = amtrak.is_standard_major_station(stop_id)
        if doing_html:
            cooked_stop_name=amtrak.station_name_to_html(raw_stop_name, major)
        elif doing_multiline_text:
            cooked_stop_name=amtrak.station_name_to_multiline_text(raw_stop_name, major)
        else:
            cooked_stop_name=amtrak.station_name_to_single_line_text(raw_stop_name, major)
        return cooked_stop_name

if __name__ == "__main__":
    from timetable_kit.initialize import initialize_feed

    gtfs_filename = (
        "/home/neroden/programming/timetable_kit/timetable_kit/amtrak/GTFS.zip"
    )
    master_feed = initialize_feed(gtfs=gtfs_filename)
    my_agency = Agency(master_feed)
    print(my_agency.get_stop_name("ALB"))
    # This works but is ugly / undesirable
    my_agency.get_stop_name = amtrak_get_stop_name
    print(my_agency.get_stop_name("ALB"))
    print(my_agency.get_stop_name("ALB", doing_multiline_text=True))
    print(my_agency.get_stop_name("ALB", doing_html=True))

