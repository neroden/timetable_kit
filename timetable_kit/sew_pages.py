#! /usr/bin/env python3
# sew_pages.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Wrappers around pdftk-java.  Takes individual one-page PDF timetable files
and sews them together.

Implements "empire-service.list" form of timetable meta-spec.
"""

import os  # for os.system
from pathlib import Path

from timetable_kit.debug import debug_print
from timetable_kit.errors import InputError


def read_list_file(filename: str, *, input_dir) -> list[str]:
    """Given a filename ending in .list, return a list of the filenames inside
    that file, one filename per line, with exterior whitespace stripped.

    The first line in a list file is actually a title for the output HTML, not a filename.

    filename: the file name
    input_dirname: where to find the list file
    """
    if not filename.endswith(".list"):
        raise InputError("Not a list file:", filename)
    input_dir = Path(input_dir)

    list_filename_path = input_dir / Path(filename)
    with open(list_filename_path, "r") as list_file:
        raw_list = list_file.readlines()
    # Remove stray whitespace from either side of each line
    cooked_list = [item.strip() for item in raw_list]
    # Filter out lines which are empty after that
    twice_cooked_list = list(filter(bool, cooked_list))
    return twice_cooked_list


def expand_list_file_to_json_filenames(filename: str, *, input_dir) -> list[str]:
    """Does the same as read_list_file, but (a) removes the first (title) line,
    and (b) appends ".json" to each filename."""
    raw_list = read_list_file(filename, input_dir=input_dir)
    list_without_title = raw_list[1:]
    cooked_list = [item + ".json" for item in list_without_title]
    return cooked_list


def expand_list_files(files: list[str], *, input_dir) -> list[str]:
    """Given a list of spec files, take all the .list filenames, read the .list
    files, and expand them into individual JSON filenames.

    Copy other filenames through into the new list unchanged.  Return
    the new, longer, list.
    """
    new_list = []
    for x in files:
        if x.endswith(".list"):
            new_list.extend(expand_list_file_to_json_filenames(x, input_dir=input_dir))
        else:
            new_list.append(x)
    return new_list


def get_only_list_files(files: list[str]) -> list[str]:
    """Given a list of spec files, get only the .list filenames."""
    new_list = []
    for x in files:
        if x.endswith(".list"):
            new_list.append(x)
    return new_list


def assemble_pdf_from_list(filename: str, *, input_dir, output_dir):
    """Given the filename for a ".list" file, and assuming the PDF files for
    the individual pages have been created in output_dir, assemble the final
    multi-page PDF in output_dir."""

    # Note, the following checks for the ".list" suffix
    # before reading the list file:
    list_file_text = read_list_file(filename, input_dir=input_dir)
    # Remove the first line, which is the title, not the name of a page
    page_name_list = list_file_text[1:]

    infile_list = [page_name + ".pdf" for page_name in page_name_list]
    infile_path_list = [str(Path(output_dir) / infile) for infile in infile_list]

    outfile = filename.removesuffix(".list") + ".pdf"
    outfile_path = str(Path(output_dir) / outfile)

    pdf_merge_command = " ".join(["pdftk", *infile_path_list, "output", outfile_path])
    debug_print(1, pdf_merge_command)
    os.system(pdf_merge_command)


#### TEST CODE
if __name__ == "__main__":
    input_dir = "/home/neroden/programming/timetable_kit/timetable_kit/specs_amtrak"
    output_dir = "/home/neroden/programming/timetable_kit/timetable_kit/output"

    old_list = ["pennsylvanian.csv", "empire-service.list", "california-zephyr.json"]
    test_list_name = "empire-service.list"

    my_list = expand_list_files(old_list, input_dir=input_dir)
    print(my_list)

    list_list = get_only_list_files(old_list)
    print(list_list)

    assemble_pdf_from_list(test_list_name, input_dir=input_dir, output_dir=output_dir)
