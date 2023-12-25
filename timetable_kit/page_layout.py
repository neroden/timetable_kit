# page_layout.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Lay out the HTML page which goes around the timetable.

The table itself is layed out in the module timetable_styling using
Pandas's Styler to apply CSS classes. This fills in the symbol key and
text around it to make a full page.

This uses a bunch of CSS files, and a few HTML files, in the "fragments"
folder. This uses Jinja2, via the load_resources module.
"""

# for typed return value
from typing import NamedTuple

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


class _HtmlAndCss(NamedTuple):
    """Container for fragment of HTML and associated fragment of CSS.

    The implementation of the container as dict vs. tuple is an
    implementation detail. It may change.
    """

    html_text: str
    css_text: str


def produce_html_page(
    timetable_styled_html,
    header_styling_list,
    tt_id,
    *,
    author,
    aux=None,
    start_date,
    end_date,
    station_codes_list,  # For connecting services key
) -> _HtmlAndCss:
    """
    Take the output of style_timetable_for_html -- which is mostly a table --
    and return a container containing
    html_text -- an HTML <div> section comprising a full page
    css_text -- a section of custom CSS for that HTML

    This will *not* include the CSS which should be shared between multiple pages.
    It will also *not* include the final "wrapper" HTML tags like <html><head> etc.
    and make it a full HTML file with embedded CSS.

    The header_styling_list has CSS attributes (not classes) for each header column
    (indexed by zero-based column number).  This is due to inefficiencies in PANDAS.

    The mandatory "author" argument gives the author of the timetable.
    """
    # ID for the <div> which brackets a whole timetable page
    page_id = "P_" + tt_id
    # ID for the heading (H1) for this, for ARIA use
    heading_id = "H_" + tt_id
    # Note that "T_" + tt_id will be the ID for the table (the T_ is prefixed by PANDAS)
    # table_id = "T_" + tt_id
    # ID for the symbol key table
    symbol_key_id = "SK_" + tt_id

    # We need to add the extras to make this a full HTML & CSS file now.
    # We're going to feed the entire aux file through, but we need some defaults
    if aux is None:
        aux = {}  # Empty dict
    aux.setdefault("heading", "A Timetable")

    if "landscape" in aux:
        debug_print(1, "Landscape orientation")

    connecting_services_one_line = True
    if "key_on_right" in aux:
        debug_print(1, "Key on right")
        connecting_services_one_line = False

    # Key for connecting services:
    # First use the station codes list to get a list of all *relevant* services
    services_list = agency_singleton().get_all_connecting_services(station_codes_list)
    # Then feed that through to get the full key html:
    connecting_services_keys_html = connecting_services.get_keys_html(
        services_list=services_list, one_line=connecting_services_one_line
    )

    ### Prepare Jinja template substitution:

    production_date_str = datetime.date.today().isoformat()
    start_date_str = text_presentation.gtfs_date_to_isoformat(start_date)
    end_date_str = text_presentation.gtfs_date_to_isoformat(end_date)

    html_params = {
        "page_id": page_id,
        "heading_id": heading_id,
        "symbol_key_id": symbol_key_id,
        "timetable": timetable_styled_html,
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
    full_page_params = aux | icon_params | html_params

    # debug_params = {i: full_page_params[i] for i in full_page_params if i != "timetable"}
    # debug_print(3, debug_params )

    # Get the Jinja2 template environment (set up in load_resources module)
    # and use it to retrieve the correct template (complete with many includes)...
    page_tpl = template_environment.get_template("page_standard.html")
    # ...then render it.
    page_html = page_tpl.render(full_page_params)

    ####################################
    # And now the custom per-page CSS. #
    ####################################

    # The header stylings, totally different for each table
    header_styling_css = make_header_styling_css(header_styling_list, table_uuid=tt_id)

    ### FONTS
    # FIXME: there should be a way to vary this per timetable when we finish.
    font_name = "SpartanTT"
    font_size = "6pt"
    font_is_tiny = True

    debugging_fonts = False
    if debugging_fonts:
        # This makes it obvious when a font doesn't load
        backup_font_name = "cursive"
    else:
        backup_font_name = "sans-serif"

    per_page_css_params = {
        "page_id": page_id,
        "header_styling_css": header_styling_css,
        "font_name": font_name,
        "backup_font_name": backup_font_name,
        "font_size": font_size,  # 6pt
        "font_is_tiny": font_is_tiny,  # True
    }
    # Get the Jinja2 template environment (set up in load_resources module)
    # and use it to retrieve the correct template (complete with many includes)...
    per_page_css_tpl = template_environment.get_template("per_page.css")
    # ...then render it.
    per_page_css = per_page_css_tpl.render(per_page_css_params)

    result = _HtmlAndCss(page_html, per_page_css)

    return result


def produce_html_file(
    pages: list[_HtmlAndCss],
    *,
    title,
):
    """
    Take a *list* of containers output by calling produce_html_page, which are like this:
    html_text -- an HTML <div> section for a page
    css_text -- a section of custom CSS for that HTML

    And produce a full HTML file, including <html></html> tags and internal stylesheet.
    Also generates the CSS which should be shared between multiple pages.

    The "title" parameter is mandatory because HTML requires it.
    """
    # For icons as imgs.
    # Get the CSS for styling icons (contains vertical alignment and 1em height/width)
    # This is used every time an icon is inserted.
    # This includes the CSS for all icons whether used in this timetable or not.
    icons_css = icons.get_css_for_all_icons()

    # For connecting service logos as imgs:
    # This includes the CSS for all logos including those not used in this timetable.
    logos_css = connecting_services.get_css_for_all_logos()

    # The @font-face directives:
    # Eventually the list of fonts should be passed in.  FIXME.
    fonts = ["SpartanTT"]
    # It breaks Weasyprint to include references to nonexistent fonts,
    # So we have to make sure it only includes used fonts.
    # (Including nonexistent fonts works OK for rendering in Firefox, though.)
    fonts_css_list = []
    for font in fonts:
        fonts_css_list.append(get_font_css(font))
    font_faces_css = "".join(fonts_css_list)

    stylesheet_params = {
        "icons_css": icons_css,
        "logos_css": logos_css,
        "font_faces_css": font_faces_css,
    }

    html_file_params = {
        "lang": "en-US",
        "encoding": "utf-8",
        "internal_stylesheet": True,
        # "external_stylesheet": False,
        "title": title,
        # Pass the whole structure of pages through to Jinja so it can loop over it
        # Jinja2 doesn't care whether each 'page' structure is a dict or a tuple;
        # The Jinja code is the same either way.
        "pages": pages,
    }

    full_file_params = html_file_params | stylesheet_params

    # Get the Jinja2 template environment (set up in load_resources module)
    # and use it to retrieve the correct template (complete with many includes)...
    file_tpl = template_environment.get_template("full_file.html")
    # ...then render it.
    file_html = file_tpl.render(full_file_params)
    return file_html
