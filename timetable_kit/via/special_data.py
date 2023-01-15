# via/special_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module includes VIA *data* which can't be found automatically in VIA GTFS.

This includes the list of which stations are major,
which trains carry checked baggage,
which trains have sleeper cars, etc.
"""


def is_connecting_service(tsn):
    """Is this a connecting, non-VIA service?"""

    # VIA has two non-VIA services in their data, but they *don't have tsns*.
    # This must be addressed by patching the feed.

    # FIXME.
    return False


# Parentheses makes a TUPLE.
sleeper_trains = set(
    (
        "1",  # Canadian
        "2",  # Canadian
        "3",  # Truncated Canadian Vancouver - Edmonton
        "4",  # Truncated Canadian
        "14",  # Ocean
        "15",  # Ocean
    )
)


def is_sleeper_train(train_number):
    """Does this train have sleeper cars?"""
    return train_number in sleeper_trains


# Trains with checked baggage cars.
# I have no idea how to find this out from VIA.
# FIXME.

other_checked_baggage_day_trains = ()

# Assemble these trains as a set.  Ugly!
checked_baggage_trains = set(
    [
        *sleeper_trains,
        *other_checked_baggage_day_trains,
    ]
)


def train_has_checked_baggage(trip_short_name: str) -> bool:
    """
    Given a trip_short_name (train number), return "True" if it has checked baggage and "False" if not.

    This is based on crowdsourced data since Amtrak doesn't have a machine-readable way to get it.
    """
    return trip_short_name in checked_baggage_trains


def is_high_speed_train(trip_short_name: str) -> bool:
    """
    Given a trip_short_name (train number) return "True" if we should color it as a high speed train.

    For VIA?  False.
    """
    return False


# "Major stations".  This is for timetable styling: making them bigger and bolder.
# This should really be per-timetable but this is a start
# These are exactly the stations which VIA boldfaces on their website
# Plus a few US stations, since VIA didn't boldface any of them

# Station code reference: https://cptdb.ca/wiki/index.php/VIA_Rail_Canada_stations
# This is missing US stations though, and Hamilton (!)

major_stations_list = (
    # Atlantic Canada
    "HLFX",  # Halifax
    "MCTN",  # Moncton
    "MIRA",  # Miramichi
    "TRUR",  # Truro
    # Quebec
    "GASP",  # Gaspe (closed)
    "JONQ",  # Jonquiere
    "MTRL",  # Montreal
    "PERC",  # Perce (closed)
    "QBEC",  # Quebec (City)
    "RMSK",  # Rimouski
    "SENN",  # Senneterre
    # Ontario
    "BLVL",  # Belleville
    "CWLL",  # Cornwall
    # Hamilton
    "KGON",  # Kingston
    "KITC",  # Kitchener
    "LNDN",  # London
    "NIAG",  # Niagara Falls
    "OTTW",  # Ottawa
    "SARN",  # Sarnia
    "SUDB",  # Sudbury
    "TRTO",  # Toronto
    "WDON",  # Windsor
    # Manitoba
    "CHUR",  # Churchill
    "TPAS",  # The Pas
    "WNPG",  # Winnipeg
    # Saskatchewan
    "SASK",  # Saskatoon
    # Alberta
    "EDMO",  # Edmonton
    "JASP",  # Jasper
    # British Columbia
    "KAMN",  # Kamloops North
    "PGEO",  # Prince George
    "PRUP",  # Prince Rupert
    "VCVR",  # Vancouver
    # US Stations
    "BUFX",  # Buffalo - Exchange
    "ALBY",  # Albany
    "NEWY",  # New York City
)


def is_standard_major_station(station_code):
    """Is a station on the list of standard 'major stations' for VIA?"""
    return station_code in major_stations_list


# TESTING
if __name__ == "__main__":
    print(train_has_checked_baggage("1"))
    print(train_has_checked_baggage("5"))
