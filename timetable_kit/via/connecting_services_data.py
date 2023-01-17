# via/connecting_services_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module is a database of which VIA stations connect to which other transit services.

Sadly, it must be maintained by hand.
"""

# key: VIA rail station code (not stop id)
# value: list of services (strings matching the definitions in timetable_kit/connecting_services/*.py
# Order matters within a single station: it's the order the logos will be printed in
connecting_services_dict = {
    # Maple Leaf stations in NY
    "NEWY": ["amtrak", "njt", "nyc_subway", "lirr"],
    "YONK": ["amtrak", "metro_north"],
    "CROT": ["amtrak", "metro_north"],
    "POUG": ["amtrak", "metro_north"],
    "HUDS": ["amtrak"],
    "RHIN": ["amtrak"],
    "ALBY": ["amtrak"],
    "SCHE": ["amtrak"],
    "AMST": ["amtrak"],
    "ROME": ["amtrak"],
    "UTIC": ["amtrak", "adirondack"],
    "SYRA": ["amtrak"],
    "ROCH": ["amtrak"],
    "BUFF": ["amtrak"],
    "BUFX": ["amtrak", "nfta_metro"],
    "NFNY": ["amtrak"],
    # Maple Leaf in Canada
    "NIAG": ["go_transit"],
    "SCAT": ["go_transit"],
    "GRIM": [],  # No GO at Grimsby
    "ALDR": ["go_transit"],
    "OAKV": ["go_transit"],
    # Toronto!
    "TRTO": ["amtrak", "go_transit", "union_pearson_express", "ttc"],
    # Montreal !
    # "Amtrak" here is the Adirondack, currently suspended
    "MTRL": ["amtrak", "exo", "montreal_metro"],
    # on the way to Hervey/Senneterre/Jonquiere
    "SAUV": ["exo", "montreal_metro"],
    "ANJO": ["exo"],
    # on the way to Quebec City and Halifax
    "SLAM": ["exo"],
    # on the way to Ottawa and points west
    # Note that Dorval also needs the montreal_airport_shuttle notation
    "DORV": ["exo"],
    # The Pas
    "TPAS": ["keewatin_railway"],
    # Vancouver, BC
    # "Amtrak" here is the Cascades
    "VCVR": ["amtrak", "skytrain"],
}


def get_all_connecting_services(station_list: list[str]) -> list:
    """
    Given a list of station codes, return a list of services which connect
    (with no duplicates)
    """
    all_services = []
    for station in station_list:
        new_services = connecting_services_dict.get(station, [])
        for service in new_services:
            if service not in all_services:
                all_services.append(service)
    return all_services


if __name__ == "__main__":
    print("File parsed.")
    # This both lists all the services, and tests get_all_connecting_services at the same time
    services = get_all_connecting_services(connecting_services_dict.keys())
    print("All known connecting services:", services)
