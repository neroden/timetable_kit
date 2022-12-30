# connecting_services/__init__.py
# Init file for connecting services subpackage of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.connecting_services subpackage

Functions for adding connecting service icons and links to the station line in a timetable.
"""

from timetable_kit.connecting_services.catalog import (
    # Used to copy image files to output
    get_filenames_for_all_logos,
    # Used to copy CSS for sizing image files to output
    get_css_for_all_logos,
)

from timetable_kit.connecting_services.text_assembly import (
    # Get the HTML for a single connecting service for a station name box
    get_connecting_service_logo_html,
    # Get the HTML for all the connecting services keys (for a list of services)
    get_keys_html,
)
