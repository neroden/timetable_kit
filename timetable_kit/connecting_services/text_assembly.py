#! /usr/bin/env python3
# connecting_services/text_assembly.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3>

"""
This module assembles suitable HTML or text strings for connecting agencies.
"""

from timetable_kit.debug import debug_print

# This contains the actual data
from timetable_kit.connecting_services.catalog import connecting_agencies_dict

# This snags the CSS
from timetable_kit.connecting_services.catalog import get_css_for_all_logos


def get_connecting_agency_logo_html(connecting_agency, doing_html=True):
    """
    Return suitable HTML for the connecting agency's logo.

    If no icon, return suitable HTML for the connecting agency's alt name.
    """
    # Fish out the data for the correct agency
    try:
        agency_dict = connecting_agencies_dict[connecting_agency]
    except KeyError:
        # Probably due to a mistyped connecting_agency in Amtrak-specific code...
        debug_print(1, "Couldn't find connecting agency info for", connecting_agency)
        # Return blank in this case
        return ""
    # Found the agency, get the HTML
    # (prebuilt in catalog.py during initialization)
    if doing_html:
        return agency_dict["logo_html"]
    else:
        return agency_dict["alt"]


def get_connecting_agency_key_html(connecting_agency, doing_html=True):
    """
    Return suitable HTML for a key for the connecting agency.
    """
    # Fish out the data for the correct agency
    try:
        agency_dict = connecting_agencies_dict[connecting_agency]
    except KeyError:
        # Probably due to a mistyped connecting_agency in Amtrak-specific code...
        debug_print(1, "Couldn't find connecting agency info for", connecting_agency)
        # Return blank in this case
        return ""
    # Found the agency, get the HTML
    # (prebuilt in catalog.py during initialization)
    if doing_html:
        return agency_dict["logo_key_html"]
    else:
        return " : ".join([agency_dict["alt"], agency_dict["full_name"]])


### TESTING CODE ###
if __name__ == "__main__":
    print("Testing plaintext:")
    print(get_connecting_agency_icon_html("marc", doing_html=False))
    print(get_connecting_agency_icon_html("baltimore_lrt", doing_html=False))
    print("Testing HTML:")
    print(get_connecting_agency_icon_html("marc"))
    print(get_connecting_agency_icon_html("baltimore_lrt"))
    print("Testing key:")
    print(get_connecting_agency_key_html("marc"))
    print(get_connecting_agency_key_html("baltimore_lrt"))
    print("Testing CSS:")
    print(get_css_for_all_logos())
