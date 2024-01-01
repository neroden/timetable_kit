# connecting_services/text_assembly.py
# Part of timetable_kit
#
# Copyright 2022, 2024 Nathanael Nerode.  Licensed under GNU Affero GPL v.3>
"""This module assembles suitable HTML or text strings for connecting services."""

from timetable_kit.debug import debug_print

# Needed to initialize the catalog if it hasn't been initialized yet
import timetable_kit.connecting_services.catalog as catalog  # For catalog.initialize()

# This contains the actual data
# It is fully memoized and should return the same thing each time
# only calculating the first time
from timetable_kit.connecting_services.catalog import get_connecting_services_dict

# This snags the CSS (it's a function)
from timetable_kit.connecting_services.catalog import get_css_for_all_logos


# For a safe version of <br>
from timetable_kit.text_assembly import SAFE_BR


def get_connecting_service_logo_html(connecting_service, doing_html=True) -> str:
    """Return suitable HTML for the connecting service's logo.

    If no icon, return suitable HTML for the connecting service's alt name.
    """
    # Fish out the data for the correct service
    try:
        service_dict = get_connecting_services_dict()[connecting_service]
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


def get_connecting_service_key_html(connecting_service, doing_html=True) -> str:
    """Return suitable HTML for a key for the connecting service."""
    # Fish out the data for the correct service
    try:
        service_dict = get_connecting_services_dict()[connecting_service]
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


def get_keys_html(services_list, one_line=True) -> str:
    """Return suitable HTML for the full key for all connecting services.

    one_line=True (default): means one line for all services.
    one_line=False: means several lines, one line per service.

    DOES NOT do the surrounding decoration ("Connecting services:") -- that is done over
    in the main Jinja templates
    """
    # TODO: this should probably be a table for screen reader purposes

    # Bail out early if there are no connecting services
    if not services_list:
        return ""
    # Strip services which aren't in our dictionary.
    cleaned_services_list = [
        service
        for service in services_list
        if service in get_connecting_services_dict().keys()
    ]

    if one_line:
        space_or_br = " "
    else:
        space_or_br = SAFE_BR

    all_keys = space_or_br.join(
        [
            (get_connecting_services_dict()[service])["logo_key_html"]
            for service in cleaned_services_list
        ]
    )
    return all_keys
