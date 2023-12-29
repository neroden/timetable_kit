# file_handling.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Handle files for timetable_kit.

This contains support routines for reading and writing files,
used by multiple tools.

"""

from pathlib import Path

def read_list_file(filename: str, *, input_dir) -> list[str]:
    """Given a filename ending in .list, return a list of the lines inside that
    file, with exterior whitespace stripped.

    The first line in a .list file is actually a title for the output HTML, not a filename.
    The rest are filenames.

    filename: the file name
    input_dirname: where to find the list file
    """
    if not filename.endswith(".list"):
        raise InputError("Not a list file:", filename)
    input_dir = Path(input_dir)

    list_filename_path = input_dir / Path(filename)
    with open(list_filename_path, "r") as list_file:
        lines = list_file.readlines()
    # Remove stray whitespace from either side of each line,
    # and drop lines which are blank after that
    stripped_list = [stripped for line in lines if (stripped := line.strip())]
    return stripped_list
