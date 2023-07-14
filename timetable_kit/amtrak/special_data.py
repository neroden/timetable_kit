# amtrak/special_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module includes Amtrak *data* which isn't provided by Amtrak.

This includes the list of which stations are major,
which trains carry checked baggage,
known problems with Amtrak's GTFS data, and similar.

(Functions for extracting data from Amtrak's JSON stations database are elsewhere.)
"""


def is_connecting_service(tsn):
    """Is this a connecting, non-Amtrak service?"""

    # TODO: convert to use agency data, and push "uphill"
    # Currently this only runs on non-buses (generally trains)

    # Amtrak's train numbers are all numbers.
    # For merged datasets such as the Hartford Line, the train numbers aren't numbers.
    # Sooo....
    if not tsn.isdigit():
        # There's stuff other than digits in this TSN.
        # So it isn't Amtrak.
        return True
    if int(tsn) >= 3000:
        # Amtrak's high-numbered services are non-Amtrak.
        # We COULD check the agency data, and we probably should
        return True
    return False


# Parentheses makes a TUPLE.
sleeper_trains = set(
    (
        "1",
        "2",  # SL
        "21",
        "22",
        "421",
        "422",  # TE -- also 321/322?
        "3",
        "4",  # SWC
        "5",
        "6",  # CZ
        "7",
        "8",
        "27",
        "28",  # EB
        "11",
        "14",  # CS
        "19",
        "20",  # Crescent
        "29",
        "30",  # CL
        "48",
        "49",
        "448",
        "449",  # LSL
        "50",
        "51",  # Cardinal
        "52",
        "53",  # Auto Train
        "58",
        "59",  # CONO
        "91",
        "92",  # Silver Star
        "97",
        "98",  # Silver Meteor
    )
)


def is_sleeper_train(train_number):
    """Does this train have sleeper cars?"""
    return train_number in sleeper_trains


# Trains with checked baggage cars.
# This one really does need to be right; I can't get it from Amtrak data.

# Oookay.  Pacific Surfliners change their numbers fairly frequently.
# There are two ranges:
# 561 through 595 (NB) or 562 through 596 (SB) for "short" trains south of LA
# 761 through 795 (NB) or 762 through 796 (SB) for "long" trains north of LA
# We do 560-599 and 760-799 for completeness.  Note that range excludes the last item.
pacific_surfliner_trains = [str(item) for item in [*range(560, 600), *range(760, 800)]]

# Similar issue with San Joaquins.
# Lowest numbered is #701.  Highest numbered is #719.
# There is no #700, and #699 is a Downeaster.
# While #720 is a Capitol Corridor to Sacramento.
san_joaquins_trains = [str(item) for item in range(700, 720)]

# Similar issue with Cascades.
# Lowest numbered Cascades is #500.  Highest is #519.
# And #520 is a Sacramento Capitol Corridor train.
# And #499 is a Springfield - New Haven train.
cascades_trains = [str(item) for item in range(500, 520)]

# Similar issue with Hiawatha.
# Lowest numbered Hiawatha is 329; highest numbered is 343.
# However, #311-316 are Kansas City to St Louis.
# However, #350 is a Wolverine to Pontiac.
# We do 320-349.
hiawatha_trains = [str(item) for item in range(320, 350)]

other_checked_baggage_day_trains = (
    "42",
    "43",  # Pennsylvanian
    "79",
    "80",  # Carolinian
    "73",
    "74",
    "75",
    "76",  # Piedmont
    "77",
    "78",
    "89",
    "90",  # Palmetto
)

# Assemble these trains as a set.  Ugly!
# Stupid technical issue with #448/449 not having a baggage car!
checked_baggage_trains = set(
    [
        *sleeper_trains,
        *pacific_surfliner_trains,
        *san_joaquins_trains,
        *cascades_trains,
        *hiawatha_trains,
        *other_checked_baggage_day_trains,
    ]
) - set(["448", "449"])


def train_has_checked_baggage(trip_short_name: str) -> bool:
    """
    Given a trip_short_name (train number), return "True" if it has checked baggage and "False" if not.

    This is based on crowdsourced data since Amtrak doesn't have a machine-readable way to get it.
    """
    return trip_short_name in checked_baggage_trains


def is_high_speed_train(trip_short_name: str) -> bool:
    """
    Given a trip_short_name (train number) return "True" if we should color it as a high speed train.

    Basically we're just counting Acela for Amtrak, to copy the old timetable style.
    """
    # So this really should check the GTFS to see if it's an Acela... but we don't. FIXME
    # Anything from 2100 to 2299 is an Acela.
    if not trip_short_name.isdigit():
        return False
    tsn_as_number = int(trip_short_name)
    if tsn_as_number >= 2100 and tsn_as_number <= 2299:
        return True
    return False


# "Major stations".  This is for timetable styling: making them bigger and bolder.
# This should really be per-timetable but this is a start
# (Empire doesn't call out NEC stations on connecting trains)
# (Vermonter only calls out NY and DC on NEC)
major_stations_list = (
    "BOS",  # NEC timetable stations first
    "NHV",
    "NYP",
    "NYG",  # Just in case there's a rerouting
    "PHL",
    "WAS",
    "RVR",  # Virginia services.  Richmond Staples Mill + 3 terminuses
    # "LYH", Amtrak emphasized, I won't since Roanoake extension
    "NPN",
    "NFK",
    "RNK",
    "HAR",  # Keystone timetable
    "PGH",
    "ALB",  # Empire timetable
    "BFX",
    "TWO",  # Maple Leaf
    "MTR",  # Adirondack
    "ESX",  # Vermonter
    "SPG",
    "BTN",  # Ethan Allen Express: Burlington
    "RUD",  # Ethan Allen Express: Rutland
    "RGH",  # Carolinian/Piedmont
    "CLT",
    "ATL",  # Crescent
    "BHM",
    "NOL",
    #    "ALT", # Pennsylvanian -- I think I won't emphasize this one.
    "CVS",  # Cardinal
    "CIN",
    "IND",
    "CHI",
    "CLE",  # LSL / CL
    "TOL",
    "GRR",  # Michigan services
    "PTH",
    "DET",
    "PNT",
    "BTL",  # Amtrak didn't mark Battle Creek, but we should
    "CHM",  # CONO/Illini/Saluki
    "CDL",
    "MEM",
    "JAN",
    "STL",  # River Runner
    "KCY",
    "QCY",  # Quincy service
    "MKE",  # Hiawathas
    "SAN",  # California Coastal
    "OSD",  # Major connecting point, I'm adding this
    "LAX",
    "SBA",
    "SLO",
    "SJC",
    "OKJ",
    "SAC",
    "SKN",  # San Joaquins
    "BFD",
    "MSP",  # EB -- Amtrak emphasized nothing on EB, so I picked some
    "MOT",
    "HAV",
    "SPK",
    "PDX",
    "SEA",
    "DEN",  # CZ -- Amtrak didn't, I should
    "SLC",
    "EMY",  # CZ
    "ABQ",  # SWC -- Amtrak didn't
    "FLG",
    "DAL",  # TE -- Amtrak emphasized nothing, so I picked some
    "FTW",  # TE / Heartland Flyer
    "OKC",  # Heartland Flyer -- Amtrak emphasized nothing
    "SAS",  # TE/SL
    "HOS",  # SL -- Amtrak emphasized nothing, so I picked some
    "ELP",
    "TUS",
    "CHS",  # Palmetto -- Amtrak emphasized nothing, so I picked Charleston
    "SAV",  # Silver Service -- Amtrak emphasized nothing, so I picked some
    "JAX",
    "ORL",
    "TPA",
    "MIA",
    "WMA",  # Grand Canyon Railway -- Williams is major
    "GCN",  # Grand Canyon Village station is too long for the timetable if boldfaced,
    # ...but we patch the station name in code, elsewhere.
)


def is_standard_major_station(station_code):
    """Is a station on the list of standard 'major stations' for Amtrak?"""
    return station_code in major_stations_list


# TESTING
if __name__ == "__main__":
    print(pacific_surfliner_trains)
    print(train_has_checked_baggage("1"))
    print(train_has_checked_baggage("5"))
