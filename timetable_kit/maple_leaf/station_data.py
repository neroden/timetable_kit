# maple_leaf/station_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
For the hybrid Amtrak-VIA GTFS for the Maple Leaf, we need to create a unified stops.txt.

This module contains the data needed to do that.
"""


# Maps Amtrak station code to VIA station code
# Note that the Canadian border "CBN" has no VIA station code
amtrak_code_to_via_code = {
    "NYP": "NEWY",
    "YNY": "YONK",
    "CRT": "CROT",
    "POU": "POUG",
    "RHI": "RHIN",
    "HUD": "HUDS",
    "ALB": "ALBY",
    "SDY": "SCHE",
    "AMS": "AMST",
    "UCA": "UTIC",
    "ROM": "ROME",
    "SYR": "SYRA",
    "ROC": "ROCH",
    "BUF": "BUFF",
    "BFX": "BUFX",
    "NFL": "NFNY",
    # Maple Leaf in Canada
    "NFS": "NIAG",
    "SCA": "SCAT",
    "GMS": "GRIM",
    "AST": "ALDR",
    "OKL": "OAKV",
    "TWO": "TRTO",
}


# Map from VIA codes to Amtrak codes.
via_code_to_amtrak_code = {
    via_code: amtrak_code for amtrak_code, via_code in amtrak_code_to_via_code.items()
}

# Which stations are Canadian?
canadian_stations = [
    "NFS",
    "SCA",
    "GMS",
    "AST",
    "OKL",
    "TWO",
]

# Which stations are American?
american_stations = [
    "NYP",
    "YNY",
    "CRT",
    "POU",
    "RHI",
    "HUD",
    "ALB",
    "SDY",
    "AMS",
    "UCA",
    "ROM",
    "SYR",
    "ROC",
    "BUF",
    "BFX",
    "NFL",
    "CBN",  # Canadian border
]

# Testing
if __name__ == "__main__":
    print(via_code_to_amtrak_code["GRIM"])
