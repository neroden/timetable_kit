#! /usr/bin/python3
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
separate_stylesheet = '''<style type="text/css">
strong {
    font-size: 200%;
    font-weight: bold;
}
.tt-table {
    border-collapse: collapse;
}
.color-cornsilk {
    background-color: cornsilk;
}
.heading-font {
    font-weight: bold;
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
</style>
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
    # We write and prepend an entirely separate stylesheet.
    # We MUST prepend the border-collapse part of the stylesheet, since the styler can't do it.
    finished_timetable_html = ''.join([separate_stylesheet, styled_timetable_html])
    return finished_timetable_html
