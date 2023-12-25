# hartford_line/connecting_services_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""This module is a database of which Amtrak stations connect to which other
transit services.

Sadly, it must be maintained by hand.
"""

# key: station code
# value: list of services (strings matching the definitions in timetable_kit/connecting_services/*.py
# Order matters: it's the order the logos will be printed in
# Hartford Line timetables are very short on space,
# So we leave out connecting services at NYP and WAS
connecting_services_dict: dict[str, list[str]] = {
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
