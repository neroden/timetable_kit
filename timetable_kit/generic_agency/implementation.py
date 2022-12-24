# generic_agency/implementation.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
This contains generic code which should be used for agencies which don't have their own subpackages.
"""

import gtfs_kit

gtfs_zip_local_path = None
gtfs_unzipped_local_path = None


def get_route_name():
    return


def get_station_name():
    return


def is_standard_major_station():
    return


# Baggage
def station_has_checked_baggage():
    return


def train_has_checked_baggage():
    return


# Access


def station_has_accessible_platform():
    return


def station_has_inaccessible_platform():
    return


# Station name munging


def station_name_to_html():
    return


def station_name_to_multiline_text():
    return


def station_name_to_single_line_text():
    return


# Feed correction


def patch_feed():
    return


# Type of service on train
def is_connecting_service():
    return


def is_sleeper_train():
    return


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


if __name__ == "__main__":
    from timetable_kit.initialize import initialize_feed

    gtfs_filename = (
        "/home/neroden/programming/timetable_kit/timetable_kit/amtrak/GTFS.zip"
    )
    master_feed = initialize_feed(gtfs=gtfs_filename)
    my_agency = Agency(master_feed)
    print(my_agency.get_stop_name("ALB"))
