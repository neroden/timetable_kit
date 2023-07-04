# generic_agency/implementation.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
This contains generic code which should be used for agencies which don't have their own subpackages.
"""

import gtfs_kit

gtfs_zip_local_path = None
gtfs_unzipped_local_path = None


def get_route_name(today_feed, route_id) -> str:
    """
    Given today_feed and a route_id, produce a suitable name for a column subheading.
    """
    # Unacceptable stub implementation
    return str(route_id)


def get_station_name_pretty(station_code: str) -> str:
    # Unacceptable stub implementation
    return station_code


# Baggage -- trivial implementations
def station_has_checked_baggage(station_code: str) -> bool:
    return False


def train_has_checked_baggage(trip_short_name: str) -> bool:
    return False


# Access


def station_has_accessible_platform(station_code: str) -> bool:
    # Unacceptable stub implementation
    return False


def station_has_inaccessible_platform(station_code: str) -> bool:
    # Unacceptable stub implementation
    return False


# Feed correction


def patch_feed():
    return


# Type of service on train
def is_connecting_service():
    return False


def is_sleeper_train():
    return False


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
    print(my_agency.get_station_name_pretty("ALB"))
