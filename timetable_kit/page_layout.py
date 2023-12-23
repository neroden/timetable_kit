# page_layout.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Lay out the HTML page which goes around the timetable.

The table itself is layed out in the module timetable_styling using Pandas's Styler to apply CSS classes.
This fills in the symbol key and text around it to make a full page.

This uses a bunch of CSS files, and a few HTML files, in the "fragments" folder.
This uses Jinja2, via the load_resources module.
"""

# Other people's packages
import datetime  # for getting today's date for credit on the timetable
import pandas as pd

# My packages
# This is tricky.
# We need runtime data such as the subpackage for the agency (amtrak, via, etc.)
import timetable_kit.runtime_config

# And we need a shorthand way to refer to it
from timetable_kit.runtime_config import agency
from timetable_kit.runtime_config import agency_singleton

# The header styling for each table has to be done in an ugly way with special CSS.
from timetable_kit.timetable_styling import make_header_styling_css

from timetable_kit import text_presentation
from timetable_kit import icons
from timetable_kit import connecting_services

from timetable_kit.debug import debug_print

from timetable_kit.load_resources import (
    get_font_css,
    template_environment,
)


def get_generally_applicable_css(fonts: list[str] = ["SpartanTT"]) -> str:
    """
    Returns the CSS which is generally applicable to all timetables,
    as opposed to CSS for styling an individual table & key.
    """
    # For producing multi-page timetables.
    # These should not vary by table or page.

    offset_comment = "/***************************************************/"
    header_comment = "/* Start CSS applicable to all pages, tables, keys */"
    footer_comment = "/*  End CSS applicable to all pages, tables, keys  */"

    # For icons as imgs.
    # Get the CSS for styling icons (contains vertical alignment and 1em height/width)
    # This is used every time an icon is inserted.
    # This includes the CSS for all icons whether used in this timetable or not.
    icons_css = icons.get_css_for_all_icons()

    # For connecting service logos as imgs:
    # This includes the CSS for all logos including those not used in this timetable.
    logos_css = connecting_services.get_css_for_all_logos()

    # The @font-face directives:
    # It breaks Weasyprint to include references to nonexistent fonts,
    # So we have to make sure it only includes used fonts.
    # (Works OK for rendering in Firefox, though.)
    fonts_css_list = []
    for font in fonts:
        fonts_css_list.append(get_font_css(font))
    font_faces_css = "".join(fonts_css_list)

    return "\n".join(
        [
            offset_comment,
            header_comment,
            offset_comment,
            font_faces_css,
            icons_css,
            logos_css,
            offset_comment,
            footer_comment,
            offset_comment,
        ]
    )


def finish_html_timetable(
    styled_timetable_html,
    header_styling_list,
    tt_id,
    *,
    author,
    aux=None,
    start_date,
    end_date,
    station_codes_list,  # For connecting services key
):
    """
    Take the output of style_timetable_for_html -- which is mostly a table --
    and make it a full HTML file with embedded CSS.

    The header_styling_list has CSS attributes (not classes) for each header column
    (indexed by zero-based column number).  This is due to inefficiencies in PANDAS.

    The mandatory "author" argument gives the author of the timetable.
    """
    # ID for the <div> which brackets a whole timetable page
    page_id = "P_" + tt_id
    # Note that "T_" + tt_id will be the ID for the table (the T_ is prefixed by PANDAS)
    # table_id = "T_" + tt_id
    # ID for the symbol key table
    symbol_key_id = "SK_" + tt_id

    # Stuff which is the same for all pages & tables
    # @font-face directives
    # Icon and logo styling
    generally_applicable_css = get_generally_applicable_css(fonts=["SpartanTT"])

    # The header stylings, totally different for each table
    header_styling_css = make_header_styling_css(header_styling_list, table_uuid=tt_id)

    if aux is None:
        aux = {}  # Empty dict

    # We need to add the extras to make this a full HTML & CSS file now.
    # We're going to feed the entire aux file through, but we need some defaults
    if "title" not in aux:
        aux["title"] = "A Timetable"

    if "heading" not in aux:
        aux["heading"] = "A Timetable"

    if "landscape" in aux:
        debug_print(1, "Landscape orientation")

    connecting_services_one_line = True
    if "key_on_right" in aux:
        debug_print(1, "Key on right")
        connecting_services_one_line = False

    ### FONTS
    font_name = "SpartanTT"
    font_size = "6pt"
    font_is_tiny = True

    debugging_fonts = True
    if debugging_fonts:
        # This makes it obvious when a font doesn't load
        backup_font_name = "cursive"
    else:
        backup_font_name = "sans-serif"

    ### ICONS

    # Key for connecting services:
    # First use the station codes list to get a list of all *relevant* services
    services_list = agency_singleton().get_all_connecting_services(station_codes_list)
    # Then feed that through to get the full key html:
    connecting_services_keys_html = connecting_services.get_keys_html(
        services_list=services_list, one_line=connecting_services_one_line
    )

    # NOTE: We would like to try the alternative embedded SVG version.
    # But Weasy can't handle SVG references within HTML.

    ### Prepare Jinja template substitution:

    stylesheet_params = {
        "generally_applicable_css": generally_applicable_css,
        "font_name": font_name,
        "backup_font_name": backup_font_name,
        "font_size": font_size,  # 6pt
        "font_is_tiny": font_is_tiny,  # True
        "header_styling": header_styling_css,
        "page_id": page_id,
    }

    production_date_str = datetime.date.today().isoformat()
    start_date_str = text_presentation.gtfs_date_to_isoformat(start_date)
    end_date_str = text_presentation.gtfs_date_to_isoformat(end_date)

    html_params = {
        "lang": "en-US",
        "encoding": "utf-8",
        "internal_stylesheet": True,
        "timetable": styled_timetable_html,
        "timetable_kit_url": "https://github.com/neroden/timetable_kit",
        "production_date": production_date_str,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "author": author,
        "connecting_services_keys_html": connecting_services_keys_html,
        "connecting_bus_key_sentence": agency_singleton().connecting_bus_key_sentence(),  # "Connecting Bus Service (can be booked through Amtrak)"
        "agency_css_class": agency_singleton().agency_css_class(),  # Used to change color of top heading (possibly other stuff later)
        "unofficial_disclaimer": agency_singleton().unofficial_disclaimer(),  # "This is unofficial" disclaimer
        "always_check_disclaimer": agency_singleton().always_check_disclaimer(),  # "Always check agency website"
        "gtfs_data_link": agency_singleton().gtfs_data_link(),  # "GTFS data"
        "by_agency_with_gtfs_link": agency_singleton().by_agency_with_gtfs_link(),  # for GTFS released "by Amtrak"
        "add_via_disclaimer": agency_singleton().add_via_disclaimer(),  # True or False, should we add the VIA disclaimer
        "symbol_key_id": symbol_key_id,
    }

    # Allows direct icon references in Jinja2
    icon_params = {
        "baggage_icon": icons.get_baggage_icon_html(),
        "accessible_icon": icons.get_accessible_icon_html(),
        "inaccessible_icon": icons.get_inaccessible_icon_html(),
        "sleeper_icon": icons.get_sleeper_icon_html(),
        "bus_icon": icons.get_bus_icon_html(),
    }

    # Dictionary merge, html_params take priority, Python 3.9
    # Not sure about associativity, but we don't plan to have duplicates anyway
    # Throw the entire aux file in
    full_page_params = aux | stylesheet_params | icon_params | html_params

    # debug_params = {i: full_page_params[i] for i in full_page_params if i != "timetable"}
    # debug_print(3, debug_params )

    # Get the Jinja2 template environment (set up in load_resources module)
    # and use it to retrieve the correct template (complete with many includes)...
    page_tpl = template_environment.get_template("page_standard.html")
    # ...then render it.
    finished_timetable_html = page_tpl.render(full_page_params)
    return finished_timetable_html
