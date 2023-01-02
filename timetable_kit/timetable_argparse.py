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

# Needed to store data including the agency subpackage (e.g. amtrak, via)
# from timetable_kit import runtime_config
# Is this actually done here?  No, it's done in the caller.

# Needed for defaulting the GTFS file:
from timetable_kit import amtrak

# Determine defaults in initialization code here:
default_gtfs_filename = amtrak.gtfs_unzipped_local_path


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
                This overrides any reference date set in the .json file in the tt-spec.
                Should be in YYYYMMDD format.
             """,
        type=str,
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
        "--output-directory",
        "--output-dir",
        "-o",
        dest="output_dirname",
        help="""Directory to put output HTML timetable files in.
                Default is current directory.
                You can also set it using the TIMETABLE_KIT_OUTPUT_DIR environment variable.
             """,
    )


def add_input_dirname_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--input-directory",
        "--input-dir",
        "-i",
        dest="input_dirname",
        help="""Directory to find input .csv / .json files (tt-spec files) in.
                Default is not to prefix a directory (use system default for lookup of files).
                You can also set it using the TIMETABLE_KIT_INPUT_DIR environment variable.
             """,
    )


def add_spec_files_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--spec",
        "--specs",
        "-l",
        dest="tt_spec_files",
        help="""Root of name of timetable spec file.
                If you type "--spec cono", then "cono.csv" and "cono.json" files should exist.
                The tt-spec format remains a work in progress.
                For more information see the file tt-spec-documentation.rst.

                You may specify several spec files at once to generate multiple timetables.
                The spec files must all be in the same input directory.
             """,
        nargs="+",  # 1 or more filenames
        default=[],  # empty list
    )


def add_positional_spec_files_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "positional_spec_files",
        help="""
             Spec files may be specified wiwhout the --spec prefix for convenience.
             """,
        nargs="*",  # 1 or more filenames
        default=[],  # empty list
    )


def add_agency_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--agency",
        help="""
            Custom programming is used for timetables for certain agencies.
            Unimplemented stub.
            """,
        choices=["generic", "amtrak", "via", "hartford"],
        default="amtrak",
    )


def make_tt_arg_parser():
    """Make argument parser for timetable.py"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Produce printable HTML timetable from a tt-spec (foo.csv and foo.json files).""",
    )
    add_spec_files_argument(parser)
    add_positional_spec_files_argument(parser)

    add_agency_argument(parser)
    add_gtfs_argument(parser)
    add_date_argument(parser)
    add_debug_argument(parser)
    add_output_dirname_argument(parser)
    add_input_dirname_argument(parser)
    parser.add_argument(
        "--author",
        "-a",
        dest="author",
        help="""Name of the person generating the timetable.
                This is mandatory!  You can also set it using the AUTHOR environment variable,
                or the TIMETABLE_KIT_AUTHOR environment variable (which takes priority).
             """,
    )
    parser.add_argument(
        "--csv",
        dest="do_csv",
        help="""Produce a CSV output file (default is not to).""",
        action="store_true",
    )
    parser.add_argument(
        "--html",
        dest="do_html",
        help="""Produce HTML output file. (Default is not to produce HTML unless needed for PDF; HTML is needed to produce PDF.)""",
        action="store_true",
    )
    parser.add_argument(
        "--no-pdf",
        dest="do_pdf",
        help="""Do not produce PDF output file unless needed for JPG.  (Default is to produce PDF.  Note PDF is needed to produce JPG.)""",
        action="store_false",
    )
    parser.add_argument(
        "--jpeg",
        "--jpg",
        "-j",
        dest="do_jpg",
        help="""Produce a JPG output file (default is not to).  Requires that VIPS be installed.  Might only work on Linux.""",
        action="store_true",
    )
    parser.add_argument(
        "--nopatch",
        help="""Don't patch the feed.  Normally patches are applied to known-defective feeds.""",
        action="store_true",
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
