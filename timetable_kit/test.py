#! /usr/bin/env python3
# test.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Run temporary testing code.

Not intended for production use.
"""

# Other people's packages
import argparse
import pandas as pd
import gtfs_kit as gk
import json

# My packages
from timetable_kit.errors import (
    GTFSError,
    NoStopError,
    TwoStopsError,
    NoTripError,
    TwoTripsError,
    InputError
)
from timetable_kit.debug import (set_debug_level, debug_print)
from timetable_kit.timetable_argparse import make_tt_arg_parser

# This one monkey-patches gk.Feed (sneaky) so must be imported early
from timetable_kit import feed_enhanced

# To intialize the feed -- does type changes
from timetable_kit.initialize import initialize_feed

from timetable_kit import amtrak # so we don't have to say "timetable_kit.amtrak"

# Hack for the testing file -- pretend we're in timetable.py
from timetable_kit.timetable import *

# For testing!
from timetable_kit import text_presentation

if __name__ == "__main__":
    debug_print (3, "Dumping sys.path for clarity:", sys.path )

    my_arg_parser = make_tt_arg_parser()
    args = my_arg_parser.parse_args()

    set_debug_level(args.debug)
    output_dirname = args.output_dirname

    gtfs_filename = args.gtfs_filename
    master_feed = initialize_feed(gtfs=gtfs_filename)

    reference_date = args.reference_date
    debug_print(1, "Working with reference date ", reference_date, ".", sep="")

    quit()

    # Generate routes.html
    debug_print(1, "Dumping routes.html")
    routes_html_path = Path(output_dirname) / "routes.html"
    with open(routes_html_path,'w') as outfile:
        print(master_feed.routes.to_html(), file=outfile)

    # Put testing code HERE
    debug_print(1, "Testing calendar dump")
    new_feed = master_feed.filter_remove_one_day_calendars()
    printable_calendar = gtfs_type_cleanup.type_uncorrected_calendar(new_feed.calendar)
    module_dir = Path(__file__).parent
    printable_calendar.to_csv( module_dir / "amtrak/gtfs/calendar_stripped.txt", index=False)
    print ("calendar without one-day calendars created")
    quit()

    tt_spec = load_tt_spec(args.tt_spec_filename)
    tt_spec = augment_tt_spec(tt_spec, feed=master_feed, date=reference_date)
    dwell_secs = get_dwell_secs("59","CDL")
    print("Dwell is", dwell_secs)
    quit()

