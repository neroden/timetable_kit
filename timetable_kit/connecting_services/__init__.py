# connecting_services/__init__.py
# Init file for connecting services subpackage of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
timetable_kit.connecting_services subpackage

Functions for adding connecting service icons and links to the station line in a timetable.
"""

# Used to copy image files to output
from timetable_kit.connecting_services.catalog import get_filenames_for_all_logos

# Used to copy CSS for sizing image files to output
from timetable_kit.connecting_services.catalog import get_css_for_all_logos

# Grab the HTML for a single  connecting service
from timetable_kit.connecting_services.text_assembly import (
    get_connecting_agency_logo_html,
)
