#! /usr/bin/python3
# tt_parse_args.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
import argparse

def make_tt_arg_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''Produce printable HTML timetable.
The --type argument determines the type of timetable:
  single - single one-way timetable
  updown - one direction down, other direction up
  fancy - generated from template
  template - create template for use with fancy (edit this by hand afterwards)
  test - do internal testing (do not generate timetable)
''',
        )
    parser.add_argument('--type','-t',
        choices=['single','updown','fancy','template','test'],
        help='Type of timetable or template to generate.',
        )
    parser.add_argument('--gtfs','-g',
        dest='gtfs_filename',
        help='''Directory containing GTFS static data files,
                or zipped GTFS static data feed,
                or URL for zipped GTFS static data feed''',
        )
    parser.add_argument('--reference-date','--date','-d',
        dest='reference_date',
        help='''Reference date.
                GTFS data contains timetables for multiple time periods;
                this produces the timetable valid as of the reference date.
             '''
        )
    parser.add_argument('--output-directory','-o',
        dest='output_dirname',
        help="Directory to put output HTML timetable files in.  Default is current directory."
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
