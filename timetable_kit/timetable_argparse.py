#! /usr/bin/env python3
# timetable_argparse.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Argument parser for timetable.py.

The primary function for external use is make_tt_arg_parser.

Also includes routines for adding common arguments to parsers for other commands.
"""

import argparse

# For the GTFS day options:
from timetable_kit.feed_enhanced import GTFS_DAYS

# For the choice of the agency subpackage:
from timetable_kit.runtime_config import agency_choices


def add_agency_argument(parser: argparse.ArgumentParser):
    """Add the common --agency argument to a parser."""
    parser.add_argument(
        "--agency",
        "-a",
        help="""
            Custom programming is used for timetables for particular agencies.
            Default is Amtrak. VIA is working.  Others (including generic) are under construction.
            """,
        choices=agency_choices,
        default="amtrak",
    )


def add_gtfs_argument(parser: argparse.ArgumentParser):
    """Add the common --gtfs argument to a parser."""
    parser.add_argument(
        "--gtfs",
        "-g",
        dest="gtfs_filename",
        help="""Directory containing GTFS static data files,
                or zipped GTFS static data feed,
                or URL for zipped GTFS static data feed;
                default is ~/.local/share/timetable_kit/<agency>/gtfs""",
        default=None,
    )


def add_get_gtfs_argument(parser: argparse.ArgumentParser):
    """Add the --get-gtfs argument to a parser."""
    parser.add_argument(
        "--get-gtfs",
        dest="get_gtfs",
        help="""Download the GTFS files for the specified agency.
                  They will be stored at ~/.local/share/timetable_kit/<agency>/gtfs""",
        action="store_true",
    )


def add_date_argument(parser: argparse.ArgumentParser):
    """Add the common --date argument to a parser."""
    parser.add_argument(
        "--reference-date",
        "--date",
        "-d",
        dest="reference_date",
        help="""Reference date.
                GTFS data contains timetables for multiple time periods;
                this produces the timetable valid as of the reference date.
                This overrides any reference date set in the aux / .toml file in the tt-spec.
                Should be in YYYYMMDD format.
             """,
        type=str,
    )


def add_search_argument(parser: argparse.ArgumentParser):
    """Add the --search argument to the parser."""
    parser.add_argument(
        "--search",
        dest="search",
        help="""Instead of running the regular timetable generator,
                search through reference dates for a "good" date, starting with the standard date and testing
                the number of days specified here.
             """,
        type=int,
    )



def add_day_argument(parser: argparse.ArgumentParser):
    """Add the --day argument to a parser."""
    parser.add_argument(
        "--day",
        help="""Restrict to trains/buses operating on a particular day of the week, or weekdays, or weekend.
                WARNING: only checks the day of the week for the FIRST station the train stops at,
                and only in the base time zone of the agency.
                Manually check if you have trains which run overnight or start in a different time zone.
                """,
        type=str.lower,  # Automatically lowercases all input to this option
        choices=[*GTFS_DAYS, "weekday", "weekend"],
    )


def add_debug_argument(parser: argparse.ArgumentParser):
    """Add the common --debug argument to a parser."""
    parser.add_argument(
        "--debug",
        dest="debug",
        help="Set debugging level, from 0 to 3 (default 1)",
        type=int,
        action="store",
        default=1,
    )


def add_output_dirname_argument(parser: argparse.ArgumentParser):
    """Add the common --output-dir argument to a parser."""
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
    """Add the common --input-dir argument to a parser."""
    parser.add_argument(
        "--input-directory",
        "--input-dir",
        "-i",
        dest="input_dirname",
        help="""Directory to find input .csv & .toml (aux) files (tt-spec files) in.
                Default is not to prefix a directory (use system default for lookup of files).
                You can also set it using the TIMETABLE_KIT_INPUT_DIR environment variable.
             """,
    )


def add_spec_files_argument(parser: argparse.ArgumentParser):
    """Add the --specs argument to a parser."""
    parser.add_argument(
        "--spec",
        "--specs",
        "-l",
        dest="tt_spec_files",
        help="""Root of name of timetable spec file.
                If you type "--spec cono", then "cono.csv" and "cono.toml" files should exist.
                The tt-spec format remains a work in progress.
                For more information see the file tt-spec-documentation.rst.

                You may specify several spec files at once to generate multiple timetables.
                The spec files must all be in the same input directory.

                You may also specify a .list file which contains a list of spec filenames.
             """,
        nargs="+",  # 1 or more filenames
        default=[],  # empty list
    )


def add_positional_spec_files_argument(parser: argparse.ArgumentParser):
    """Add the positional specs argument to a parser."""
    parser.add_argument(
        "positional_spec_files",
        help="""
             Spec files may be specified without the --spec prefix for convenience.
             """,
        nargs="*",  # 1 or more filenames
        default=[],  # empty list
    )


def make_tt_arg_parser():
    """Make argument parser for timetable.py."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Produce printable HTML timetable from a tt-spec (foo.csv and foo.toml files).""",
    )
    add_spec_files_argument(parser)
    add_positional_spec_files_argument(parser)

    add_agency_argument(parser)
    add_gtfs_argument(parser)
    add_get_gtfs_argument(parser)

    add_date_argument(parser)
    add_debug_argument(parser)
    add_output_dirname_argument(parser)
    add_input_dirname_argument(parser)

    add_search_argument(parser)
    parser.add_argument(
        "--author",
        "-w",
        dest="author",
        help="""Name of the person generating the timetable.
                This is mandatory!  You can also set it using the AUTHOR environment variable,
                or the TIMETABLE_KIT_AUTHOR environment variable (which takes priority).
             """,
    )
    parser.add_argument(
        "--csv",
        dest="do_csv",
        help="""Produce CSV output files (default is not to).""",
        action="store_true",
    )
    parser.add_argument(
        "--no-html",
        dest="do_html",
        help="""Produce HTML output file. (Default is to produce HTML. HTML is needed to produce PDF.)""",
        action="store_false",
    )
    parser.add_argument(
        "--no-pdf",
        dest="do_pdf",
        help="""Do not produce PDF output file.  (Default is to produce PDF.)""",
        action="store_false",
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
    test_parser = make_tt_arg_parser()
    args = test_parser.parse_args()
    print("GTFS Filename: " + str(args.gtfs_filename))
    print("Reference Date: " + str(args.reference_date))
    print("Output Dirname: " + str(args.output_dirname))
