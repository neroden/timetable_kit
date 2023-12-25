# timetable_styling.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Style a timetable.

This module uses Pandas's Styler to apply CSS classes to a timetable;
then renders HTML, including complicated extra bits.

This uses a bunch of CSS files, and a few HTML files, in the "fragments"
folder. This uses Jinja2, via the load_resources module.

This module handles the actual *table*. For the text which goes around
it and the key, see the page_layout module.
"""

# Other people's packages
import pandas as pd
from pandas.io.formats.style import Styler

# My packages
# This is tricky.
# We need runtime data such as the subpackage for the agency (amtrak, via, etc.)
import timetable_kit.runtime_config

# And we need a shorthand way to refer to it
from timetable_kit.runtime_config import agency
from timetable_kit.runtime_config import agency_singleton

from timetable_kit.errors import InputError
from timetable_kit.debug import debug_print
from timetable_kit.tsn import train_spec_to_tsn


def get_time_column_stylings(
    train_spec, route_from_train_spec, output_type="attributes"
):
    """Return a set of CSS attributes or classes to style the header of this
    column, based on the trains_spec.

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

    assert agency_singleton() is not None

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
    elif agency_singleton().is_connecting_service(tsn):
        # it's not a bus, it's a connecting train!
        color_css = "background-color: blanchedalmond;"
        color_css_class = "color-connecting-train"
    elif agency_singleton().is_sleeper_train(tsn):
        color_css = "background-color: lavender;"
        color_css_class = "color-sleeper"
    elif agency_singleton().is_high_speed_train(tsn):
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
    timetable,
    styler_df,
    table_uuid,
    table_classes="",
):
    """Take a timetable DataFrame, with parallel styler DataFrame, and separate
    header styler map, and style it for output.

    table_classes is a string of extra CSS classes to add to the table;
    it will always have 'tt-table'. table_uuid will have "T_" prefixed
    (by PANDAS) and be used as an id for the table.
    """

    # There's an unpleasant issue here if we want to generate multipage timetables in HTML.
    # We have to attach the header codes by row & column (Jinja2 for PANDAS won't do mix-in classes).
    # This means we have to use an ID selector with a unique ID, known to the header styling CSS generator.
    # This is what table_uuid is for.

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

    # The ID for the heading, so that we can do an ARIA cross-reference
    heading_id = "H_" + table_uuid
    # Want to add ARIA labelling to the table, which means we have to manually define the table class.  SIGH!
    # Note that aria labelling only works on an item with an explicit landmark role, so this must be "main".
    # Who knows whether this works!
    table_attrs = 'class="tt-table" role="main" aria-labelled-by="' + heading_id + '"'
    # Specify the ID to allow for multipage timetables.
    styled_timetable_html = s2.to_html(
        table_attributes=table_attrs, table_uuid=table_uuid
    )

    # NOTE That this generates an unwanted blank style sheet...
    unwanted_prefix = """<style type="text/css">
</style>
"""
    styled_timetable_html = styled_timetable_html.removeprefix(unwanted_prefix)
    return styled_timetable_html


def make_header_styling_css(header_styling_list, table_uuid: str) -> str:
    """Given a list of strings, which maps from column numbers (the index) to
    CSS attributes, return suitable CSS.

    Assumes PANDAS-standard classes col_heading, col0, col1, etc.  I see
    no other way to do it.  :-(

    The string table_uuid must be supplied. These styling columns apply
    to the table with the id "T_" + table_uuid (conforming to the way
    PANDAS makes the ids).
    """
    if not table_uuid:
        raise ValueError("table_uuid must be a nonempty string")

    top_selector = "#T_" + table_uuid

    accumulated_css = ""
    # The CSS selector is: a descendant of .tt_table or specified ID
    # which is both th, .col_heading, and .col0 (or whatever number)
    for col_num, attributes in enumerate(header_styling_list):
        this_css = "".join(
            [
                top_selector,
                " th.col_heading.col",
                str(col_num),
                " { ",
                attributes,
                " }\n",
            ]
        )
        accumulated_css += this_css
    return accumulated_css
