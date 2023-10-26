# maple_leaf/connecting_services_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module is a database of which stations connect to which other transit services.

Sadly, it must be maintained by hand.
"""

# In order to reuse the existing code, we have to key these by the *enhanced* station code,
# which looks like NYP / NEWY

# key: station code
# value: list of services (strings matching the definitions in timetable_kit/connecting_services/*.py
# Order matters: it's the order the logos will be printed in
# Maple Leaf is the only timetable where we include both VIA and Amtrak connections
# New York State Fair (NYF) shows up occasionally, but leave this out
connecting_services_dict = {
    "NYP / NEWY": ["amtrak", "njt", "nyc_subway", "lirr"],
    "YNY / YONK": ["amtrak"],
    "CRT / CROT": ["amtrak", "metro_north"],
    "POU / POUG": ["amtrak", "metro_north"],
    "RHI / RHIN": ["amtrak"],
    "HUD / HUDS": ["amtrak"],
    "ALB / ALBY": ["amtrak"],
    "SDY / SCHE": ["amtrak"],
    "AMS / AMST": ["amtrak"],
    "UCA / UTIC": ["amtrak", "adirondack"],
    "ROM / ROME": ["amtrak"],
    "SYR / SYRA": ["amtrak"],
    "ROC / ROCH": ["amtrak"],
    "BUF / BUFF": ["amtrak"],
    "BFX / BUFX": ["amtrak", "nfta_metro"],
    "NFL / NFNY": ["amtrak"],
    # "CBN": [],  # Canadian Border
    # Maple Leaf in Canada
    "NFS / NIAG": ["via_rail", "go_transit"],
    "SCA / SCAT": ["via_rail", "go_transit"],
    "GMS / GRIM": ["via_rail"],
    "AST / ALDR": ["via_rail", "go_transit"],
    "OKL / OAKV": ["via_rail", "go_transit"],
    "TWO / TRTO": ["via_rail", "go_transit", "union_pearson_express", "ttc"],
}
