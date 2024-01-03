#! /usr/bin/env python3
# core.py
# Part of timetable_kit
# Copyright 2021, 2022, 2023, 2024 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Handle tt-specs and generate timetables.

core.py contains the core code for handling specs and filling in timetables.
Includes the TTSpec type.
"""

#########################
# Other people's packages

import os  # For os.PathLike, for passing paths around
from copy import deepcopy  # For copying dicts properly
from pathlib import Path, PurePath
from typing import Type, Self, TypedDict

import tomlkit
import pandas as pd

############
# My modules
# This (runtime_config) stores critical data supplied at runtime such as the agency subpackage to use.
from timetable_kit.time import (
    get_zonediff,  # for "days"
    explode_timestr,  # for "days"
    day_string,  # for "days"
    get_zone_str,  # for TZ column
)

from timetable_kit import text_presentation
from timetable_kit import icons

####################################
# Specific functions from my modules
# Note namespaces are separate for each file/module
# Also note: python packaging is really sucky for direct script testing.
from timetable_kit.debug import debug_print
from timetable_kit.errors import (
    GTFSError,
    NoTripError,
    TwoTripsError,
    InputError,
)
from timetable_kit.convenience_types import GTFSDate

from timetable_kit.feed_enhanced import GTFS_DAYS, FeedEnhanced

# We call these repeatedly, so give them shorthand names
from timetable_kit.runtime_config import agency
from timetable_kit.runtime_config import agency_singleton

# This is the big styler routine, lots of CSS; keep out of main namespace
from timetable_kit.timetable_styling import (
    get_time_column_stylings,
)
from timetable_kit.tsn import (
    train_spec_to_tsn,
    find_tsn_dupes,
    make_tsn_to_trip_id_dict,
    make_tsn_and_day_to_trip_id_dict,
    stations_list_from_tsn,
    stations_list_from_trip_id,
)

# For the new HTML layout engine
from timetable_kit.timetable_class import Timetable


# Constant set for the special column names.
# These should not be interpreted as trip_short_names or train numbers.
special_column_names = {
    "",
    "station",
    "stations",
    "services",
    "access",
    "timezone",
}

# Constant set for special row names.
# These should not be interpreted as stop_code or station codes
special_row_names = {
    "",
    "omit",
    "column-options",
    "column_options",
    "route-name",
    "updown",
    "days",
    "days-of-week",
    "origin",
    "destination",
}


class TTSpec:
    """An entire TTSpec, both aux file and CSV spec file."""

    def __init__(self: Self, aux: dict, csv: pd.DataFrame) -> None:
        self.aux: dict = aux
        self.csv: pd.DataFrame = csv
        self.__set_aux_defaults()  # Set defaults for missing aux
        # Warning, this doesn't set crucial things like tt_id.

    def __set_aux_defaults(self: Self):
        """Fill in some default values for the aux if they're not present.

        Subroutine of TTSpec.__init__()

        This edits the dict in place.
        """
        self.aux.setdefault("for_rpa", False)
        # Affects a lot of things.
        self.aux.setdefault("transposed", False)
        # These are used when filling the timetable.
        self.aux.setdefault("train_numbers_side_by_side", False)
        self.aux.setdefault("dwell_secs_cutoff", 300)
        self.aux.setdefault("use_bus_icon_in_cells", False)
        self.aux.setdefault("box_time_characters", False)
        self.aux.setdefault("times_24h", False)
        # aria_label should be set in spec files.
        # Derive table_aria_label from it by appending "Timetable"
        # If it wasn't set, just use "Timetable".
        self.aux.setdefault(
            "table_aria_label", self.aux.get("aria_label", "") + " Timetable"
        )
        # These are used later, setting up the CSS
        self.aux.setdefault("font_name", "SpartanTT")
        self.aux.setdefault("font_size", "8px")  # 8px = 6pt
        self.aux.setdefault("font_allow_ligatures", False)

    def set_reference_date(self: Self, reference_date: GTFSDate | None):
        """Set the reference_date in the aux part of the TTSpec.

        If None is passed, does nothing (leaves it unchanged).
        """
        if reference_date:
            self.aux["reference_date"] = reference_date

    @classmethod
    def from_files(cls: Type[Self], filename: str, input_dir: os.PathLike | str = "."):
        """Load a tt-spec from files, both the aux and the CSV."""
        input_dir = Path(input_dir)

        # Accept the spec name with or without a suffix, for convenience
        filename_base = filename.removesuffix(".csv").removesuffix(".toml")

        csv_path = input_dir / (filename_base + ".csv")
        toml_path = input_dir / (filename_base + ".toml")
        debug_print(1, "TTSpec csv_path", csv_path, "/ toml_path", toml_path)

        new_ttspec = cls(cls.read_toml(toml_path), cls.read_csv(csv_path))
        # Fill in output_filename if it isn't in the aux. (Edit in place.)
        new_ttspec.aux.setdefault("output_filename", filename_base)
        # Fill in a reasonable value for the unique HTML ID.
        # TODO: do better with this.
        new_ttspec.aux.setdefault("tt_id", cls._make_tt_id(filename_base))
        return new_ttspec

    # These are here largely for namespacing purposes, to keep names short.
    @staticmethod
    def read_toml(file: os.PathLike | str) -> dict:
        """Load a TOML file (aux file) for the tt-spec."""
        path = Path(file)
        if path.is_file():
            with open(path, "r") as f:
                auxfile_str = f.read()
                # FIXME: maybe we can just use tomllib here?
                # We do plan to potentially write out edited toml elsewhere
                # which calls for tomlkit
                aux = tomlkit.loads(auxfile_str)
                debug_print(1, "tt-spec TOML (aux) file loaded")
                return aux
            print("Shouldn't get here, file load failed.")
        else:
            # Make it blank, basically
            debug_print(1, "No tt-spec TOML (aux) file.")
            return {}

    #    @staticmethod
    #    def read_json(file: os.PathLike | str) -> dict:
    #        """Load a JSON file for the tt-spec.
    #
    #        The preferred format is now TOML, but we keep this around as an alternative.
    #        """
    #        path = Path(file)
    #        if path.is_file():
    #            with open(path, "r") as f:
    #                auxfile_str = f.read()
    #                aux = json.loads(auxfile_str)
    #                debug_print(1, "tt-spec JSON file loaded")
    #                return aux
    #            print("Shouldn't get here, file load failed.")
    #        else:
    #            # Make it blank, basically
    #            debug_print(1, "No tt-spec JSON file.")
    #            return {}

    @staticmethod
    def read_csv(file: os.PathLike | str) -> pd.DataFrame:
        """Read a tt-spec CSV file."""
        ttspec_csv = pd.read_csv(file, index_col=False, header=None, dtype=str)
        debug_print(1, "tt-spec CSV file loaded")
        # PANDAS reads blank entries as NaN.
        # We really don't want NaNs in this file.  They should all be converted to "".
        ttspec_csv.fillna(value="", inplace=True)
        return ttspec_csv

    # A subroutine of a class method, nothing more.  Could be freestanding.
    @staticmethod
    def _make_tt_id(filename: str) -> str:
        """Given a filename, sanitize and prefix it to make a good HTML ID."""
        # First remove directories and suffixes
        in_file = PurePath(filename).stem
        # Technically a lot is valid, but:
        # we want only ASCII numbers, letters, underscore, hyphen
        cleaned = "".join(
            [
                c
                for c in in_file
                if c.isascii() and (c.isalnum() or c == "-" or c == "_")
            ]
        )
        # Finally add the prefix
        return "tt_" + cleaned

    def __getitem__(self: Self, index):
        """Return first the aux, second the CSV."""
        # Allow unpacking
        return (self.aux, self.csv)[index]

    def strip_omits(self):
        """Strip any rows in the CSV where the first column is "omit" (used for
        comments)."""
        old_csv = self.csv
        # Note: assumes that the column names are 0,1,2,etc.
        # I couldn't figure out how to do this with iloc FIXME
        new_csv = old_csv[old_csv[0] != "omit"].reset_index(drop=True)
        debug_print(6, "STRIPPED: ", new_csv)
        self.csv = new_csv

    def augment_from_key_cell(self, *, feed: FeedEnhanced):
        """Fill in the station list for a tt-spec if it has a key code.

        Cell 0,0 is normally blank. If it is "Stations of 59", then (a) assume there is
        only one tt-spec row; (b) get the stations for 59 and fill the rows in from that

        Requires a feed.  Requires that reference_date be set.

        Note that this tucks on the end of the tt_spec.  A "second row" for column-
        options will therefore be unaffected.  Other second rows may result in confusing
        results.

        Prints the CSV.
        """
        key_code = str(self.csv.iloc[0, 0])
        if key_code == "":
            # No key code, nothing to do
            return

        if not key_code.startswith("stations of "):
            raise InputError(
                "Key cell must be blank or 'stations of xxx', was ", key_code
            )

        # Find the train name:
        key_train_name = key_code.removeprefix("stations of ")
        debug_print(1, f"Using key tsn {key_train_name}")

        # Filter the feed down to a single date...
        reference_date = self.aux["reference_date"]
        today_feed = feed.filter_by_dates(reference_date, reference_date)

        # And possibly filter by day as well
        for day in GTFS_DAYS:
            if key_train_name.endswith(day):
                key_train_name = key_train_name.removesuffix(day).strip()
                today_feed = today_feed.filter_by_day_of_week(day)
                break

        # And pull the stations list
        stations_df = stations_list_from_tsn(today_feed, key_train_name)
        new_csv = self.csv.copy()  # Copy entire original spec
        new_csv.iloc[0, 0] = ""  # Blank out key_code
        # The following will add the stations as desired.
        # It creates duplicate indexes, so we must reset the index.
        self.csv = pd.concat([new_csv, stations_df]).fillna("").reset_index(drop=True)
        debug_print(1, "Augmented TTSpec:")
        debug_print(1, self.csv)

    def split(self: Self) -> list[Self]:
        """Split a TTSpec with lots of columns according to the max_columns_per_page parameter

        This will only work if all the "special" columns are on the left edge of the spec.
        Also absolutely requires a column_options row.  (FIXME.)
        """
        debug_print(1, "Starting CSV:")
        debug_print(1, self.csv)
        cols_per_page = self.aux.get("max_columns_per_page", 0)
        if cols_per_page == 0:
            # We are not splitting this timetable
            return [self]

        (row_count, column_count) = self.csv.shape
        # column 0 is always the code column
        for x in range(1, column_count):
            column_key_str = str(self.csv.iloc[0, x]).strip()
            if column_key_str.lower() not in special_column_names:
                first_regular_column = x
                break
        else:
            raise InputError(
                "Failure splitting spec: No regular columns, only special columns"
            )
        debug_print(1, "First regular column", first_regular_column)

        num_regular_columns = column_count - first_regular_column

        # "Upside down floor division"
        # effectively acts as ceiling division
        num_pages = -(num_regular_columns // -cols_per_page)
        # debug_print(1, "Number of pages", num_pages)

        # Left section with the special columns
        # Pandas slices do NOT include the end, like regular Python slices
        # Make a copy so we can edit it
        left_section = self.csv.iloc[:, 0:first_regular_column].copy()

        # This is helpful to check fencepost errors
        # debug_print(1, "Left section")
        # debug_print(1, left_section)

        # Accumulate the new specs
        new_specs = []
        orphan_flag = False
        for i in range(0, num_pages):
            # Notice that i is 0-indexed, while the printed page number is 1-indexed
            first_col = first_regular_column + i * cols_per_page
            potential_post_final_col = first_col + cols_per_page
            post_final_col = min(potential_post_final_col, column_count)

            # Special "anti-orphan" code:
            if (i == num_pages - 2) and (post_final_col == column_count - 1):
                # Would leave one column for next page.
                # Instead, leave two.
                post_final_col -= 1
                orphan_flag = True
            if (i == num_pages - 1) and (orphan_flag == True):
                # Pick up the extra column.
                first_col -= 1

            debug_print(1, f"Slicing columns from [{first_col} to {post_final_col})")
            # Pandas slices do NOT include the end, like regular Python slices
            # Make a copy so we can edit it
            current_section = self.csv.iloc[:, first_col:post_final_col].copy()
            if i > 0:
                # Insert "ardp" in the left column, row 1 (always column-options)
                # Ugly and fragile.  FIXME.
                current_section.iloc[1, 0] += " ardp"

            # This is helpful to check fencepost errors
            # debug_print(1, "Current section:")
            # debug_print(1, current_section)

            # Now join the left section to the data section, and reindex.
            new_csv = left_section.join(current_section)
            # Reset rows index
            new_csv.reset_index(drop=True, inplace=True)
            # Reset columns index
            new_csv.columns = range(new_csv.shape[1])
            # TODO: see if we can make this reindexing optional.

            # Remember to copy the aux dict so we can change it
            new_aux = deepcopy(self.aux)

            new_spec = TTSpec(new_aux, new_csv)
            del new_spec.aux["max_columns_per_page"]
            new_spec.aux["heading"] += f" Page {i + 1}/{num_pages}"
            new_spec.aux["aria_label"] += f" page {i + 1}"
            # This one's critically important since IDs must be unique
            new_spec.aux["tt_id"] += f"_page_{i + 1}"

            # Wish we could do new_specs[i] = new_spec ?
            new_specs.append(new_spec)

            debug_print(1, f"Extracted spec {i} (page {i + 1})")
            # This is helpful for debugging the split as a whole
            # debug_print(1, new_spec.aux)
            # debug_print(1, new_spec.csv)

        # And return the list.
        return new_specs

    def filter_and_reduce_feed(self: Self, master_feed: FeedEnhanced) -> FeedEnhanced:
        """Filter a master feed to trips relevant to this spec only.

        First we filter to the reference date in the TTSpec aux. (This is essential to
        get accurate timetables for a given period.)

        Then we filter it to trip_short_names which are in the header of the TTSpec CSV.

        (This is necessary to get effective dates for the period, and also vastly
        reduces computational load for the main program.)

        Return the reduced feed.
        """

        # Filter the feed to the relevant day.  Required.
        reference_date = self.aux["reference_date"]
        today_feed = master_feed.filter_by_dates(reference_date, reference_date)
        debug_print(1, "Feed filtered by reference date.")

        # Reduce the feed, by eliminating stuff from other trains.
        # By reducing the stop_times table to be much smaller,
        # this hopefully makes each subsequent search for a timepoint faster.
        # This cuts a testcase runtime from 23 seconds to 20.
        train_specs_list = self.get_train_specs_list()
        # Contains "/" items; must flatten
        flattened_train_specs_set = flatten_train_specs_list(train_specs_list)

        # Contains "91 monday" and similar specs: remove the day suffixes here
        flattened_tsn_list = [
            train_spec_to_tsn(train_spec) for train_spec in flattened_train_specs_set
        ]

        reduced_feed = today_feed.filter_by_trip_short_names(flattened_tsn_list)
        debug_print(1, "Feed filtered by trip_short_name.")

        # Uniqueness sanity check -- check for two rows in reduced_feed.trips with the same tsn.
        # This will make it impossible to map from tsn to trip_id.
        # HOWEVER, Amtrak has some weird duplicates with duplicate trip_ids and identical timings,
        # so this might not be a fatal error.
        if find_tsn_dupes(reduced_feed):
            debug_print(
                1,
                "Warning, tsn duplicates!  If you use one of these without a day"
                " disambiguator, a random trip will be picked!  Usually a bad idea!",
            )

        # Print the calendar for debugging
        debug_print(1, "Calendar:")
        debug_print(1, reduced_feed.calendar)

        # Debugging for the reduced feed.  Seems to be fine.
        # with open( Path("./dump-stop-times.csv"),'w') as outfile:
        #    print(reduced_feed.stop_times.to_csv(index=False), file=outfile)

        return reduced_feed

    def get_stations_list(self: Self) -> list[str]:
        """Return list of station codes in the spec."""
        stations_df = self.csv.iloc[1:, 0]
        stations_list_raw = stations_df.to_list()
        stations_list_strings = [str(i).strip() for i in stations_list_raw]
        stations_list = [i for i in stations_list_strings if i not in special_row_names]
        return stations_list

    def get_train_specs_list(self: Self) -> list[str]:
        """Return list of train specs in the spec."""
        train_specs_df = self.csv.iloc[0, 1:]
        train_specs_list_raw = train_specs_df.to_list()
        train_specs_list_strings = [str(i).strip() for i in train_specs_list_raw]
        train_specs_list = [
            i for i in train_specs_list_strings if i not in special_column_names
        ]
        return train_specs_list

    def extract_column_options(self: Self):
        """If this TTSpec has column-options in row 2 of the CSV, remove that row and
        fill in the column_options structure.

        This data structure is a list (indexed by column number) wherein each element is
        a list. These inner lists are either empty, or a list of options.

        Options are free-form, space-separated, and several are defined.

        The column options are specified in row 2 of the CSV.  If they're not there,
        don't call this.

        We HAVE to reindex after removing the column_options from the CSV.
        """
        self.column_options: list[list[str]]
        # Consider generalizing to allow column-options in other rows
        if str(self.csv.iloc[1, 0]).lower() not in ["column-options", "column_options"]:
            column_count = self.csv.shape[1]
            # What, there weren't any?  Make a list containing blank lists:
            self.column_options = [[]] * column_count
            # No column-options row, so don't delete it
            return
        # Now for the main version
        column_options_df = self.csv.iloc[1, 0:]  # second row, all of it
        column_options_raw_list = column_options_df.to_list()
        column_options_nested_list = [str(i).split() for i in column_options_raw_list]
        self.column_options = column_options_nested_list
        # Now delete row 2.
        # This drops by index and not by actual row number, FIXME
        # Thankfully they're currently the same
        # Operate in place
        self.csv.drop(1, axis="index", inplace=True)
        # We MUST reset the index so rows are numbered 0 to end without breaks
        # Drop old index, operate in place
        self.csv.reset_index(drop=True, inplace=True)
        debug_print(1, "Column options separated from CSV:", self.column_options)
        debug_print(6, "New CSV:", self.csv)


class _CellCodes(TypedDict, total=False):
    """Represents codes which might be in a cell in a timetable spec."""

    train_spec: str | None
    first: bool
    last: bool
    blank: bool
    two_row: bool


def get_cell_codes(code_text: str, train_specs: list[str]) -> _CellCodes | None:
    """Given special code text in a cell, decipher it.

    The code leads with a train_spec (train number or train number + day of week), followed by a space,
    followed by zero or more of the following (space-separated):
    "first" (first station for train, show departure only)
    "last" (last station for train, show arrival only)
    "first two_row" -- use two-row format
    "last two_row" -- use two-row format
    "two-row" -- use two-row format, show arrival and departure always
    "blank" -- if this train does not stop at this station, make a blank cell with this train's color

    Specifying just a train spec is supported.

    For special codes which aren't dependent on a train number, see
    text_presentation.get_cell_substitution.  Those include simple (white cell) "blank".

    Returns None if there was no code in the cell (the usual case)

    Otherwise, returns a dict:
    train_spec: the train_spec
    first: True or False
    last: True or False
    blank: True or False
    two_row: True or False
    """
    # TODO: unify this so we can have colored backgrounds for arrows?

    if code_text == "":
        return None

    code_text = code_text.strip()

    # Train specs may have a "noheader" suffix.  Remove it.
    train_specs = [
        train_spec.removesuffix("noheader").strip() for train_spec in train_specs
    ]

    # The cell code may end with two_row or two-row.  Remove it.
    two_row = False
    if code_text.endswith("two_row"):
        two_row = True
        code_text = code_text.removesuffix("two_row").strip()
    elif code_text.endswith("two-row"):
        two_row = True
        code_text = code_text.removesuffix("two-row").strip()
    elif code_text.endswith("tworow"):
        two_row = True
        code_text = code_text.removesuffix("tworow").strip()

    if code_text.endswith("last"):
        train_spec = code_text.removesuffix("last").strip()
        if train_spec == "":
            return {
                "train_spec": None,
                "last": True,
                "first": False,
                "blank": False,
                "two_row": two_row,
            }
        if train_spec not in train_specs:
            return None
        return {
            "train_spec": train_spec,
            "last": True,
            "first": False,
            "blank": False,
            "two_row": two_row,
        }

    if code_text.endswith("first"):
        train_spec = code_text.removesuffix("first").strip()
        if train_spec == "":
            return {
                "train_spec": None,
                "last": False,
                "first": True,
                "blank": False,
                "two_row": two_row,
            }
        if train_spec not in train_specs:
            return None
        return {
            "train_spec": train_spec,
            "first": True,
            "last": False,
            "blank": False,
            "two_row": two_row,
        }

    # We handle simple "blank" in text_presentation.get_cell_substitution.
    # This is "blank" with a train number -- colored blank.
    if code_text.endswith("blank"):
        train_spec = code_text.removesuffix("blank").strip()
        if train_spec not in train_specs:
            return None
        return {
            "train_spec": train_spec,
            "first": False,
            "last": False,
            "blank": True,
            "two_row": two_row,  # ignored in this case, but OK
        }

    # Simple train number. (Possibly with two-row.)
    train_spec = code_text.strip()
    if train_spec == "" and two_row:
        return {
            "train_spec": None,
            "last": False,
            "first": False,
            "blank": False,
            "two_row": two_row,
        }
    if train_spec not in train_specs:
        return None
    return {
        "train_spec": train_spec,
        "first": False,
        "last": False,
        "blank": False,
        "two_row": two_row,
    }


def split_trains_spec(trains_spec):
    """Given a string like "59 / 174 / 22", return a structured list:

    [["59, "174", "22"], True]

    Used to separate specs for multiple trains in the same timetable column. A single
    "59" will simply give {"59"}.

    This also processes specs like "59 monday".  And "59 noheader".  And "59 monday
    noheader". These require exact spacing; this routine should probably clean up the
    spacing, but does not.
    """
    # Remove leading whitespace and possible leading minus sign
    clean_trains_spec = trains_spec.lstrip()

    raw_list = clean_trains_spec.split("/")
    clean_list = [item.strip() for item in raw_list]  # remove whitespace again
    return clean_list


def flatten_train_specs_list(train_specs_list):
    """Take a nested list of trains and make a flat list of trains.

    Take a list of trains as specified in a tt_spec such as ['','174
    monday','178/21','stations','23/1482'] and make a flat list of all trains involved
    ['174 monday','178','21','23','1482'] without the special keywords like "station".

    Leaves the '91 monday' type entries.

    Removes "noheader" suffixes (we never want them in flattened form).
    """
    flattened_ts_set = set()
    for ts in train_specs_list:
        train_specs = split_trains_spec(ts)  # Separates at the "/"
        for train_spec in train_specs:
            cleaned_train_spec = train_spec.removesuffix("noheader").strip()
            flattened_ts_set.add(cleaned_train_spec)
    flattened_ts_set = flattened_ts_set - special_column_names
    return flattened_ts_set


# Subroutines for fill_tt_spec


def make_stations_max_dwell_map(
    today_feed: FeedEnhanced, spec: TTSpec, trip_from_train_spec_fn
) -> dict[str, bool]:
    """Return a dict from station_code to True/False, based on the trains in the
    tt_spec.

    This is used to decide whether a station should get a "double line" or "single line" format in the timetable.

    today_feed: a feed filtered to a single date (so tsns are unique)
    spec: the spec, CSV + aux
    trip_from_train_spec_fn: a function which maps train_spec to trip_id and provides error raising

    The spec's aux section should contain
    dwell_secs_cutoff: below this, we don't bother to list arrival and departure times both

    Expects a feed already filtered to a single date.
    The feed *may* be restricted to the relevant trains (but must contain all relevant trains).

    First we extract the list of stations and the list of train names from the tt_spec.

    If any train in tsns has a dwell time of dwell_secs or longer at a station,
    then the dict returns True for that station_code; otherwise False.
    """
    dwell_secs_cutoff = spec.aux["dwell_secs_cutoff"]
    # First get stations and trains list from tt_spec.
    stations_list = spec.get_stations_list()
    train_specs_list = spec.get_train_specs_list()
    # Note train_specs_list still contains "/" items
    flattened_train_spec_set = flatten_train_specs_list(train_specs_list)
    # Note that "91 monday" is a perfectly valid spec here

    # Prepare the dict to return
    stations_dict = {}
    for station_code in stations_list:
        stop_id = agency_singleton().stop_code_to_stop_id(station_code)
        max_dwell_secs = 0
        for train_spec in flattened_train_spec_set:
            debug_print(3, "debug dwell map:", train_spec, station_code)
            trip_id = trip_from_train_spec_fn(train_spec).trip_id
            max_dwell_secs = max(
                max_dwell_secs, today_feed.get_dwell_secs(trip_id, stop_id)
            )
        if max_dwell_secs >= dwell_secs_cutoff:
            stations_dict[station_code] = True
        else:
            stations_dict[station_code] = False
    return stations_dict


def raise_error_if_not_one_row(trips):
    """Given a PANDAS DataFrame, raise an error if it has either 0 or more than 1 row.

    The error text is based on the assumption that this is a GTFS trips frame. This
    returns nothing if successful; it is solely sanity-check code.

    For speed, we have to work with trips directly rather than modifying the feed, which
    is why this is needed for fill_tt_spec, rather than merely in FeedEnhanced.
    """
    num_rows = trips.shape[0]
    if num_rows == 0:
        raise NoTripError(
            "Expected single trip: no trips in filtered trips table", trips
        )
    if num_rows > 1:
        print(trips)
        raise TwoTripsError(
            "Expected single trip: too many trips in filtered trips table", trips
        )
    return


def fill_tt_spec(
    spec: TTSpec,
    *,
    today_feed: FeedEnhanced,
    doing_html=False,
    doing_multiline_text=True,
    is_ardp_station="dwell",
) -> Timetable:
    """Fill a timetable from a TTSpec template using GTFS data.

    spec: a TTSpec containing both the CSV spec and the auxilliary aux
    Most components of the aux are optional. The following are mandatory:
        reference_date
        train_numbers_side_by_side
        dwell_secs_cutoff
        use_bus_icon_in_cells
        box_time_characters
    (These will all be given good default values when creating a TTSpec.)

    today_feed: GTFS feed to work with.  Mandatory.
        This should already be filtered to a single representative date.  This is not checked.
        This *may* be filtered to relevant trains only.  It must contain all relevant trains.
    reference_date: Reference date to get timetable for.  Also used for Arizona timezone conversion.

    doing_html: Produce HTML timetable.  Default is false (produce plaintext timetable).
    doing_multiline_text: Produce multiline text in cells.  Ignored if doing_html.
        Default is True.
        If False, stick with single-line text (and never print arrival times FIXME)
    is_ardp_station: pass a function which says whether a station should have arrival times;
        Default is "dwell" (case sensitive), which uses dwell_secs_cutoff.
        "major" uses only "major" stations.
        "False" means false for all.
        "True" means true for all.

    aux options:
    box_time_characters: Box every character in the time in an HTML box to make them line up.
        For use with fonts which don't have tabular nums.
        Default is False.  Avoid if possible; fragile.
    train_numbers_side_by_side: For column headers for a column with multiple trains, put train numbers side by side.
        Default is to stack them top to bottom.
    dwell_secs_cutoff: Show arrival & departure times if dwell time is this many seconds
        or higher for some train in the tt_spec
        Defaults to 300, meaning 5 minutes.
        Probably don't want to ever make it less than 1 minute.
    use_bus_icon_in_cells: Put a bus icon next to timetable cells which are a bus.
    """
    # MyPy throws a fit over the tables in the feed.  Assert them all.
    assert today_feed.agency is not None
    assert today_feed.calendar is not None
    assert today_feed.stops is not None
    assert today_feed.routes is not None
    assert today_feed.trips is not None

    # Extract vital information from the aux (aux) dict.
    if not spec.aux.get("reference_date"):
        raise InputError("No reference date in aux file or at command line!")
    reference_date = str(spec.aux["reference_date"])
    debug_print(1, "Working with reference date ", reference_date)

    times_24h = bool(spec.aux["times_24h"])
    train_numbers_side_by_side = bool(spec.aux["train_numbers_side_by_side"])
    use_bus_icon_in_cells = bool(spec.aux["use_bus_icon_in_cells"])
    box_time_characters = bool(spec.aux["box_time_characters"])
    transposed = bool(spec.aux["transposed"])

    if "programmers_warning" in spec.aux:
        print("WARNING: ", spec.aux["programmers_warning"])

    # Clean up the spec.
    spec.strip_omits()
    spec.extract_column_options()  # Also removes column_options from main CSV dataframe
    spec.augment_from_key_cell(feed=today_feed)  # Expand "shorthand" specs

    # We have a filtered feed.  We're going to have to map from tsns to trip_ids, repeatedly.
    # This was the single slowest step in earlier versions of the code, using nearly all the runtime.
    # So we generate a dict for it.
    tsn_to_trip_id = make_tsn_to_trip_id_dict(today_feed)
    # Because of the problem of "same tsn, different day", we have to add the "91 monday" indices.
    tsn_and_day_to_trip_id = make_tsn_and_day_to_trip_id_dict(today_feed)
    # Merger of both dictionaries:
    train_spec_to_trip_id = tsn_and_day_to_trip_id | tsn_to_trip_id

    # Create an inner function to get the trip from the tsn, using the dict we just made
    # Also depends on the today_feed
    def trip_from_train_spec_local(train_spec: str) -> pd.Series:
        assert today_feed.trips is not None  # Silence MyPy
        try:
            my_trip_id = train_spec_to_trip_id[train_spec]
        except KeyError as e:
            raise InputError("No trip_id for ", train_spec) from e
        my_trips = today_feed.trips[today_feed.trips.trip_id == my_trip_id]
        raise_error_if_not_one_row(my_trips)
        my_trip = my_trips.iloc[0]
        return my_trip

    # Now, we need to determine whether the tsn is a bus.  This is actually in GTFS.
    # However, it has to be looked up by trip_id, so this needs to use the local version
    # of trip_from_train_spec_local, *and* should use the local reduced feed, so it has to be
    # subordinate to this particular run of the timetable generator!
    # So create another inner function to pull the line from the route table.
    def route_from_train_spec_local(train_spec: str) -> pd.Series:
        assert today_feed.routes is not None  # Silence MyPy
        my_trip = trip_from_train_spec_local(train_spec)
        my_routes = today_feed.routes[today_feed.routes.route_id == my_trip.route_id]
        if my_routes.shape[0] == 0:
            raise GTFSError("Missing route_id for train_spec", train_spec)
        my_route = my_routes.iloc[0]
        return my_route

    # Load variable functions for is_ardp_station
    match is_ardp_station:
        case False:
            is_ardp_station = lambda station_code: False
        case True:
            is_ardp_station = lambda station_code: True
        case "major":
            is_ardp_station = (
                lambda station_code: agency_singleton().is_standard_major_station(
                    station_code
                )
            )
        case "dwell":
            # Prep max dwell map.  This is the second-slowest part of the program.
            stations_max_dwell_map = make_stations_max_dwell_map(
                today_feed=today_feed,
                spec=spec,
                trip_from_train_spec_fn=trip_from_train_spec_local,
            )
            is_ardp_station = lambda station_code: stations_max_dwell_map[station_code]
            debug_print(1, "Dwell map prepared.")
    if not callable(is_ardp_station):
        raise TypeError(
            "Received is_ardp_station which is not callable: ", is_ardp_station
        )

    # Get the column options row (previously calculated)
    column_options = spec.column_options

    # The list of stations, occasionally useful:
    station_codes_list = spec.get_stations_list()

    #######################
    # Object containing the DataFrame tables to fill in for the timetable.
    # Initialized to have the same STRUCTURE as the spec, but no content.
    # DataFrame Elements:
    # text -- to be printed in each cell
    # th -- boolean table, is this a <th> cell?  Default False
    # classes -- string of CSS classes for each cell
    # attributes -- extra attribute definitions string for each cell
    t = Timetable(spec.csv)
    debug_print(1, "Prepped timetable structure.")

    # Debug-print the spec in its "final" form
    debug_print(1, "Spec CSV immediately before filling timetable:")
    debug_print(1, spec.csv)

    # Go through the columns to get an ardp columns map -- cleaner than current implementation
    # FIXME.

    # Base CSS classes for every data cell.  Currently an empty list.
    base_cell_css_list: list[str] = []
    # Base CSS for column headers.
    # This is necessary to apply base column header behavior.
    base_column_header_css_list = ["col_heading"]

    # NOTE, border variations not implemented yet FIXME
    # borders_final_css="border-bottom-heavy"
    # borders_initial_css="border-top-heavy"
    # Have to add "initial" and "final" with heavy borders

    # Pick out the agency timezone.  Although theoretically each agency has its own timezone,
    # The dataset is not allowed by GTFS to have multiple agency timezones,
    # so the feed is sufficient to specify the agency timezone
    any_agency_row = today_feed.agency.iloc[0]
    agency_tz = any_agency_row.agency_timezone
    debug_print(1, "Agency time zone", agency_tz)

    # Now for the main routine, which is a giant double loop, and therefore quite slow.
    (row_count, column_count) = spec.csv.shape

    for x in range(1, column_count):  # First (0) column is the station code
        column_key_str = str(spec.csv.iloc[0, x]).strip()  # row 0, column x
        # Create blank train_specs list, so we can call get_cell_codes on a special column without crashing
        train_specs = []

        # First do the stuff for the column headers.

        # reset the CSS list each time through the loop.
        # Note!  Mustn't use this, it won't work becuase it creates an object alias:
        # column_header_css_list = base_column_header_css_list
        # Do not do that!
        column_header_css_list = [*base_column_header_css_list]

        match column_key_str.lower():
            case "station" | "stations":
                # in a span
                t.text.iloc[0, x] = text_presentation.get_station_column_header(
                    doing_html=doing_html
                )
                # Mark the entire column as "rowheader"...
                # This is intended for screenreaders.  It ALMOST works.
                # Unfortunately a bug in ORCA will read "Via, Go" instead of reading "Oakville"
                # when recapitulating the row header.  This is confusing so don't activate.
                # for y in range(1, row_count):
                #    t.attributes.iloc[y,x] = 'role="rowheader"'

            case "services":
                # in a span
                t.text.iloc[0, x] = text_presentation.get_services_column_header(
                    doing_html=doing_html
                )
            case "access":
                # in a span
                t.text.iloc[0, x] = text_presentation.get_access_column_header(
                    doing_html=doing_html
                )
            case "timezone":
                # in a span
                t.text.iloc[0, x] = text_presentation.get_timezone_column_header(
                    doing_html=doing_html
                )
            case _:
                # it's actually a train, or several trains
                # Check column options for reverse, days, ardp:
                reverse = "reverse" in column_options[x]
                use_daystring = "days" in column_options[x]
                long_days_box = "long-days-box" in column_options[x]
                short_days_box = "short-days-box" in column_options[x]
                this_column_gets_ardp = "ardp" in column_options[x]
                no_rd = "no-rd" in column_options[x]

                # Separate train numbers by "/", and create the train_spec list
                train_specs = split_trains_spec(column_key_str)
                t.text.iloc[0, x] = text_presentation.get_time_column_header(
                    train_specs,
                    route_from_train_spec_local,
                    doing_html=doing_html,
                    train_numbers_side_by_side=train_numbers_side_by_side,
                )
                if doing_html:
                    # Style the header with the color & styling for the first tsn
                    # ...which isn't "noheader"...
                    # ...because I don't know how to do multiples! FIXME
                    header_styling_train_spec = None
                    for potential_train_spec in train_specs:
                        if potential_train_spec.endswith("noheader"):
                            continue
                        else:
                            header_styling_train_spec = potential_train_spec
                            break
                    if header_styling_train_spec:
                        column_header_css_list.append(
                            get_time_column_stylings(
                                header_styling_train_spec, route_from_train_spec_local
                            )
                        )
                # Check whether this column has any buses which should be marked
                use_bus_icon_this_column = False
                if use_bus_icon_in_cells:
                    for train_spec in train_specs:
                        train_spec = train_spec.removesuffix("noheader").strip()
                        route = route_from_train_spec_local(train_spec)
                        if route.route_type == 3:
                            # We have found a bus
                            use_bus_icon_this_column = True
                            break

                # Check whether this column has any checked baggage
                use_baggage_icon_this_column = False
                for train_spec in train_specs:
                    potential_baggage_tsn = train_spec_to_tsn(train_spec)
                    if agency_singleton().train_has_checked_baggage(
                        potential_baggage_tsn
                    ):
                        use_baggage_icon_this_column = True
                        break

        # Fill in CSS styles for this column header
        t.classes.iloc[0, x] = " ".join(column_header_css_list)
        # Set this column header to be a header
        t.th.iloc[0, x] = True
        # ...with column scope (although that's usually automatic)
        t.attributes.iloc[0, x] = 'scope="col" role="columnheader"'

        # Cache this for use in "origin" and "destination";
        # it only looks at the first tsn.
        # It won't fill on special columns, which is OK
        if train_specs:
            train_spec = train_specs[0]  # Look only at the first train in the column
            train_spec = train_spec.removesuffix("noheader").strip()
            col_trip_id = train_spec_to_trip_id[train_spec]
            stations_df_for_column = stations_list_from_trip_id(today_feed, col_trip_id)

        for y in range(1, row_count):  # First (0) row is the header
            station_code = str(spec.csv.iloc[y, 0])  # row y, column 0

            # Reset the styler string:
            cell_css_list = [*base_cell_css_list]
            # Check for cell_codes like "28 last".  This *usually* returns None.
            cell_codes = get_cell_codes(str(spec.csv.iloc[y, x]), train_specs)

            # Check for simple cell substitutions like "blank" and "downarrow".
            # Returns None or a string.
            cell_substitution = text_presentation.get_cell_substitution(
                str(spec.csv.iloc[y, x])
            )
            if cell_substitution:
                spec.csv.iloc[y, x] = cell_substitution

            # This is effectively matching row, column, cell contents in spec
            match [station_code.lower(), column_key_str.lower(), spec.csv.iloc[y, x]]:
                case ["", _, ""]:
                    # Make sure blanks become *string* blanks in this line.
                    t.text.iloc[y, x] = ""
                case ["", _, raw_text]:
                    # This is probably raw text like "To Chicago".
                    # But it might be a cell code.  We only accept "91 blank".
                    # Note that the simple substitutions were processed earlier.
                    if cell_codes and cell_codes["blank"]:
                        t.text.iloc[y, x] = ""
                        cell_css_list.append("blank-cell")
                        blank_train_spec = cell_codes["train_spec"]
                        cell_css_list.append(
                            get_time_column_stylings(
                                blank_train_spec, route_from_train_spec_local
                            )
                        )
                    else:
                        # This is probably special text like "to Chicago".
                        cell_css_list.append("special-cell")
                        # Copy the handwritten text over.
                        t.text.iloc[y, x] = raw_text
                case ["route-name", ck, raw_text] if ck in special_column_names:
                    # Usually blank for special columns, but could be free-written text
                    cell_css_list.append("route-name-cell")
                    t.text.iloc[y, x] = raw_text or ""
                case ["route-name", _, _]:
                    # Line for route names.
                    cell_css_list.append("route-name-cell")
                    route_names: list[str] = []
                    styled_route_names: list[str] = []
                    styled_already = False
                    for train_spec in train_specs:
                        if train_spec.endswith("noheader"):
                            continue
                        my_trip = trip_from_train_spec_local(train_spec)
                        route_id = my_trip.route_id
                        # Clean this interface up later.  FIXME
                        route_name = agency_singleton().get_route_name(
                            today_feed, route_id
                        )
                        styled_route_name = (
                            text_presentation.style_route_name_for_column(
                                route_name, doing_html=doing_html
                            )
                        )
                        if not route_names or route_names[-1] != route_name:
                            # Don't duplicate if same route as previous train in slashed list
                            route_names.append(route_name)
                            styled_route_names.append(styled_route_name)
                        if not styled_already:
                            # Color based on the first one which isn't noheader.
                            cell_css_list.append(
                                get_time_column_stylings(
                                    train_spec, route_from_train_spec_local
                                )
                            )
                            styled_already = True
                    if doing_html:
                        separator = "<hr>"
                    else:
                        separator = "\n"
                    full_styled_route_names = separator.join(styled_route_names)
                    t.text.iloc[y, x] = full_styled_route_names
                case ["updown", ck, raw_text] if ck in special_column_names:
                    cell_css_list.append("updown-cell")
                    t.text.iloc[y, x] = raw_text or ""
                case ["updown", _, _]:
                    # Special line just to say "Read Up" or "Read Down"
                    cell_css_list.append("updown-cell")
                    t.text.iloc[y, x] = text_presentation.style_updown(
                        reverse, doing_html=doing_html
                    )
                case [
                    "days" | "days-of-week",
                    ck,
                    raw_text,
                ] if ck in special_column_names:
                    cell_css_list.append("days-of-week-cell")
                    t.text.iloc[y, x] = raw_text or ""
                case ["days" | "days-of-week", _, ""]:
                    cell_css_list.append("days-of-week-cell")
                    # No reference stop?  Maybe this should be blank.
                    # Useful if one train runs across midnight.
                    t.text.iloc[y, x] = ""
                    # Color this cell
                    # FIXME, currently using color from first tsn only
                    cell_css_list.append(
                        get_time_column_stylings(
                            train_specs[0], route_from_train_spec_local
                        )
                    )
                case ["days" | "days-of-week", _, reference_stop_code]:
                    reference_stop_id = agency_singleton().stop_code_to_stop_id(
                        reference_stop_code
                    )
                    # Days of week -- best for a train which doesn't run across midnight
                    cell_css_list.append("days-of-week-cell")
                    # We can only show the days for one station.
                    # So get the reference stop_id / station code to use; user-specified
                    if len(train_specs) > 1:
                        print(
                            "Warning: using only ", train_specs[0], " for days header"
                        )
                    my_trip = trip_from_train_spec_local(train_specs[0])
                    timepoint = today_feed.get_timepoint_from_trip_id(
                        my_trip.trip_id, reference_stop_id
                    )
                    if timepoint is None:
                        # Manual override?  Pass the raw text through.
                        raw_text = reference_stop_code
                        t.text.iloc[y, x] = raw_text
                    else:
                        # Automatically calculated day string.
                        # Pull out the timezone for the reference_stop_id (should precache as dict, TODO)
                        stop_df = today_feed.stops[
                            today_feed.stops.stop_id == reference_stop_id
                        ]
                        stop_tz = stop_df.iloc[0].stop_timezone
                        zonediff = get_zonediff(stop_tz, agency_tz, reference_date)
                        # Get the day change for the reference stop (format is explained in text_presentation)
                        departure = explode_timestr(timepoint.departure_time, zonediff)
                        offset = int(departure.day)
                        # Finally, get the calendar (must be unique)
                        calendar = today_feed.calendar[
                            today_feed.calendar.service_id == my_trip.service_id
                        ]
                        # And fill in the actual string
                        daystring = day_string(calendar, offset=offset)
                        # TODO: add some HTML styling here
                        t.text.iloc[y, x] = daystring
                    # Color this cell
                    # FIXME, currently using color from first tsn only
                    cell_css_list.append(
                        get_time_column_stylings(
                            train_specs[0], route_from_train_spec_local
                        )
                    )
                case [_, _, raw_text] if raw_text != "" and not cell_codes:
                    # Line led by a station code,
                    # Or "origin", "destination", but cell already has a value.
                    # and the value isn't one of the special codes we check later.
                    cell_css_list.append("special-cell")
                    # This is probably special text like "to Chicago".
                    # Copy the handwritten text over.
                    t.text.iloc[y, x] = raw_text
                case ["origin" | "destination", "station" | "stations", _]:
                    # Fill in the station column with blank space.
                    # This prevents the line from "compacting" on pages with no origin cells,
                    # Which is important for the NEC.
                    t.text.iloc[y, x] = text_presentation.get_origin_destination_spacer(
                        doing_html=doing_html
                    )
                case [
                    "origin" | "destination",
                    ck,
                    raw_text,
                ] if ck in special_column_names:
                    # Free-written text was checked earlier
                    t.text.iloc[y, x] = raw_text or ""
                case ["origin", _, _]:
                    # Get the originating station for the train, and
                    # IF it is not in this timetable, print something appropriate
                    # Only looks at the first tsn.  (FIXME)
                    # Free-written text was checked earlier
                    first_station_code = stations_df_for_column.iat[0]
                    if first_station_code not in station_codes_list:
                        t.text.iloc[y, x] = agency_singleton().get_station_name_from(
                            first_station_code,
                            doing_multiline_text=doing_multiline_text,
                            doing_html=doing_html,
                        )
                    else:
                        t.text.iloc[y, x] = ""
                case ["destination", _, _]:
                    # Get the final (terminating) station for the train, and
                    # IF it is not in this timetable, print something appropriate
                    # Only looks at the first tsn. (FIXME)
                    # Free-written text was checked earlier
                    last_station_code = stations_df_for_column.iat[-1]
                    if last_station_code not in station_codes_list:
                        t.text.iloc[y, x] = agency_singleton().get_station_name_to(
                            last_station_code,
                            doing_multiline_text=doing_multiline_text,
                            doing_html=doing_html,
                        )
                    else:
                        t.text.iloc[y, x] = ""
                case [_, "station" | "stations", _]:
                    # Line led by a station code, column for station names
                    cell_css_list.append("station-cell")
                    # FIXME: no way to tell it to use connecting services or not to.
                    station_name_str = agency_singleton().get_station_name_pretty(
                        station_code,
                        doing_html=doing_html,
                        doing_multiline_text=doing_multiline_text,
                    )
                    t.text.iloc[y, x] = station_name_str
                    # This oughta be a th.  But this will make ORCA think it's on the left.
                    # (in Chromium and partially in Firefox)
                    # t.th.iloc[y, x] = True
                    # t.attributes.iloc[y, x] = 'scope="row"'
                    # So it's not OK.
                    # Try this instead:
                    # t.attributes.iloc[y,x] = 'role="rowheader"'
                    # This works better.  But it goes weird when transitioning from
                    # a header colum into the row.  FIXME
                    # We instead run through the whole column earlier (processing the headers).

                    # Now for screen readers we don't want to read that WHOLE thing
                    # every time we're looking at a cell, but we do want to read the city.
                    # So we add the city as an abbr attribute
                    # Does not work in ORCA on Firefox or Chromium.
                    # station_name_short = agency_singleton().get_station_name_short(
                    #    station_code,
                    #    doing_multiline_text=doing_multiline_text,
                    #    doing_html=doing_html,
                    # )
                    # station_name_short_escaped = html.escape(station_name_short)
                    # t.th.iloc[y, x] = True
                    # t.attributes.iloc[y, x] += f'abbr="{station_name_short_escaped}"'
                case [_, "services", _]:
                    # Column for station services codes.  Currently, completely vacant.
                    cell_css_list.append("services-cell")
                    services_str = ""
                    t.text.iloc[y, x] = services_str
                case [_, "access", _]:
                    cell_css_list.append("access-cell")
                    access_str = ""
                    if agency_singleton().station_has_accessible_platform(station_code):
                        access_str += icons.get_accessible_icon_html(
                            doing_html=doing_html
                        )
                    elif agency_singleton().station_has_inaccessible_platform(
                        station_code
                    ):
                        access_str += icons.get_inaccessible_icon_html(
                            doing_html=doing_html
                        )
                    t.text.iloc[y, x] = access_str
                case [_, "timezone", _]:
                    # Pick out the stop timezone -- TODO, precache this as a dict
                    stop_id = agency_singleton().stop_code_to_stop_id(station_code)
                    stop_df = today_feed.stops[today_feed.stops.stop_id == stop_id]
                    stop_tz = stop_df.iloc[0].stop_timezone
                    cell_css_list.append("timezone-cell")
                    t.text.iloc[y, x] = get_zone_str(stop_tz, doing_html=doing_html)
                case [_, _, _]:
                    # Line led by station code, column led by train numbers,
                    # cell empty or has a "cell code": the normal case -- we need to fill in a time.

                    # For a slashed train spec ( 549 / 768 ) pull the *first* train's times,
                    # then the second train's times *if the first train doesn't stop there*

                    # For connecting trains, use two different rows and use cell codes.

                    # Convert station_code to stop_id
                    stop_id = agency_singleton().stop_code_to_stop_id(station_code)

                    # Pick out the stop timezone -- TODO, precache this as a dict
                    stop_df = today_feed.stops[today_feed.stops.stop_id == stop_id]
                    try:
                        stop_tz = stop_df.iloc[0].stop_timezone
                    except BaseException as err:
                        print("While finding time zone at", station_code)
                        raise

                    debug_print(
                        3,
                        "Trainspecs: " + str(train_specs) + "; Station:" + station_code,
                    )

                    # Extract my_trip, timepoint (and later calendar)
                    # Note that in Python variables defined in a loop "hang around"

                    if cell_codes and cell_codes["train_spec"]:
                        # Specific train_spec was requested.
                        debug_print(2, "cell codes found: ", cell_codes)
                        train_specs_to_check = [cell_codes["train_spec"]]
                    else:
                        train_specs_to_check = [
                            train_spec.removesuffix("noheader").strip()
                            for train_spec in train_specs
                        ]

                    for train_spec in train_specs_to_check:
                        my_trip = trip_from_train_spec_local(train_spec)
                        debug_print(2, "debug trip_id:", train_spec, my_trip.trip_id)
                        timepoint = today_feed.get_timepoint_from_trip_id(
                            my_trip.trip_id, stop_id
                        )
                        if timepoint is not None:
                            # Use the FIRST one which returns a timepoint
                            break

                    if (timepoint is None) or (cell_codes and cell_codes["blank"]):
                        # This train does not stop at this station
                        # *** Or we've been told to make a colored blank cell ***
                        t.text.iloc[y, x] = ""
                        cell_css_list.append("blank-cell")
                        # For now, we style if we have a single train.
                        # Including if it's specified with a cell code like "94 blank".
                        # Otherwise, leave it white, because it's hard to know what color to use.
                        if len(train_specs_to_check) == 1:
                            cell_css_list.append(
                                get_time_column_stylings(
                                    train_specs_to_check[0], route_from_train_spec_local
                                )
                            )
                    else:
                        # *** MAIN ROUTINE FOR PUTTING A TIME IN A CELL ***
                        # We have a station code, and a specific tsn
                        cell_css_list.append("time-cell")
                        cell_css_list.append(
                            get_time_column_stylings(
                                train_spec, route_from_train_spec_local
                            )
                        )

                        calendar = None  # if not use_daystring, save time
                        if use_daystring:
                            calendar = today_feed.calendar[
                                today_feed.calendar.service_id == my_trip.service_id
                            ]

                        has_baggage = bool(
                            agency_singleton().train_has_checked_baggage(
                                train_spec_to_tsn(train_spec)
                            )
                            and agency_singleton().station_has_checked_baggage(
                                station_code
                            )
                        )

                        # Should we put the bus symbol on this cell?
                        # Only if the timetable wants to use them,
                        # And only if it is actually a bus.
                        is_bus = False
                        if use_bus_icon_this_column:
                            route = route_from_train_spec_local(train_spec)
                            if route.route_type == 3:
                                # It is a bus!
                                is_bus = True

                        # Normally we are two_row if the station calls for it,
                        # but (hackishly) we allow the cell_codes to override it.
                        # This isn't quite right as it should be station specific.
                        two_row = is_ardp_station(station_code)

                        # MUST figure first_stop and last_stop
                        # ...which means we need to make earlier passes through the table FIXME
                        # But for now we can handle it with manual annotation in the spec
                        is_first_stop = False
                        is_last_stop = False
                        if cell_codes:
                            is_first_stop = cell_codes["first"]
                            is_last_stop = cell_codes["last"]
                            if is_first_stop or is_last_stop:
                                two_row = False
                            if cell_codes["two_row"]:
                                # Allow spec creator to force two_row
                                two_row = True

                        cell_text = text_presentation.timepoint_str(
                            timepoint,
                            stop_tz=stop_tz,
                            agency_tz=agency_tz,
                            reference_date=reference_date,
                            doing_html=doing_html,
                            box_time_characters=box_time_characters,
                            reverse=reverse,
                            two_row=two_row,
                            use_ar_dp_str=this_column_gets_ardp,
                            times_24h=times_24h,
                            use_daystring=use_daystring,
                            calendar=calendar,
                            long_days_box=long_days_box,
                            short_days_box=short_days_box,
                            is_first_stop=is_first_stop,
                            is_last_stop=is_last_stop,
                            use_baggage_icon=use_baggage_icon_this_column,
                            has_baggage=has_baggage,
                            use_bus_icon=use_bus_icon_this_column,
                            is_bus=is_bus,
                            no_rd=no_rd,
                        )
                        t.text.iloc[y, x] = cell_text
            # Fill the styler.  We MUST overwrite every single cell of the styler.
            t.classes.iloc[y, x] = " ".join(cell_css_list)

    # Row 0 and column 0 might not have been filled.
    t.text.fillna(value="", inplace=True)
    # debug_print(1, "Text table:", t.text)
    t.classes.fillna(value="", inplace=True)
    # debug_print(1, "Classes table:", t.classes)
    # This is only set if it's "True"; fill in the "False" states.
    t.th.fillna(value=False, inplace=True)
    # This is only set if it's not empty; fill in the "" states.
    t.attributes.fillna(value="", inplace=True)  # Correct default

    return t
