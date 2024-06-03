# timetable_styling.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Support for applying CSS classes to a timetable.

The main work is done in fill_tt_spec.
This has support routines for finding class types to apply.

This module handles the actual *table*. For the text which goes around it and the key,
see the page_layout module.
"""

# My packages
from timetable_kit.debug import debug_print
from timetable_kit.tsn import train_spec_to_tsn

# We need the agency singleton (amtrak, via, etc.)
from timetable_kit.runtime_config import agency_singleton


def get_time_column_stylings(train_spec, route_from_train_spec) -> str:
    """Return a set of CSS classes to style the header of this column,
    based on the trains_spec.

    train_spec: trip_short_name / train number, maybe with day suffix
    route_from_train_spec: route which takes a tsn and gives the row from the GTFS routes table corresponding to the tsn
    (This is needed because tsn to route mapping is expensive and must be done in the calling function)

    This mostly picks a color.

    Consider using complementary but different header and data cell colors.  (Not done right now.)
    """
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
        color_css_class = "color-bus"
    elif agency_singleton().is_connecting_service(tsn):
        # it's not a bus, it's a connecting train!
        color_css_class = "color-connecting-train"
    elif agency_singleton().is_sleeper_train(tsn):
        # Note that this should come first and overrride is_specially_colored train
        color_css_class = "color-sleeper"
    elif agency_singleton().is_high_speed_train(tsn):
        color_css_class = "color-high-speed-train"
    elif agency_singleton().is_specially_colored_train(tsn):
        # This is used to distinguish connecting services on the Valley Flyer timetable
        # Currently triggers for Hartford Line, Valley Flyer, and LSL / Texas Eagle branches
        color_css_class = "color-specially-colored-train"
    else:
        color_css_class = "color-day-train"
    return color_css_class
