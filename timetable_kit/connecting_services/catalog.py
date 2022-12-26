# connecting_services/catalog.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module contains the list of known connecting services, with
their icon files, CSS files, CSS class names, etc.

The exported data is connecting_services_data.
"""

_marc_dict = {
    "src": "MARC_train.svg",
    "css_file": "MARC_train.css",
    "class": "marc-train-img",
    "alt": "MARC",
    "title": "MARC Train",
    "url": "https://www.mta.maryland.gov/schedule?type=marc-train",
    "full_name": "MARC Train",
}

_baltimore_lrt_dict = {
    "src": "Baltimore_Light_RailLink_logo.svg",
    "css_file": "Baltimore_Light_RailLink_logo.css",
    "class": "baltimore-lrt-img",
    "alt": "LRT",
    "title": "Baltimore LRT",
    "url": "https://www.mta.maryland.gov/schedule/lightrail",
    "full_name": "Baltimore Light Rail Link",
}

# And now the "dictionary of dictionaries":
connecting_services_data = {
    "marc": _marc_dict,
    "baltimore_lrt": _baltimore_lrt_dict,
}
