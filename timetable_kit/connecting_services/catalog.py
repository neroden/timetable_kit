# connecting_services/catalog.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module contains the list of known connecting services, with
their icon files, CSS files, CSS class names, etc.

The exported data is connecting_services_data.

To do: consider converting this to a .csv file and reading it dynamically.
"""

# This isn't real, it's a template for making new ones
# Note that "title" is the mouseover
# "alt" is for when we can't display images at all
# "full_name" is for use in the key at the bottom
_generic_dict = {
    "src": "generic.svg",
    "css_file": "generic.css",
    "class": "generic-img",
    "alt": "Generic",
    "title": "Generic",
    "url": "https://www.generic.org/",
    "full_name": "Generic Agency",
}

# NEC connecting agencies: North to south.

_njt_dict = {
    "src": "NJT_logo.svg",
    "css_file": "NJT_logo.css",
    "class": "njt-logo-img",
    "alt": "NJT",
    "title": "NJ Transit",
    "url": "https://www.njtransit.com/",
    "full_name": "NJ Transit",
}

_septa_dict =
    "src": "SEPTA.svg",
    "css_file": "SEPTA.css",
    "class": "septa-img",
    "alt": "SEPTA",
    "title": "SEPTA",
    "url": "https://septa.org/",
    "full_name": "SEPTA",
}

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

_wmata_dict = {
    "src": "WMATA_Metro_Logo.svg",
    "css_file": "WMATA_Metro_Logo.css",
    "class": "wmata-metro-img",
    "alt": "WMATA",
    "title": "WMATA",
    "url": "https://www.wmata.com/",
    "full_name": "WMATA",
}

# And now the "dictionary of dictionaries":
connecting_services_data = {
    "marc": _marc_dict,
    "baltimore_lrt": _baltimore_lrt_dict,
    
}
