#! /usr/bin/env python3
# update_reference_dates.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Update the reference dates in a whole bunch of .json spec files all at once.

A bit of a hackish workaround for a known piece of tedium during timetable updates.
"""

import argparse
import os  # for os.PathLike for type hints

# for the in-place file editing
import re
import shutil
import tempfile
from pathlib import Path


def make_argparser():
    """
    Generate argument parser for the update_reference_dates miniprogram
    """
    parser = argparse.ArgumentParser(
        description="""Update reference dates for all .json files in a given directory""",
    )
    # First positional argument is the date
    parser.add_argument(
        "new_date",
        help="New reference date (in YYYYMMDD format)",
        type=str,
    )
    # Second positional argument is the directory, defaulting to specs_amtrak
    parser.add_argument(
        "directory",
        help="Directory containing .json files to modify (e.g. ./specs_amtrak)",
        nargs="?",
        default="./specs_amtrak",
    )
    parser.add_argument(
        "--nec",
        help="Just do the NEC",
        action="store_true",
    )
    return parser


# This routine is ripped off wholesale from Cecil Curry's 2015 implementation at
# https://stackoverflow.com/questions/4427542/how-to-do-sed-like-text-replace-with-python
# Thanks to Cecil.


def stream_edit_in_place(filename, pattern, repl):
    """
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    """
    # For efficiency, precompile the passed regular expression.
    pattern_compiled = re.compile(pattern)

    # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
    # writing with updating). This is usually a good thing. In this case,
    # however, binary writing imposes non-trivial encoding constraints trivially
    # resolved by switching to text writing. Let's do that.
    with (
        tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file,
        open(filename) as src_file,
    ):
        for line in src_file:
            tmp_file.write(pattern_compiled.sub(repl, line))

    # Overwrite the original file with the munged temporary file in a
    # manner preserving file attributes (e.g., permissions).
    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)


def update_reference_date_for_file(file: str | os.PathLike, new_date: str) -> None:
    """Update the reference date in one file."""
    # Sanity check.  Date must be 8 digits (YYYYMMDD).
    test_pattern = r"[0-9]{8}"
    if not re.fullmatch(test_pattern, new_date):
        raise Exception("Date is not in correct format: ", new_date)

    # Search and replace.
    search_pattern = r'"reference_date":\s*"([0-9]{8})"'
    replace_string = "".join(['"reference_date": "', new_date, '"'])
    stream_edit_in_place(file, search_pattern, replace_string)


if __name__ == "__main__":
    my_arg_parser = make_argparser()
    args = my_arg_parser.parse_args()
    new_date = args.new_date
    directory = Path(args.directory)

    for file in directory.iterdir():
        if file.suffix == ".json":
            if args.nec and not file.name.startswith("nec"):
                print("Skipping", file)
                continue
            print("Updating", file)
            update_reference_date_for_file(file, new_date)
