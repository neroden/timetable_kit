# timetable_styling.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Style a timetable.

This module uses Pandas's Styler to apply CSS classes to a timetable;
then renders HTML, including a lot of complicated extra bits.

This uses a bunch of CSS files, and a few HTML files, in the "fragments" folder.
This uses Jinja2, via the load_resources module.

"""

# Other people's packages
import datetime  # for getting today's date for credit on the timetable

# import pandas as pd
from pandas.io.formats.style import Styler

# My packages
# This is tricky.
# We need runtime data such as the subpackage for the agency (amtrak, via, etc.)
# import timetable_kit.runtime_config

# And we need a shorthand way to refer to it
from timetable_kit.runtime_config import agency as agency

# If we don't use the "as", calls to agency() will "None" out

from timetable_kit import icons
from timetable_kit import text_presentation
from timetable_kit import connecting_services

from timetable_kit.errors import InputError
from timetable_kit.debug import debug_print
from timetable_kit.tsn import train_spec_to_tsn

# These are for finish_html_timetable
from timetable_kit.load_resources import (
    get_font_css,
    template_environment,
)


def get_time_column_stylings(
    train_spec, route_from_train_spec, output_type="attributes"
):
    """
    Return a set of CSS attributes or classes to style the header of this column, based on the trains_spec.

    train_spec: trip_short_name / train number, maybe with day suffix
    route_from_train_spec: route which takes a tsn and gives the row from the GTFS routes table corresponding to the tsn
    (This is needed because tsn to route mapping is expensive and must be done in the calling function)

    This mostly picks a color.

    If out_type is "attribute", prints the attributes -- used for the header cells.  This is the default.
    If out_type is "class", prints a class instead of an attribute -- used for cells.

    Note that these two colors may be complementary rather than identical.  (But this is not the case right now.)
    """
    if output_type not in ["class", "attributes"]:
        raise InputError("expected class or attributes")

    if agency() is None:
        raise RuntimeError(
            "Internal error, agency not set before calling get_time_column_stylings"
        )

    # Note that Amtrak GTFS data only has route_types:
    # 2 (is a train)
    # 3 (is a bus)
    # TODO: look up the color_css from the color_css_class by reading the template?
    # Currently these have to match up with the colors in templates/
    route_type = route_from_train_spec(train_spec).route_type
    tsn = train_spec_to_tsn(train_spec)
    if route_type == 3:
        # it's a bus!
        color_css = "background-color: honeydew;"
        color_css_class = "color-bus"
    elif agency().is_connecting_service(tsn):
        # it's not a bus, it's a connecting train!
        color_css = "background-color: blanchedalmond;"
        color_css_class = "color-connecting-train"
    elif agency().is_sleeper_train(tsn):
        color_css = "background-color: lavender;"
        color_css_class = "color-sleeper"
    elif agency().is_high_speed_train(tsn):
        color_css = "background-color: aliceblue;"
        color_css_class = "color-high-speed-train"
    else:
        color_css = "background-color: cornsilk;"
        color_css_class = "color-day-train"
    if output_type == "class":
        return color_css_class
    else:
        return color_css


def style_timetable_for_html(
    timetable, styler_df, table_classes="", table_uuid="main_timetable"
):
    """
    Take a timetable DataFrame, with parallel styler DataFrame, and separate header styler map, and style it for output.

    table_classes is a string of extra CSS classes to add to the table; it will always have 'tt-table'.
    """

    # There's an unpleasant issue here if we want to generate multipage timetables in HTML.  FIXME.
    # We have to attach the header codes by row & column (Jinja2 for PANDAS won't do mix-in classes).
    # But that means each timetable needs a *unique* class so the CSS can catch it.
    # Or the ID selector can be used (#table_id) but that still requires a unique ID,
    # which is known to the header styling CSS generator.  FIXME!
    # Possibly we need to pull this ID out of the JSON file?

    table_classes += " tt-table"
    table_attributes = f'class="{table_classes}"'

    # Note that the styler doesn't escape HTML per default --> yay
    # Make the table more readable by not using cell IDs.
    # Load the table attributes up front, to apply the table-wide border attributes
    # I was passing uuid_len=0, but I don't know why
    s0 = Styler(data=timetable, cell_ids=False, table_attributes=table_attributes)
    # N. B. !!! It is essential to have the tt-table class for border-collapse.
    # Border-collapse doesn't work when applied to an ID
    # and must be applied to "table" (not td/th) or to a class defined on a table.

    # Remove headings: index is arbitrary numbers, not interesting to the final reader;
    # column headers aren't elegant enough for us, so we build our own 'header' in the top row
    # s1 = s0.hide_index().hide_columns()

    # Screen readers want column headers.  It is *impossible* to add classes to the column headers,
    # without redoing the Jinja2 template (which we will probably do eventually).  FIXME.

    # We do not want the row headers.
    s1 = s0.hide(axis="index")
    # Apply the styler classes.  This is where the main work is done.
    s2 = s1.set_td_classes(styler_df)

    # Produce HTML.
    # Need to add ARIA role to the table, which means we have to manually define the table class.  SIGH!
    table_attrs = 'class="tt-table" role="main" aria-label="Timetable" '  # FIXME: the aria label should be more specific
    # Specify the ID to avoid it being randomly generated on each run
    styled_timetable_html = s2.to_html(
        table_attributes=table_attrs, table_uuid=table_uuid
    )

    # NOTE That this generates an unwanted blank style sheet...
    unwanted_prefix = """<style type="text/css">
</style>
"""
    styled_timetable_html = styled_timetable_html.removeprefix(unwanted_prefix)
    return styled_timetable_html


def make_header_styling_css(header_styling_list) -> str:
    """
    Given a list of strings, which maps from column numbers (the index) to CSS attributes, return suitable CSS.

    Assumes PANDAS-standard classes col_heading, col0, col1, etc.  I see no other way to do it.  :-(
    """
    accumulated_css = ""
    # The CSS selector is: a descendant of .tt_table which is both th, .col_heading, and .col0 (or whatever number)
    for col_num, attributes in enumerate(header_styling_list):
        this_css = f".tt-table th.col_heading.col{col_num} {{ {attributes} }}\n"
        accumulated_css += this_css
    return accumulated_css


def finish_html_timetable(
    styled_timetable_html,
    header_styling_list,
    *,
    author,
    aux=None,
    _for_weasyprint=False,
    box_time_characters=False,
    start_date,
    end_date,
    station_codes_list,  # For connecting services key
):
    """
    Take the output of style_timetable_for_html and make it a full HTML file with embedded CSS.

    The header_styling_list has CSS attributes (not classes) for each header column
    (indexed by zero-based column number).  This is due to inefficiencies in PANDAS.

    The mandatory "author" argument gives the author of the timetable.
    """

    header_styling_css = make_header_styling_css(header_styling_list)

    if aux is None:
        aux = {}  # Empty dict

    # We need to add the extras to make this a full HTML & CSS file now.
    # We're going to feed the entire aux file through, but we need some defaults
    aux.setdefault("title", "A Timetable")
    aux.setdefault("heading", "A Timetable")
    aux.setdefault("landscape", "Landscape orientation")

    connecting_services_one_line = True
    if "key_on_right" in aux:
        debug_print(1, "Key on right")
        connecting_services_one_line = False

    # FONTS
    font_name = "SpartanTT"
    font_size = "6pt"
    font_is_tiny = True

    debugging_fonts = True
    if debugging_fonts:
        # This makes it obvious when a font doesn't load
        backup_font_name = "cursive"
    else:
        backup_font_name = "sans-serif"

    # The @font-face directives:
    font_faces_css = get_font_css(font_name)

    # ICONS

    # For icons as imgs.
    # Get the CSS for styling icons (contains vertical alignment and 1em height/width)
    # This is used every time an icon is inserted...
    icons_css = icons.get_css_for_all_icons()

    # For connecting service logos as imgs:
    logos_css = connecting_services.get_css_for_all_logos()

    # Key for connecting services:
    # First use the station codes list to get a list of all *relevant* services
    services_list = agency().get_all_connecting_services(station_codes_list)
    # Then feed that through to get the full key html:
    connecting_services_keys_html = connecting_services.get_keys_html(
        services_list=services_list, one_line=connecting_services_one_line
    )

    # NOTE: We would like to try the alternative embedded SVG version.
    # But Weasy can't handle SVG references within HTML.

    ### Prepare Jinja template substitution:

    stylesheet_params = {
        "font_faces": font_faces_css,
        "font_name": font_name,
        "backup_font_name": backup_font_name,
        "font_size": font_size,  # 6pt
        "font_is_tiny": font_is_tiny,  # True
        "icons": icons_css,
        "logos": logos_css,
        "header_styling": header_styling_css,
        "box_time_characters": box_time_characters,
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
        "gtfs_url": agency().published_gtfs_url,  # e.g. URL to Amtrak GTFS
        "agency_name": agency().published_name,  # e.g. "Amtrak"
        "agency_names_or": agency().published_names_or,  # e.g. "Amtrak" -- "Amtrak or VIA Rail" for Maple Leaf
        "agency_names_and": agency().published_names_and,  # e.g. "Amtrak" -- "Amtrak and VIA Rail" for Maple Leaf
        "agency_website": agency().published_website,  # e.g. "Amtrak.com" -- with capitalization, no https://
        "agency_css_class": agency().css_class,  # e.g. amtrak-special-css -- currently just changes header color
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
