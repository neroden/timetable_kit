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

def style_timetable_for_html(timetable, styler):
    """Take a timetable DataFrame with parallel styler DataFrame and style it for output."""
    # Time to try the styler
    # Note that the styler doesn't escape HTML per default --> yay
    # Make the table more readable by not using cell IDs.
    # Load the table attributes up front, to apply the table-wide border attributes
    s0 = Styler(data=timetable, uuid_len=0, cell_ids=False,
                table_attributes='class="tt-table"')
    # N. B. !!! It is essential to have the tt-table class for border-collapse.
    # Border-collapse doesn't work when applied to an ID
    # and must be applied to "table" (not td/th) or to a class defined on a table.

    # Remove headings: index is arbitrary numbers, not interesting to the final reader;
    # column headers aren't elegant enough for us, so we build our own 'header' in the top row
    # s1 = s0.hide_index().hide_columns()

    # Aaargh, screen readers want column headers!  Find a way to style them SOMEHOW
    s1 = s0.hide_index()
    # Apply the styler classes.  This is where the main work is done.
    s2 = s1.set_td_classes(styler)

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

# Start of HTML document
html_header='''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
'''

def finish_html_timetable(styled_timetable_html, title="", for_weasyprint=False):
    """Take the output of style_timetable_for_html and make it a full HTML file with embedded CSS."""

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
    # And the specific internal pseudo-table layout for the individual cells displaying times:
    with open(fragments_dirname + "time_boxes_extras.css", "r") as file:
        time_boxes_extras_css = file.read()

    box_characters=True
    if (box_characters):
        if (for_weasyprint):
            with open(fragments_dirname + "time_box_characters.css", "r") as file:
                time_boxes_main_css = file.read()
        else: # not for_weasyprint
            with open(fragments_dirname + "time_box_characters_weasy.css", "r") as file:
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
    else:
        # ...but for now, use the same font_choice
        with open(fragments_dirname + "font_choice_screen.css", "r") as file:
            font_choice_css = file.read()

    # The @font-face directives:
    fonts_dirname = "./fonts/"
    fonts_css_list = []
    for font in ["Spartan_TMB","Spartan_MB","Spartan_MB_Web",
                "Spartan","League_Spartan",
                "Roboto", "Roboto_Condensed", "B612",
                "Open_Sans", "Clear_Sans",
                "Varela_Round", "Titillium_Web", "NationalPark",
                "Raleway", "Cantarell",
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
                                         font_choice_css,
                                         fonts_css,
                                         icons_css,
                                         timetable_main_css,
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

