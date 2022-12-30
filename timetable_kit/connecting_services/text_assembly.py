# connecting_services/text_assembly.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3>

"""
This module assembles suitable HTML or text strings for connecting services.
"""

from timetable_kit.debug import debug_print

# This contains the actual data
from timetable_kit.connecting_services.catalog import connecting_services_dict

# This snags the CSS
from timetable_kit.connecting_services.catalog import get_css_for_all_logos


def get_connecting_service_logo_html(connecting_service, doing_html=True) ->str:
    """
    Return suitable HTML for the connecting service's logo.

    If no icon, return suitable HTML for the connecting service's alt name.
    """
    # Fish out the data for the correct service
    try:
        service_dict = connecting_services_dict[connecting_service]
    except KeyError:
        # Probably due to a mistyped connecting_service in Amtrak-specific code...
        debug_print(1, "Couldn't find connecting service info for", connecting_service)
        # Return blank in this case
        return ""
    # Found the service, get the HTML
    # (prebuilt in catalog.py during initialization)
    if doing_html:
        return service_dict["logo_html"]
    else:
        return service_dict["alt"]


def get_connecting_service_key_html(connecting_service, doing_html=True) ->str:
    """
    Return suitable HTML for a key for the connecting service.
    """
    # Fish out the data for the correct service
    try:
        service_dict = connecting_services_dict[connecting_service]
    except KeyError:
        # Probably due to a mistyped connecting_service in Amtrak-specific code...
        debug_print(1, "Couldn't find connecting service info for", connecting_service)
        # Return blank in this case
        return ""
    # Found the service, get the HTML
    # (prebuilt in catalog.py during initialization)
    if doing_html:
        return service_dict["logo_key_html"]
    else:
        return " : ".join([service_dict["alt"], service_dict["full_name"]])


def get_full_key_html(station_codes_list: list[str], one_line=True) -> str:
    """
    Return suitable HTML for the full key for all connecting services.
    one_line=True (default) means one line for all services
    one_line=False means several lines, one line per service
    """
    return "FIXME"


### TESTING CODE ###
if __name__ == "__main__":
    print("Testing plaintext:")
    print(get_connecting_service_icon_html("marc", doing_html=False))
    print(get_connecting_service_icon_html("baltimore_lrt", doing_html=False))
    print("Testing HTML:")
    print(get_connecting_service_icon_html("marc"))
    print(get_connecting_service_icon_html("baltimore_lrt"))
    print("Testing key:")
    print(get_connecting_service_key_html("marc"))
    print(get_connecting_service_key_html("baltimore_lrt"))
    print("Testing CSS:")
    print(get_css_for_all_logos())
