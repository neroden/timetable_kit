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
# Email dated Jan 26, 2023 at 7:05 AM:
"""
Good morning,

Thank you for contacting Via Rail Canada.

No trains in the Corridor have checked baggage service at this time.

Only Long Haul trains (Toronto to Vancouver, Halifax to Montreal, 
Winnipeg to Churchill, Montreal to Jonquiere/Senneterre, Jasper to 
Prince Rupert and Sudbury to White River) have checked baggage service 
and only at manned stations on these routes.

If you have any further questions, please do not hesitate to contact us.

Sincerely,

Nathalie
Customer Service
Via Rail Canada
"""

other_checked_baggage_day_trains = set(
    (
        "600",  # Jonquiere
        "601",
        "602",
        "603",  # Senneterre
        "604",
        "606",
        "185",  # Sudbury - White River
        "186",
        "690",  # Winnipeg - Churchill
        "691",
        "692",
        "693",
        "5",  # Jasper - Prince Rupert
        "6",
    )
)

# Assemble these trains as a set.  Ugly!
checked_baggage_trains = set(
    [
        *sleeper_trains,
        *other_checked_baggage_day_trains,
    ]
)


def station_has_checked_baggage(station_code: str) -> bool:
    """
    Does this VIA rail station handle checked baggage?

    Currently we have no data, so must assume not
    """
    return False


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
# This list started as stations which VIA boldfaces on their website
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
    "SFOY",  # Sainte-Foy (for Quebec City) -- I added this one
    "QBEC",  # Quebec (City)
    "RMSK",  # Rimouski
    "SENN",  # Senneterre
    "HERV",  # Hervey -- added for the JONQ/SENN split
    # Ontario
    "BLVL",  # Belleville
    "CWLL",  # Cornwall
    "HAML",  # Hamilton
    "KGON",  # Kingston
    "KITC",  # Kitchener
    "LNDN",  # London
    "NIAG",  # Niagara Falls
    "OTTW",  # Ottawa
    "SARN",  # Sarnia
    "TRTO",  # Toronto
    "WDON",  # Windsor
    # Western Ontario -- I added these for the Canadian
    "CAPR",  # Capreol
    "HNPN",  # Hornepayne
    "SLKT",  # Sioux Lookout
    # Western Ontario -- I added these for the Sudbury-White River train
    "SUDB",  # Sudbury -- VIA has this one boldfaced
    "CART",  # Cartier
    "CHAP",  # Chapleau
    "WHTR",  # White River
    # Manitoba
    "CHUR",  # Churchill
    "GILL",  # Gillam - I added
    "THOM",  # Thompson - I added
    "TPAS",  # The Pas
    "CANO",  # Canora - I added
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
