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
# import datetime

# Needed for defaulting the GTFS file:
from timetable_kit import amtrak

# Determine defaults in initialization code here:
default_gtfs_filename = amtrak.gtfs_unzipped_local_path

# Default reference date removed.
# Reference date now overrides the .tt-aux file,
# so we want to be able to omit it and trust the .tt-aux file.
#
# Use tomorrow as the default reference date.
# After all, you aren't catching a train today, right?
# tomorrow = datetime.date.today() + datetime.timedelta(days=1)
# default_reference_date = int(tomorrow.strftime("%Y%m%d"))


def add_gtfs_argument(parser: argparse.ArgumentParser):
    """Add the common --gtfs argument to a parser"""
    parser.add_argument(
        "--gtfs",
        "-g",
        dest="gtfs_filename",
        help="""Directory containing GTFS static data files,
                or zipped GTFS static data feed,
                or URL for zipped GTFS static data feed;
                default is Amtrak""",
        default=default_gtfs_filename,
    )


def add_date_argument(parser: argparse.ArgumentParser):
    """Add the common --date argument to a parser"""
    parser.add_argument(
        "--reference-date",
        "--date",
        "-d",
        dest="reference_date",
        help="""Reference date.
                GTFS data contains timetables for multiple time periods;
                this produces the timetable valid as of the reference date.
                This overrides any reference date set in the .tt-aux file.
                Should be in YYYYMMDD format.
             """,
        type=int,
    )


def add_debug_argument(parser: argparse.ArgumentParser):
    """Add the common --debug argument to a parser"""
    parser.add_argument(
        "--debug",
        dest="debug",
        help="Set debugging level, from 0 to 3 (default 1)",
        type=int,
        action="store",
        default=1,
    )


def add_output_dirname_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--output-directory","--output-dir",
        "-o",
        dest="output_dirname",
        help="Directory to put output HTML timetable files in.  Default is current directory.",
        default=".",
    )

def add_input_dirname_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--input-directory","--input-dir",
        "-i",
        dest="input_dirname",
        help="Directory to find input .tt-spec / .tt-aux files in.  Default is not to prefix a directory (use system default for lookup of files)",
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
    add_input_dirname_argument(parser)
    parser.add_argument(
        "--spec","--specs",
        "-l",
        dest="tt_spec_files",
        help="""Root of name of timetable spec file.
                If you type "--spec cono", then "cono.tt-spec" and "cono.tt-aux" files should exist.
                The tt-spec and tt-aux formats remain a work in progress.
                For more information see the file tt-spec-documentation.rst.

                You may specify several spec files at once to generate multiple timetables.
                The spec files must all be in the same input directory.
             """,
        nargs = "+", # 1 or more filenames
    )
    parser.add_argument(
        "--author",
        "-a",
        dest="author",
        help="""Name of the person generating the timetable.
                This is mandatory!
             """,
    )
    return parser


# Testing code
if __name__ == "__main__":
    print("Testing argument parser:")
    parser = make_tt_arg_parser()
    args = parser.parse_args()
    print("GTFS Filename: " + str(args.gtfs_filename))
    print("Reference Date: " + str(args.reference_date))
    print("Output Dirname: " + str(args.output_dirname))
