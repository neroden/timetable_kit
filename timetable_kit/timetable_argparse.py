#! /usr/bin/env python3
# timetable_argparse.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Argument parser for timetable.py

The primary function for external use is make_tt_arg_parser.

Also includes routines for adding common arguments to parsers for other commands.
"""

import argparse

# Needed for defaulting the reference date to tomorrow:
import datetime

# Needed for defaulting the GTFS file:
from timetable_kit import amtrak

# Determine defaults in initialization code here:
default_gtfs_filename = amtrak.gtfs_unzipped_local_path
# Use tomorrow as the default reference date.
# After all, you aren't catching a train today, right?
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
default_reference_date = int( tomorrow.strftime('%Y%m%d') )

def add_gtfs_argument(parser: argparse.ArgumentParser):
    """Add the common --gtfs argument to a parser"""
    parser.add_argument('--gtfs','-g',
        dest='gtfs_filename',
        help='''Directory containing GTFS static data files,
                or zipped GTFS static data feed,
                or URL for zipped GTFS static data feed;
                default is Amtrak''',
        default = default_gtfs_filename,
        )

def add_date_argument(parser: argparse.ArgumentParser):
    """Add the common --date argument to a parser"""
    parser.add_argument('--reference-date','--date','-d',
        dest='reference_date',
        help="""Reference date.
                GTFS data contains timetables for multiple time periods;
                this produces the timetable valid as of the reference date.
             """,
        type = int,
        default = default_reference_date,
        )

def add_debug_argument(parser: argparse.ArgumentParser):
    """Add the common --debug argument to a parser"""
    parser.add_argument('--debug',
        dest='debug',
        help="Set debugging level, from 0 to 3 (default 1)",
        type=int,
        action='store',
        default=1,
        )

def add_output_dirname_argument(parser: argparse.ArgumentParser):
    parser.add_argument('--output-directory','-o',
        dest='output_dirname',
        help="Directory to put output HTML timetable files in.  Default is current directory.",
        default=".",
        )

def make_tt_arg_parser():
    """Make argument parser for timetable.py"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Produce printable HTML timetable from a .tt-spec file.""",
        )
    add_gtfs_argument(parser)
    add_date_argument(parser)
    add_debug_argument(parser)
    add_output_dirname_argument(parser)
    parser.add_argument('--spec','-l',
        dest='tt_spec_filename',
        help="""CSV file containing tt-spec template for timetable.
                The tt-spec format is a work in progress.
                For more information see the specifications.  Brief summary:
                Top row should have a train number, "stations", or "services" in each column except the first.
                Second row may have "column-options" in the first column and special codes in the other columns.
                Left column should have a station code in every row except the first & second,
                or be blank to pass through text on this row to the final timetable.
                The center of the timetable will be filled in according to the train number and station code.
             """,
        )
    parser.add_argument("--author", "-a",
        dest="author",
        help="""Name of the person generating the timetable.
                This is mandatory!
             """,
        )
    return parser;

# Testing code
if __name__ == "__main__":
    print("Testing argument parser:")
    parser = make_tt_arg_parser()
    args = parser.parse_args()
    print("GTFS Filename: " + str(args.gtfs_filename))
    print("Reference Date: " + str(args.reference_date))
    print("Output Dirname: " + str(args.output_dirname))
