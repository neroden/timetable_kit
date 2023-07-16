# hartford_line/connecting_services_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module is a database of which Amtrak stations connect to which other transit services.

Sadly, it must be maintained by hand.
"""

# key: station code
# value: list of services (strings matching the definitions in timetable_kit/connecting_services/*.py
# Order matters: it's the order the logos will be printed in
# Hartford Line timetables are very short on space,
# So we leave out connecting services at NYP and WAS
connecting_services_dict = {
    # Hartford Line
    "SPG": ["amtrak"],
    "WNL": [],
    "WND": [],
    "HFD": [],
    "BER": [],
    "MDN": [],
    "WFD": [],
    "STS": ["shore_line_east"],
    "NHV": ["amtrak", "shore_line_east", "metro_north"],
    "NYP": [],
    "WAS": [],
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
