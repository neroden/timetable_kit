# timetable_styling.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Style a timetable.

This module uses Pandas's Styler to apply CSS classes to a timetable;
then renders HTML, including a lot of complicated extra bits.

This uses a bunch of CSS files, and a few HTML files, in the "fragments" folder.
This uses Jinja2, via the load_resources module.

"""

# Other people's packages
import datetime  # for getting today's date for credit on the timetable
import pandas as pd
from pandas.io.formats.style import Styler

# My packages
# This imports the subpackage by name so we can just call it "amtrak"
from timetable_kit import amtrak
from timetable_kit import icons
from timetable_kit import text_presentation

from timetable_kit.errors import InputError
from timetable_kit.debug import debug_print

# These are for finish_html_timetable
from timetable_kit.load_resources import (
    get_font_css,
    template_environment,
)


def get_time_column_stylings(tsn, route_from_tsn, output_type="attributes"):
    """
    Return a set of CSS attributes or classes to style the header of this column, based on the trains_spec.

    tsn: trip_short_name / train number
    route_from_tsn: route which takes a tsn and gives the row from the GTFS routes table corresponding to the tsn
    (This is needed because tsn to route mapping is expensive and must be done in the calling function)

    This mostly picks a color.

    If out_type is "attribute", prints the attributes -- used for the header cells.  This is the default.
    If out_type is "class", prints a class instead of an attribute -- used for cells.

    Note that these two colors may be complementary rather than identical.  (But this is not the case right now.)
    """
    if output_type not in ["class", "attributes"]:
        raise InputError("expected class or attributes")

    # Note that Amtrak GTFS data only has route_types:
    # 2 (is a train)
    # 3 (is a bus)
    # TODO: look up the color_css from the color_css_class by reading the template?
    # Currently these have to match up with the colors in templates/
    route_type = route_from_tsn(tsn).route_type
    if route_type == 3:
        # it's a bus!
        color_css = "background-color: honeydew;"
        color_css_class = "color-bus"
    elif amtrak.special_data.is_connecting_service(tsn):
        # it's not a bus, it's a connecting train!
        color_css = "background-color: blanchedalmond;"
        color_css_class = "color-connecting-train"
    elif amtrak.special_data.is_sleeper_train(tsn):
        color_css = "background-color: lavender;"
        color_css_class = "color-sleeper"
    else:
        color_css = "background-color: cornsilk;"
        color_css_class = "color-day-train"
    if output_type == "class":
        return color_css_class
    else:
        return color_css


def style_timetable_for_html(timetable, styler_df, table_classes=""):
    """
    Take a timetable DataFrame, with parallel styler DataFrame, and separate header styler map, and style it for output.

    table_classes is a string of extra CSS classes to add to the table; it will always have 'tt-table'.
    """

    table_classes += " tt-table"
    table_attributes = "".join(['class="', table_classes, '"'])

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
    styled_timetable_html = s2.to_html(table_attributes=table_attrs)

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
        this_css = "".join(
            [".tt-table th.col_heading.col", str(col_num), " { ", attributes, " }\n"]
        )
        accumulated_css += this_css
    return accumulated_css


def finish_html_timetable(
    styled_timetable_html,
    header_styling_list,
    *,
    author,
    aux=None,
    for_weasyprint=False,
    box_time_characters=False,
    start_date,
    end_date,
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
    if "title" not in aux:
        aux["title"] = "A Timetable"

    if "heading" not in aux:
        aux["heading"] = "A Timetable"

    if "landscape" in aux:
        debug_print(1, "Landscape orientation")

    if "key_on_right" in aux:
        debug_print(1, "Key on right")

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

    # The @font-face directives:
    fonts_css_list = []
    for font in [font_name]:
        fonts_css_list.append(get_font_css(font))
    font_faces_css = "".join(fonts_css_list)

    ### ICONS

    # For icons as imgs.
    # Get the CSS for styling icons (contains vertical alignment and 1em height/width)
    # This is used every time an icon is inserted...
    icons_css = icons.get_css_for_all_icons()

    # TODO FIXME: add the alternative embedded SVG version.
    # Weasy can't handle SVG references within HTML.
    # Get the hidden SVGs to prepend to the HTML file, which are referenced in the later HTML
    # 'baggage' is the only one so far
    # svg_symbols_html = ""
    # with open(icons_dirname + "suitcase-solid.svg", "r") as baggage_svg_file:
    #     svg_symbols_html += baggage_svg_file.read()

    ### Prepare Jinja template substitution:

    stylesheet_params = {
        "font_faces": font_faces_css,
        "font_name": font_name,
        "backup_font_name": backup_font_name,
        "font_size": font_size,  # 6pt
        "font_is_tiny": font_is_tiny,  # True
        "icons": icons_css,
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
        # FIXME hardcoded Amtrak URL here
        "gtfs_url": "https://www.transit.land/feeds/f-9-amtrak~amtrakcalifornia~amtrakcharteredvehicle",
    }

    # Allows direct icon references in Jinja2
    icon_params = {
        "baggage_icon": icons.get_baggage_icon_html(),
        "accessible_icon": icons.get_accessible_icon_html(),
        "inaccessible_icon": icons.get_inaccessible_icon_html(),
    }

    # Dictionary merge, html_params take priority, Python 3.9
    # Not sure about associativity, but we don't plan to have duplicates anyway
    # Throw the entire aux file in
    full_page_params = aux | stylesheet_params | icon_params | html_params

    # Get the Jinja2 template environment (set up in load_resources module)
    # and use it to retrieve the correct template (complete with many includes)...
    page_tpl = template_environment.get_template("page_standard.html")
    # ...then render it.
    finished_timetable_html = page_tpl.render(full_page_params)
    return finished_timetable_html
