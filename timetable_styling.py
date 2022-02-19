# timetable_styling.py
# Part of timetable_kit
# Copyright 2021 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.


# Other people's packages
import pandas as pd
from pandas.io.formats.style import Styler

# BIG workaround here.  Border-collapse will not work with an ID specified.
# This stylesheet (global variable) will be prepended to HTML output.
# The class "timetable-css-class" must match the one assigned to the table
# in the Styler.

separate_stylesheet = '''
@page {
    /* For printing */
    size: Letter; /* change from default A4, since this is the US */
    margin: 1cm; /* Default margins vary in PDF generators.  This is safe for printing. */
}
.heading-font {
    font-weight: bold;
}
strong {
    font-size: 200%;
    font-weight: bold;
}
.major-station {
    text-transform: uppercase;
    font-weight: bold;
    font-size: normal;
}
.minor-station {
    font-weight: normal;
}
.station-footnotes {
    font-weight: normal;
/* This does not work with weasyprint: font-size: smaller; */
    font-size: 80%;
}
.color-cornsilk {
    background-color: cornsilk;
}
.tt-table {
    border-collapse: collapse;
}
.align-top {
    vertical-align: top;
}
.align-vcenter {
    vertical-align: center;
}
.align-bottom {
    vertical-align: bottom;
}
.align-left {
    text-align: left;
}
.align-right {
    text-align: right;
}
.align-center {
    text-align: center;
}
.border-top-heavy {
    border-top-style: solid;
    border-top-width: 2px;
    border-top-color: black;
}
.border-bottom-heavy {
    border-bottom-style: solid;
    border-bottom-width: 2px;
    border-bottom-color: black;
}
.border-top-light {
    border-top-style: solid;
    border-top-width: 1px;
    border-top-color: gray;
}
.border-bottom-light {
    border-bottom-style: solid;
    border-bottom-width: 1px;
    border-bottom-color: gray;
}
.border-left {
    border-left-style: solid;
    border-left-width: 2px;
    border-left-color: black;
}
.noborder-left {
    border-left-style: hidden
}
.border-right {
    border-right-style: solid;
    border-right-width: 2px;
    border-right-color: black;
}
.noborder-right {
    border-right-style: hidden
}
'''

# There are recurrent differences between the way the fonts and tables
# are rendered in web browsers vs. PDF converters, affecting sizes.
# So we specify one variant of the CSS for screen display,
# and a different one if we're printing to PDF.

# HOWEVER -- most PDF converters are better at font sizes than they appear,
# because most PDF viewers display the PDFs at the wrong size!
# Okular, for instance, is only "correct" size if displayed at 90%!

# The baseline font choice is always DejaVu Sans, which is basically
# Bitstream Vera Sans but with more codepoints.
# Other fonts to consider include Quicksand (pretty, art-decoish)
# and Liberation Sans (good, but uglier I think)

font_size_screen_css='''
.font-sans-serif {
    font-family: "DejaVu Sans", "Bitstream Vera Sans", sans-serif;
}
.font-data-size {
    /* Font size for screen use */
    /* Amtrak's old timetables were basically 6 pt, or maybe even smaller */
    /* But that's unnecessarily grim for screen use, probably */
    font-size: 10pt;
}
'''
font_size_weasyprint_css='''
.font-sans-serif {
    font-family: "Deja Vu Sans", "Bitstream Vera Sans", sans-serif;
}
.font-data-size {
    /* Font size for feeding through weasyprint */
    font-size: 10pt;
}
'''

def style_timetable_for_html(timetable, styler):
    ''' Take a timetable DataFrame with parallel styler DataFrame and style it for output. '''
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
    s1 = s0.hide_index().hide_columns()
    # Apply the styler classes.  This is where the main work is done.
    s2 = s1.set_td_classes(styler)
    styled_timetable_html = s2.render()
    return styled_timetable_html;

# Start of HTML document
html_header='''<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
'''

def finish_html_timetable(styled_timetable_html, title="", for_weasyprint=False):
    ''' Take the output of style_timetable_for_html and make it a full HTML file with embedded CSS.'''

    # We need to add the extras to make this a full HTML & CSS file now.
    if not title:
        title="An Amtrak Timetable" # FIXME
    # We have to make the font sizes different for weasyprint to make it come out
    # the same size as screen output (bug in weasyprint)
    if for_weasyprint:
        font_size_css = font_size_weasyprint_css
    else:
        font_size_css = font_size_screen_css

    # We write and prepend an entirely separate stylesheet.
    # We MUST prepend the border-collapse part of the stylesheet, since the styler can't do it.
    finished_timetable_html = '\n'.join([html_header,
                                         "<title>",
                                         title,
                                         "</title>",
                                         "<style>",
                                         separate_stylesheet,
                                         font_size_css,
                                         "</style>",
                                         "</head><body>",
                                         styled_timetable_html,
                                         "</body></html>",
                                        ])
    return finished_timetable_html

def amtrak_station_name_to_multiline_text(station_name: str, major=False ) -> str:
    '''
    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable text version (possibly multiple lines)
    If "major", then make the station name bigger and bolder
    We want to avoid very long lines as they mess up timetable formats
    '''
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
    '''
    The easy one.
    Station name to single line text.
    '''
    if (major):
        return station_name.upper()
    else:
        return station_name

def amtrak_station_name_to_html(station_name: str, major=False ) -> str:
    '''
    Given an Amtrak station name in one of these two forms:
    Champaign-Urbana, IL (CHM)
    New Orleans, LA - Union Passenger Terminal (NOL)
    Produce a pretty-printable HTML version
    If "major", then make the station name bigger and bolder
    '''

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

