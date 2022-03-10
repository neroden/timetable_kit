# timetable_styling.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Style a timetable.

This module uses Pandas's Styler to apply CSS classes to a timetable;
then renders HTML, including a lot of complicated extra bits.

This uses a bunch of CSS files, and a few HTML files, in the "fragments" folder.

"""

# Other people's packages
import pandas as pd
from pandas.io.formats.style import Styler

# My packages
import amtrak_helpers

def get_time_column_stylings(trains_spec, type="attributes"):
    """
    Return a set of CSS attributes or classes to style the header of this column, based on the trains_spec.

    In practice, trains_spec is currently a train number (trip_short_name).

    This mostly picks a color.

    If type is "attribute", prints the attributes -- used for the header cells.  This is the default.
    If type is "class", prints a class instead of an attribute -- used for cells.

    Note that these two colors may be complementary rather than identical.  (But this is not the case right now.)
    """
    if (type not in ["class", "attributes"]):
        raise InputError("expected class or attributes")

    train_number = trains_spec # Because we aren't parsing trains_spec yet -- FIXME
    if amtrak_helpers.is_sleeper_train(train_number):
        color_css = "background-color: thistle;"
        color_css_class = "color-sleeper" # thistle
    elif amtrak_helpers.is_bus(train_number):
        color_css = "background-color: darkseagreen;"
        color_css_class = "color-bus"
    else:
        color_css = "background-color: cornsilk;"
        color_css_class = "color-day-train"
    if (type == "class"):
        return color_css_class
    else:
        return color_css

def style_timetable_for_html(timetable, styler_df, table_classes=""):
    """
    Take a timetable DataFrame, with parallel styler DataFrame, and separate header styler map, and style it for output.

    table_classes is a string of extra CSS classes to add to the table; it will always have 'tt-table'.
    """

    table_classes += ' tt-table'
    table_attributes = ''.join(['class="',table_classes,'"'])

    # Note that the styler doesn't escape HTML per default --> yay
    # Make the table more readable by not using cell IDs.
    # Load the table attributes up front, to apply the table-wide border attributes
    # I was passing uuid_len=0, but I don't know why
    s0 = Styler(data=timetable, cell_ids=False,
                table_attributes=table_attributes)
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
    table_attrs = 'class="tt-table" role="main" aria-label="Timetable" ' # FIXME: the aria label should be more specific
    styled_timetable_html = s2.to_html(table_attributes=table_attrs)

    # NOTE That this generates an unwanted blank style sheet...
    unwanted_prefix='''<style type="text/css">
</style>
'''
    styled_timetable_html = styled_timetable_html.removeprefix(unwanted_prefix)
    return styled_timetable_html;


def make_header_styling_css(header_styling_list) -> str:
    """
    Given a list of strings, which maps from column numbers (the index) to CSS attributes, return suitable CSS.

    Assumes PANDAS-standard classes col_heading, col0, col1, etc.  I see no other way to do it.  :-(
    """
    accumulated_css=""
    # The CSS selector is: a descendant of .tt_table which is both th, .col_heading, and .col0 (or whatever number)
    for col_num, attributes in enumerate(header_styling_list):
        this_css = ''.join([ ".tt-table th.col_heading.col", str(col_num), " { ", attributes, " }\n" ])
        accumulated_css += this_css
    return accumulated_css

# Start of HTML document
html_header='''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
'''

def finish_html_timetable(styled_timetable_html, header_styling_list, title="", for_weasyprint=False):
    """
    Take the output of style_timetable_for_html and make it a full HTML file with embedded CSS.

    The header_styling_list has CSS attributes (not classes) for each header column
    (indexed by zero-based column number).  This is due to inefficiencies in PANDAS.
    """

    header_styling_css = make_header_styling_css(header_styling_list)

    # Directory containing CSS and HTML fragments
    fragments_dirname = "./fragments/"

    # We need to add the extras to make this a full HTML & CSS file now.
    if not title:
        title="An Amtrak Timetable" # FIXME

    # CSS for the whole page, not an individual table
    with open(fragments_dirname + "page.css", "r") as file:
        page_css = file.read()

    # Main CSS for the actual timetable
    with open(fragments_dirname + "timetable_main.css", "r") as file:
        timetable_main_css = file.read()
    # Main CSS for the headers
    with open(fragments_dirname + "timetable_headers.css", "r") as file:
        timetable_headers_css = file.read()
    # CSS for the colors
    with open(fragments_dirname + "timetable_colors.css", "r") as file:
        timetable_colors_css = file.read()

    # And the specific internal pseudo-table layout for the individual cells displaying times:
    with open(fragments_dirname + "time_boxes_extras.css", "r") as file:
        time_boxes_extras_css = file.read()

    box_characters=True # FIXME, pass this down
    if (box_characters):
        if (for_weasyprint):
            with open(fragments_dirname + "time_box_characters_weasy.css", "r") as file:
                time_boxes_main_css = file.read()
        else: # not for_weasyprint
            with open(fragments_dirname + "time_box_characters.css", "r") as file:
                time_boxes_main_css = file.read()
    else: # not box_characters
        with open(fragments_dirname + "time_boxes_simple.css", "r") as file:
            time_boxes_main_css = file.read()

    # Get the symbol key and its associated CSS
    with open(fragments_dirname + "symbol_key.html", "r") as file:
        symbol_key_html = file.read()
    with open(fragments_dirname + "symbol_key.css", "r") as file:
        symbol_key_css = file.read()

    # fonts:
    # We may want different fonts and font sizes for screen and print.
    if for_weasyprint:
        with open(fragments_dirname + "font_choice_screen.css", "r") as file:
            font_choice_css = file.read()
        with open(fragments_dirname + "font_size_screen.css", "r") as file:
            font_size_css = file.read()
    else:
        # ...but for now, use the same font_choice
        with open(fragments_dirname + "font_choice_screen.css", "r") as file:
            font_choice_css = file.read()
        with open(fragments_dirname + "font_size_screen.css", "r") as file:
            font_size_css = file.read()

    # The @font-face directives:
    fonts_dirname = "./fonts/"
    fonts_css_list = []
    for font in ["Spartan",
#                    "Spartan_MB",
#                    "Spartan1004",
                    "SpartanTT",
                ]:
        with open(fonts_dirname + font + ".css", "r") as file:
            fonts_css_list.append( file.read() )
    fonts_css = ''.join(fonts_css_list)

    # Icons:
    icons_dirname = "./icons/"
    # Get the CSS for styling icons (contains vertical alignment and 1em height/width)
    # This is used every time an icon is inserted...
    with open(icons_dirname + "icons.css", "r") as file:
        icons_css = file.read()
    # This allowed embedded SVGs, but Weasyprint can't handle it.
    # Consider doing two versions, one for Weasy, one not for Weasy (yee-haw! FIXME)
    # Get the hidden SVGs to prepend to the HTML file, which are referenced in the later HTML
    # 'baggage' is the only one so far
    # svg_symbols_html = ""
    # with open(icons_dirname + "suitcase-solid.svg", "r") as baggage_svg_file:
    #     svg_symbols_html += baggage_svg_file.read()

    # We write and prepend an entirely separate stylesheet.
    # We MUST prepend the border-collapse part of the stylesheet, since the styler can't do it.
    finished_timetable_html = '\n'.join([html_header,
                                         "<title>",
                                         title,
                                         "</title>",
                                         "<style>",
                                         page_css,
                                         fonts_css,
                                         font_choice_css,
                                         font_size_css,
                                         icons_css,
                                         timetable_main_css,
                                         timetable_headers_css,
                                         header_styling_css,
                                         timetable_colors_css,
                                         time_boxes_main_css,
                                         time_boxes_extras_css,
                                         symbol_key_css,
                                         "</style>",
                                         "</head><body>",
                                         styled_timetable_html,
                                         symbol_key_html,
                                         "</body></html>",
                                        ])
    return finished_timetable_html

def amtrak_station_name_to_multiline_text(station_name: str, major=False ) -> str:
    """
    Produce pretty Amtrak station name for plaintext -- multi-line.

    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable text version (possibly multiple lines)
    If "major", then make the station name bigger and bolder
    We want to avoid very long lines as they mess up timetable formats
    """
    if (" - " in station_name):
        (city_state_name, second_part) = station_name.split(" - ", 1)
        (facility_name, suffix) = second_part.split(" (", 1)
        (station_code, junk) = suffix.split(")",1)
    else:
        facility_name = None
        (city_state_name, suffix) = station_name.split(" (", 1)
        (station_code, junk) = suffix.split(")",1)

    if (major):
        enhanced_city_state_name = city_state_name.upper()
    else:
        enhanced_city_state_name = city_state_name

    enhanced_station_code = ''.join(["(", station_code, ")"])

    if (facility_name):
        enhanced_facility_name = ''.join(["\n", " - ", facility_name])
    else:
        enhanced_facility_name = ''

    fancy_name = ''.join([enhanced_city_state_name,
                          " ",
                          enhanced_station_code,
                          enhanced_facility_name
                         ])
    return fancy_name

def amtrak_station_name_to_single_line_text(station_name: str, major=False ) -> str:
    """
    Produce pretty Amtrak station name for plaintext -- single line.

    The easy version.  Station name to single line text.
    """
    if (major):
        return station_name.upper()
    else:
        return station_name

def amtrak_station_name_to_html(station_name: str, major=False ) -> str:
    """
    Produce pretty Amtrak station name for HTML -- potentially multiline, and complex.

    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable HTML version
    If "major", then make the station name bigger and bolder
    """

    if (" - " in station_name):
        (city_state_name, second_part) = station_name.split(" - ", 1)
        (facility_name, suffix) = second_part.split(" (", 1)
        (station_code, junk) = suffix.split(")",1)
    else:
        facility_name = None
        (city_state_name, suffix) = station_name.split(" (", 1)
        (station_code, junk) = suffix.split(")",1)

    if (major):
        enhanced_city_state_name = ''.join(["<span class=major-station >",
                                            city_state_name,"</span>"])
    else:
        enhanced_city_state_name = ''.join(["<span class=minor-station >",
                                            city_state_name,"</span>"])

    enhanced_station_code = ''.join(["<span class=station-footnotes>(",
                                     station_code,")</span>"])

    if (facility_name):
        enhanced_facility_name = ''.join(["<br><span class=station-footnotes>",
                                          " - ", facility_name,"</span>"])
    else:
        enhanced_facility_name = ''

    fancy_name = ' '.join([enhanced_city_state_name,
                           enhanced_station_code,
                           enhanced_facility_name
                          ])
    return fancy_name

