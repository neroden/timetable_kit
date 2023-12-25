#! /usr/bin/env python3
# timetable.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Generate timetables.

timetable.py is the main program for generating timetables and related
things timetable.py --help gives documentation
"""

#########################
# Other people's packages

import sys  # sys.exit(1) and sys.path
import os  # for os.getenv
import os.path  # for os.path abilities including os.path.isdir
import shutil  # To copy files
from pathlib import Path, PurePath

import json

import pandas as pd

import gtfs_kit  # type: ignore # Tell MyPy this has no type stubs

from weasyprint import HTML as weasyHTML  # type: ignore # Tell MyPy this has no type stubs

############
# My modules
# This (runtime_config) stores critical data supplied at runtime such as the agency subpackage to use.
from timetable_kit import runtime_config

####################################
# Specific functions from my modules
# Note namespaces are separate for each file/module
# Also note: python packaging is really sucky for direct script testing.
from timetable_kit.debug import set_debug_level, debug_print
from timetable_kit.errors import (
    GTFSError,
    TwoStopsError,
    NoTripError,
    TwoTripsError,
    InputError,
)
from timetable_kit.convenience_types import HtmlAndCss
from timetable_kit.feed_enhanced import FeedEnhanced

# We call these repeatedly, so give them shorthand names
from timetable_kit.runtime_config import agency
from timetable_kit.runtime_config import agency_singleton

# The actual value of agency will be set up later, after reading the arguments
# It is unsafe to do it here!

# For anything where the code varies by agency, we always explicitly call:
# agency().special_data
# agency().json_stations
# And similarly for all other agency-specific callouts
# Except for calls to the singleton, which use agency_singleton()

from timetable_kit.initialize import initialize_feed

from timetable_kit.timetable_argparse import make_tt_arg_parser
from timetable_kit import sew_pages  # For understanding list files
from timetable_kit.core import (
    TTSpec,
    fill_tt_spec,
)
from timetable_kit.timetable_styling import (
    style_timetable_for_html,
)
from timetable_kit.page_layout import (
    produce_html_page,
    produce_html_file,
)

# For copying into the final HTML folder
from timetable_kit import connecting_services
from timetable_kit import icons

# This is a module-level global
prepared_output_dirs = []
prepared_output_dirs_for_rpa = []


def copy_supporting_files_to_output_dir(output_dirname, for_rpa=False):
    """Copy supporting files (icons, fonts) to the output directory.

    Necessary for Weasyprint, and for the HTML to display right.
    """
    # Copy the image files to the destination directory.
    # Necessary for weasyprint to work right!

    output_dir = Path(output_dirname)

    # Memoize.
    # We would like to save on copying by caching the fact that we've done this.
    # for_rpa adds an extra file (a superset of the other version)
    global prepared_output_dirs_for_rpa
    global prepared_output_dirs
    if str(output_dir) in prepared_output_dirs_for_rpa:
        return
    if not for_rpa and str(output_dir) in prepared_output_dirs:
        return

    source_dir = Path(__file__).parent

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.samefile(source_dir, output_dir):
        debug_print(1, "Working in module directory, not copying fonts and icons")
        return

    icons_dir = output_dir / "icons"
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    icon_filenames = icons.get_filenames_for_all_icons()
    if for_rpa:
        icon_filenames.append("rpa-logo.svg")
    for icon_filename in icon_filenames:
        icon_file_source_path = source_dir / "icons" / icon_filename
        icon_file_dest_path = icons_dir / icon_filename
        # Note, this overwrites
        shutil.copy2(icon_file_source_path, icon_file_dest_path)

    # Connecting service logos: logos folder in destination
    logos_dir = output_dir / "logos"
    if not os.path.exists(logos_dir):
        os.makedirs(logos_dir)
    logo_filenames = connecting_services.get_filenames_for_all_logos()
    for logo_filename in logo_filenames:
        logo_file_source_path = (
            source_dir / "connecting_services" / "logos" / logo_filename
        )
        logo_file_dest_path = logos_dir / logo_filename
        # Note, this overwrites
        shutil.copy2(logo_file_source_path, logo_file_dest_path)

    fonts_dir = output_dir / "fonts"
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
    # Each font has its own directory
    font_subdir_names = ["SpartanTT"]
    for font_subdir_name in font_subdir_names:
        font_subdir = fonts_dir / font_subdir_name
        if not os.path.exists(font_subdir):
            os.makedirs(font_subdir)
    # And font files within the directory
    font_filenames = ["SpartanTT/SpartanTT-Bold.ttf", "SpartanTT/SpartanTT-Medium.ttf"]
    for font_filename in font_filenames:
        font_file_source_path = source_dir / "fonts" / font_filename
        font_file_dest_path = fonts_dir / font_filename
        # Note, this overwrites
        shutil.copy2(font_file_source_path, font_file_dest_path)

    debug_print(1, "Fonts and icons copied to", output_dir)
    if for_rpa:
        prepared_output_dirs_for_rpa.append(str(output_dir))
    prepared_output_dirs.append(str(output_dir))
    return


def reduce_for_html_id(input: str):
    """Return string minus all characters not good for an HTML ID"""
    # Technically a lot is valid, but:
    # we don't want non-ASCII
    # we don't want punctuation except underscore or hyphen
    # we don't want whitespace or control characters, just numbers and letters plus _ and -
    return "".join(
        [c for c in input if c.isascii() and (c.isalnum() or c == "-" or c == "_")]
    )


def make_unique_page_id(spec_file, subspec_file):
    """Return an ID suitable for use in HTML and CSS which will identify the page in the timetable uniquely.

    The only information we have available is the names of the spec_file and subspec_file.  These are the same
    for a one-page timetable.
    """
    # Regular case.  Find the base filename, without suffix of directories.
    spec_file_basename = PurePath(spec_file).stem
    subspec_file_basename = PurePath(subspec_file).stem
    spec_file_component = reduce_for_html_id(spec_file_basename)
    subspec_file_component = reduce_for_html_id(subspec_file_basename)
    if spec_file_component == subspec_file_component:
        return "_".join(["tt", spec_file_component])
    else:
        return "_".join(["tt", spec_file_component, subspec_file_component])


def produce_several_timetables(
    spec_file_list,
    *,
    gtfs_filename=None,
    do_csv=False,
    do_html=True,
    do_pdf=True,
    do_jpg=False,
    author=None,
    command_line_reference_date=None,
    input_dirname=None,
    output_dirname=None,
    patch_the_feed=True,
) -> None:
    """Main program to run from other Python programs.

    Doesn't mess around with args or environment variables. Does not
    take a default gtfs filename. DOES take filenames and directory
    names.
    """

    if not author:
        print("produce_several_timetables: author is mandatory!")
        sys.exit(1)

    if not input_dirname:
        print("produce_several_timetables: input_dirname is mandatory!")
        sys.exit(1)
    debug_print(1, "Using input_dir", input_dirname)

    if not output_dirname:
        print("produce_several_timetables: output_dirname is mandatory!")
        sys.exit(1)
    debug_print(1, "Using output_dir", output_dirname)
    output_dir = Path(output_dirname)

    if not gtfs_filename:
        print("produce_several_timetables: gtfs_filename is mandatory!")
        sys.exit(1)

    # Doing PDF requires doing HTML first.
    if do_pdf:
        do_html = True

    # The following are rather finicky in their ordering:

    # Acquire the feed, enhance it, do generic patching.
    master_feed = initialize_feed(gtfs=gtfs_filename, patch_the_feed=patch_the_feed)

    for spec_file in spec_file_list:
        debug_print(1, "Producing timetable for", spec_file)
        if spec_file.endswith(".list"):
            (title, *subspec_files) = sew_pages.read_list_file(
                spec_file, input_dir=input_dirname
            )
            output_filename_base = spec_file.removesuffix(".list")
        else:
            # Single file.  Treat as list...
            subspec_files = [spec_file]
            # Placeholders to fill later
            title = None
            output_filename_base = None
        page_list: list[HtmlAndCss] = []
        for subspec_file in subspec_files:
            # Load the tt-spec, both aux and csv
            spec = TTSpec.from_files(subspec_file, input_dir=input_dirname)
            # Set reference date override -- does nothing if passed "None"
            spec.set_reference_date(command_line_reference_date)
            # Filter feed by reference date and by the train numbers (trip_short_names) in the spec header
            reduced_feed = spec.filter_and_reduce_feed(master_feed)

            subspec_filename_base = spec.json["output_filename"]

            if do_csv:
                # CSV can only do one page at a time.  Use the subspec name.
                filled_tt_plaintext = fill_tt_spec(
                    spec, today_feed=reduced_feed, doing_html=False
                )
                # Note that there is a real danger of overwriting the source file.
                # Avoid this by adding an extra suffix to the timetable name.
                path_for_csv = output_dir / Path(subspec_filename_base + "-out.csv")
                filled_tt_plaintext.write_csv_file(path_for_csv)

            if do_html:
                # Copy the icons and fonts to the output dir.
                # This is memoized, so it won't duplicate work if you do multiple tables.
                for_rpa = bool(spec.json["for_rpa"])  # used when copying files
                copy_supporting_files_to_output_dir(output_dir, for_rpa)

                # This is an ID to distinguish one timetable page from another
                # in the CSS coding.  Prefixed versions will be used to tag the
                # <div> for the page, and the table itself.
                # This should be unique per page.
                tt_id = make_unique_page_id(spec_file, subspec_file)

                # Main timetable, same for HTML and PDF
                (timetable, styler_table, header_styling_list) = fill_tt_spec(
                    spec, today_feed=reduced_feed, doing_html=True
                )
                timetable_styled_html = style_timetable_for_html(
                    timetable, styler_table, table_uuid=tt_id
                )
                debug_print(1, "HTML styled")

                # Find the date range on which the entire reduced feed is valid
                (
                    latest_start_date,
                    earliest_end_date,
                ) = reduced_feed.get_valid_date_range()
                debug_print(
                    1, f"Believed valid from {latest_start_date} to {earliest_end_date}"
                )

                # Produce a final complete page, and associated page-specific CSS.
                # Add it to the list of pages.

                new_page = produce_html_page(
                    timetable_styled_html,
                    header_styling_list,
                    tt_id=tt_id,
                    spec=spec,
                    author=author,
                    start_date=str(latest_start_date),
                    end_date=str(earliest_end_date),
                )
                page_list.append(new_page)

                # Fill these only if it wasn't filled by the list file
                # i.e. only in the single-spec-file case
                if not output_filename_base:
                    output_filename_base = subspec_filename_base
                if not title:
                    title = spec.json["title"] or "A Timetable"

                if do_jpg:
                    # This is awful.  JPG can only handle single pages.
                    # So in this case run through all the steps...
                    timetable_finished_html = produce_html_file(
                        [new_page], title=spec.json["title"] or "Timetable"
                    )
                    path_for_html = output_dir / Path(subspec_filename_base + ".html")
                    with open(path_for_html, "w") as outfile:
                        print(timetable_finished_html, file=outfile)
                    debug_print(1, "Wrote HTML file", outfile.name)
                    # Pick up already-created HTML, convert to PDF
                    weasy_html_pathname = str(path_for_html)
                    html_for_weasy = weasyHTML(filename=weasy_html_pathname)
                    path_for_weasy = output_dir / Path(subspec_filename_base + ".pdf")
                    html_for_weasy.write_pdf(path_for_weasy)
                    debug_print(1, "Wrote PDF file", path_for_weasy)
                    # Convert PDF to JPG
                    path_for_jpg = output_dir / Path(subspec_filename_base + ".jpg")
                    vips_command = "".join(
                        [
                            "vips copy ",
                            str(path_for_weasy),
                            "[dpi=300] ",
                            str(path_for_jpg),
                        ]
                    )
                    os.system(vips_command)
                    debug_print(1, "Wrote JPG file", path_for_jpg)
        if do_html:
            # Out of the (inner) loop.
            # Produce complete multi-page HTML file.
            timetable_finished_html = produce_html_file(page_list, title=title)
            path_for_html = output_dir / Path(output_filename_base + ".html")
            with open(path_for_html, "w") as outfile:
                print(timetable_finished_html, file=outfile)
            debug_print(1, "Wrote HTML file", outfile.name)
        if do_pdf:
            # Pick up already-created HTML, convert to PDF
            weasy_html_pathname = str(path_for_html)
            html_for_weasy = weasyHTML(filename=weasy_html_pathname)
            path_for_weasy = output_dir / Path(output_filename_base + ".pdf")
            html_for_weasy.write_pdf(path_for_weasy)
            debug_print(1, "Wrote PDF file", path_for_weasy)
        debug_print(1, "Done producing timetable for", spec_file)


def main():
    """Main program to run from the command line.

    Contains everything involving processing command line arguments,
    environment variables, etc.
    """

    debug_print(3, "Dumping sys.path for clarity:", sys.path)

    my_arg_parser = make_tt_arg_parser()
    args = my_arg_parser.parse_args()

    # Make sure user has provided at least one argument when running program
    # Otherwise, provide help
    if len(sys.argv) <= 1:
        my_arg_parser.print_help()
        sys.exit(1)

    spec_file_list = [*args.tt_spec_files, *args.positional_spec_files]

    if spec_file_list == []:
        print(
            "You need to specify at least one spec file.  Use the --help option for help."
        )
        my_arg_parser.print_usage()
        sys.exit(1)

    set_debug_level(args.debug)
    debug_print(2, "Successfully set debug level to 2.")

    # Get the selected agency
    debug_print(2, "Agency found:", args.agency)
    runtime_config.set_agency(args.agency)

    input_dirname = (
        args.input_dirname
        or runtime_config.agency_input_dir
        or os.getenv("TIMETABLE_KIT_INPUT_DIR")
        or "."
    )
    if not os.path.isdir(input_dirname):
        print("Input dir", input_dirname, "does not exist.  Aborting.")
        sys.exit(1)

    output_dirname = args.output_dirname or os.getenv("TIMETABLE_KIT_OUTPUT_DIR") or "."
    if not os.path.isdir(output_dirname):
        print("Output dir", output_dirname, "does not exist.  Aborting.")
        sys.exit(1)

    gtfs_filename = args.gtfs_filename or agency().gtfs_unzipped_local_path

    author = args.author or os.getenv("TIMETABLE_KIT_AUTHOR") or os.getenv("AUTHOR")
    if not author:
        print("--author is mandatory!")
        sys.exit(1)

    # If nopatch, don't patch the feed.  Otherwise, do patch it.
    patch_the_feed = not args.nopatch

    command_line_reference_date = args.reference_date  # Does not default, may be None

    produce_several_timetables(
        spec_file_list=spec_file_list,
        gtfs_filename=gtfs_filename,
        do_csv=args.do_csv,
        do_html=args.do_html,
        do_pdf=args.do_pdf,
        do_jpg=args.do_jpg,
        author=author,
        command_line_reference_date=command_line_reference_date,
        input_dirname=input_dirname,
        output_dirname=output_dirname,
        patch_the_feed=patch_the_feed,
    )


##########################
#### NEW MAIN PROGRAM ####
##########################
if __name__ == "__main__":
    main()
    sys.exit(0)
