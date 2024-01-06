#! /usr/bin/env python3
# timetable.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Generate timetables.

timetable.py is the main program for generating timetables and related things
timetable.py --help gives documentation
"""

#########################
# Other people's packages

import sys  # sys.exit(0), sys.exit(1), and sys.path
import os  # for os.getenv
import os.path  # for os.path abilities including os.path.isdir
import shutil  # To copy files
from pathlib import Path

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
from timetable_kit.file_handling import read_list_file

from timetable_kit.convenience_types import HtmlAndCss

# We call these repeatedly, so give them shorthand names
from timetable_kit.runtime_config import agency
from timetable_kit.runtime_config import agency_singleton

# The actual value of agency will be set up later, after reading the arguments
# It is unsafe to do it here!

from timetable_kit.initialize import initialize_feed

from timetable_kit.timetable_argparse import make_tt_arg_parser
from timetable_kit.core import (
    TTSpec,
    fill_tt_spec,
)
from timetable_kit.timetable_class import (
    Timetable,
)
from timetable_kit.page_layout import (
    produce_html_page,
    produce_html_file,
)

# For copying into the final HTML folder
from timetable_kit import connecting_services
from timetable_kit import icons

# Module-level globals for memoization
_prepared_output_dirs = []
_prepared_output_dirs_for_rpa = []


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
    global _prepared_output_dirs_for_rpa
    global _prepared_output_dirs
    if str(output_dir) in _prepared_output_dirs_for_rpa:
        return
    if not for_rpa and str(output_dir) in _prepared_output_dirs:
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
    font_filenames = [
        "SpartanTT/SpartanTT-Bold.woff2",
        "SpartanTT/SpartanTT-Medium.woff2",
    ]
    for font_filename in font_filenames:
        font_file_source_path = source_dir / "fonts" / font_filename
        font_file_dest_path = fonts_dir / font_filename
        # Note, this overwrites
        shutil.copy2(font_file_source_path, font_file_dest_path)

    debug_print(1, "Fonts and icons copied to", output_dir)
    if for_rpa:
        _prepared_output_dirs_for_rpa.append(str(output_dir))
    _prepared_output_dirs.append(str(output_dir))
    return


def produce_several_timetables(
    list_file_list,
    *,
    gtfs_filename=None,
    do_csv=False,
    do_html=True,
    do_pdf=True,
    author=None,
    command_line_reference_date=None,
    input_dirname=None,
    output_dirname=None,
    patch_the_feed=True,
) -> None:
    """Main program to run from other Python programs.

    Doesn't mess around with args or environment variables. Does not take a default gtfs
    filename. DOES take filenames and directory names.
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

    # Loop over files specified at the command line
    for list_file in list_file_list:
        debug_print(1, "Producing timetable for", list_file)
        if list_file.endswith(".list"):
            (title, *spec_files) = read_list_file(list_file, input_dir=input_dirname)
            output_filename_base = list_file.removesuffix(".list")
        else:
            # Single file.  Treat as if it were a list of one
            spec_files = [list_file]
            # Placeholders to fill later
            title = None
            output_filename_base = None

        # Start the accumulating page list
        page_list: list[HtmlAndCss] = []

        for_rpa = False  # Will be set true if true for any spec file

        # Loop over files within a list file
        for spec_file in spec_files:
            # Load the tt-spec, both aux and csv
            # Also sets tt_id value in the aux
            spec = TTSpec.from_files(spec_file, input_dir=input_dirname)
            # Set reference date override -- does nothing if passed "None"
            spec.set_reference_date(command_line_reference_date)
            # Filter feed by reference date and by the train numbers (trip_short_names) in the spec header
            reduced_feed = spec.filter_and_reduce_feed(master_feed)
            # Note that we don't re-reduce the feed for a max-columns split spec (like the NEC).
            # We could but we want the whole NEC NB/Weekday TT to be valid over the same dates...

            # Find the date range on which the entire reduced feed is valid
            (latest_start_date, earliest_end_date) = reduced_feed.get_valid_date_range()
            debug_print(
                1,
                f"For {spec_file}: believed valid from {latest_start_date} to {earliest_end_date}",
            )

            spec_filename_base = spec.aux["output_filename"]

            if do_csv:
                # CSV can only do one page at a time.  Use the subspec name.
                # Also don't split big specs for CSV.  The end-user can do that.
                t_plaintext: Timetable = fill_tt_spec(
                    spec, today_feed=reduced_feed, doing_html=False
                )
                # Note that there is a real danger of overwriting the source file.
                # Avoid this by adding an extra suffix to the timetable name.
                path_for_csv = output_dir / Path(spec_filename_base + "-out.csv")
                t_plaintext.write_csv_file(path_for_csv)

            if do_html:
                # Set true if true on any spec
                for_rpa = for_rpa or bool(spec.aux.get("for_rpa"))

                # OK!  This code is intended to simplify work on the NEC.
                if spec.aux.get("max_columns_per_page", 0):
                    debug_print(
                        1,
                        f'Splitting {spec_filename_base} spec with max columns {spec.aux["max_columns_per_page"]}',
                    )
                    split_specs = spec.split()
                else:
                    # Non-split spec: treat it as a list of one
                    split_specs = [spec]

                # Loop over specs split out programmatically from a single .csv file
                for subspec in split_specs:
                    # Main timetable, same for HTML and PDF
                    t: Timetable = fill_tt_spec(
                        subspec, today_feed=reduced_feed, doing_html=True
                    )
                    # Render to HTML
                    timetable_styled_html = t.render()
                    debug_print(1, "HTML styled")

                    # Produce a final complete page, and associated page-specific CSS.
                    # Add it to the list of pages.
                    new_page = produce_html_page(
                        timetable_styled_html,
                        spec=subspec,
                        author=author,
                        start_date=str(latest_start_date),
                        end_date=str(earliest_end_date),
                    )
                    page_list.append(new_page)
                # End loop over specs split out programmatically from a single .csv file

            # Still in loop over files within a list file
            if do_html:
                # This is done if the list file was really just a single spec file
                # Fill these only if it wasn't filled by the list file
                # i.e. only in the single-spec-file case
                if not output_filename_base:
                    output_filename_base = spec_filename_base
                if not title:
                    title = spec.aux["title"] or "A Timetable"
            # End loop over files within a list file

        # Out of loop over files within a list file
        # Still in loop over files specified at the command line
        if do_html:
            # Produce complete multi-page HTML file.
            timetable_finished_html = produce_html_file(
                page_list, title=title, for_rpa=for_rpa
            )
            path_for_html = output_dir / Path(output_filename_base + ".html")
            with open(path_for_html, "w") as outfile:
                print(timetable_finished_html, file=outfile)
            debug_print(1, "Wrote HTML file", outfile.name)

            # Copy the icons and fonts to the output dir.
            # This is memoized, so it won't duplicate work if called repeatedly.
            copy_supporting_files_to_output_dir(output_dir, for_rpa)

        if do_pdf:
            # Pick up already-created HTML, convert to PDF
            weasy_html_pathname = str(path_for_html)
            html_for_weasy = weasyHTML(filename=weasy_html_pathname)
            path_for_weasy = output_dir / Path(output_filename_base + ".pdf")
            debug_print(1, "Writing PDF file...")
            html_for_weasy.write_pdf(path_for_weasy)
            debug_print(1, "Wrote PDF file", path_for_weasy)
        debug_print(1, "Done producing timetable for", spec_file)
    # Out of loop over files specified at the command line


def main():
    """Main program to run from the command line.

    Contains everything involving processing command line arguments, environment
    variables, etc.
    """

    debug_print(3, "Dumping sys.path for clarity:", sys.path)

    my_arg_parser = make_tt_arg_parser()
    args = my_arg_parser.parse_args()

    # Make sure user has provided at least one argument when running program
    # Otherwise, provide help
    if len(sys.argv) <= 1:
        my_arg_parser.print_help()
        sys.exit(1)

    set_debug_level(args.debug)
    debug_print(2, f"Successfully set debug level to {args.debug}.")

    # Check for the --get_gtfs flag
    must_get_gtfs: bool = bool(args.get_gtfs)

    # Get the selected agency (will default to Amtrak)
    debug_print(2, "Agency found:", args.agency)
    runtime_config.set_agency(args.agency)
    if must_get_gtfs and args.agency == "generic":
        print(
            "Can't automatically get GTFS for generic agency; use --gtfs argument instead"
        )
        sys.exit(1)

    # Retrieve the GTFS according to agency-specific methods
    if must_get_gtfs:
        agency().get_gtfs_files().download_and_save()
        debug_print(1, f"GTFS for {args.agency} ready.")

    # Passed at command line, or the gtfs directory for the agency
    gtfs_filename = args.gtfs_filename or agency().get_gtfs_files().get_path()

    spec_file_list = [*args.tt_spec_files, *args.positional_spec_files]

    if spec_file_list == []:
        if must_get_gtfs:
            # It's OK to have no specs if we were just downloading GTFS.
            # In this case, just quit.
            sys.exit(0)
        print(
            "You need to specify at least one spec file.  Use the --help option for help."
        )
        my_arg_parser.print_usage()
        sys.exit(1)

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

    author = args.author or os.getenv("TIMETABLE_KIT_AUTHOR") or os.getenv("AUTHOR")
    if not author:
        print("--author is mandatory!")
        sys.exit(1)

    # If nopatch, don't patch the feed.  Otherwise, do patch it.
    patch_the_feed = not args.nopatch

    command_line_reference_date = args.reference_date  # Does not default, may be None

    produce_several_timetables(
        list_file_list=spec_file_list,
        gtfs_filename=gtfs_filename,
        do_csv=args.do_csv,
        do_html=args.do_html,
        do_pdf=args.do_pdf,
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
