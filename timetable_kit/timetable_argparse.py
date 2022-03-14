#! /usr/bin/env python3
# timetable_argparse.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Argument parser for timetable.py

The only function for external use is make_tt_arg_parser.
"""

import argparse

def make_tt_arg_parser():
    """Make argument parser for timetable.py"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Produce printable HTML timetable.
The --type argument determines the type of timetable:
  single - single one-way timetable (mostly for testing)
  fill - timetable made from a tt-spec
  stations - create station list CSV file, in order, from single train number (for making tt-specs)
  make-spec - create tt-spec for use with fancy (edit this by hand afterwards - not working)
  compare - compare timetables for trips on a single route (to spot schedule changes for tt-spec making -- do not generate timetable)
  test - do internal testing (do not generate timetable)
''',
        )
    parser.add_argument('--type','-t',
        choices=['single','fill','stations','make-spec','compare','test'],
        help='What to do: type of timetable or tt-spec to generate.',
        )
    parser.add_argument('--gtfs','-g',
        dest='gtfs_filename',
        help='''Directory containing GTFS static data files,
                or zipped GTFS static data feed,
                or URL for zipped GTFS static data feed''',
        )
    parser.add_argument('--spec','-l',
        dest='tt_spec_filename',
        help='''CSV file containing tt-spec template for timetable.
                Top row should have a train number in each column except the first.
                A minus sign in front of train number indicates that column is read upward;
                a slash between trains indicates two trains in one column).
                The left column should have station codes in every row except the first.
                They are in the order they will be in in the finished timetable.
                The rest of the file should usually be blank.
                Format is a work in progress.
             ''',
        )
    parser.add_argument('--reference-date','--date','-d',
        dest='reference_date',
        help='''Reference date.
                GTFS data contains timetables for multiple time periods;
                this produces the timetable valid as of the reference date.
             '''
        )
    parser.add_argument('--trip',
        dest='trip_short_name',
        help='''For the stations and single options only.
                This specifies which trip_short_name to use
                to generate the list of stations.  For instance, if it's "51", train 51
                will be used, and the output will be tt_51_stations.csv.
             '''
        )
    parser.add_argument('--route',
        dest='route_long_name',
        help='''For the compare option only.
                This specifies which route_long_name to use.
                For instance "Cardinal" or "Lake Shore Limited".
             '''
        )
    parser.add_argument('--output-directory','-o',
        dest='output_dirname',
        help="Directory to put output HTML timetable files in.  Default is current directory."
        )
    parser.add_argument('--debug',
        dest='debug',
        help="Set debugging level, from 0 to 3 (default 1)",
        type=int,
        action='store',
        )
    return parser;

# Testing code
if __name__ == "__main__":
    print("Testing argument parser:")
    parser = make_tt_arg_parser()
    args = parser.parse_args()
    print("Type: " + str(args.type))
    print("GTFS Filename: " + str(args.gtfs_filename))
    print("Reference Date: " + str(args.reference_date))
    print("Output Dirname: " + str(args.output_dirname))
