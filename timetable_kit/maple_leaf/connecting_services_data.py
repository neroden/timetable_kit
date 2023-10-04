# maple_leaf/connecting_services_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module is a database of which stations connect to which other transit services.

Sadly, it must be maintained by hand.
"""

# key: station code
# value: list of services (strings matching the definitions in timetable_kit/connecting_services/*.py
# Order matters: it's the order the logos will be printed in
# Maple Leaf is the only timetable where we include both VIA and Amtrak connections
# New York State Fair (NYF) shows up occasionally, but leave this out
connecting_services_dict = {
    "NYP": ["amtrak", "njt", "nyc_subway", "lirr"],
    "YNY": ["amtrak"],
    "CRT": ["amtrak", "metro_north"],
    "POU": ["amtrak", "metro_north"],
    "RHI": ["amtrak"],
    "HUD": ["amtrak"],
    "ALB": ["amtrak"],
    "SDY": ["amtrak"],
    "AMS": ["amtrak"],
    "UCA": ["amtrak", "adirondack"],
    "ROM": ["amtrak"],
    "SYR": ["amtrak"],
    "ROC": ["amtrak"],
    "BUF": ["amtrak"],
    "BFX": ["amtrak", "nfta_metro"],
    "NFL": ["amtrak"],
    "CBN": [],  # Canadian Border
    # Maple Leaf in Canada
    "NFS": ["via_rail", "go_transit"],
    "SCA": ["via_rail", "go_transit"],
    "GMS": ["via_rail"],
    "AST": ["via_rail", "go_transit"],
    "OKL": ["via_rail", "go_transit"],
    "TWO": ["via_rail", "go_transit", "union_pearson_express", "ttc"],
}
