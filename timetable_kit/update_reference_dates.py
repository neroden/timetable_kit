#! /usr/bin/env python3
# update_reference_dates.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Update the reference dates in a whole bunch of .toml spec files all at once.

A bit of a hackish workaround for a known piece of tedium during timetable updates.
"""

import argparse
import os  # for os.PathLike for type hints
import re  # for sanity-checking the argument
from pathlib import Path

# We read and write toml
import tomlkit

from timetable_kit.errors import InputError


def make_argparser():
    """Generate argument parser for the update_reference_dates miniprogram."""
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
        help="Directory containing .toml files to modify (e.g. ./specs_amtrak)",
        nargs="?",
        default="./specs_amtrak",
    )
    parser.add_argument(
        "--nec",
        help="Just do the NEC",
        action="store_true",
    )
    return parser


def update_reference_date_for_file(file: str | os.PathLike, new_date: str) -> None:
    """Update the reference date in one file."""
    # Sanity check.  Date must be 8 digits (YYYYMMDD).
    test_pattern = r"[0-9]{8}"
    if not re.fullmatch(test_pattern, new_date):
        raise InputError("Date is not in correct format: ", new_date)

    with open(file, "r") as f:
        my_toml = tomlkit.load(f)

    my_toml["reference_date"] = new_date

    with open(file, "w") as f:
        tomlkit.dump(my_toml, f)


if __name__ == "__main__":
    my_arg_parser = make_argparser()
    args = my_arg_parser.parse_args()
    new_date = args.new_date
    directory = Path(args.directory)

    for file in directory.iterdir():
        if file.suffix == ".toml":
            if args.nec and not file.name.startswith("nec"):
                # print("Skipping", file)
                continue
            print("Updating", file)
            update_reference_date_for_file(file, new_date)
