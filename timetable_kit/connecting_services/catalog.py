# connecting_services/catalog.py
# Part of timetable_kit
#
# Copyright 2022, 2023, 2024 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""This module holds the list of known connecting services, with their icon files, CSS
files, CSS class names, etc.

It is automatically extracted from a CSV file in this package, specified in
connecting_services_csv_filename

The exported data is get_connecting_services_df() (as a DataFrame) and
get_connecting_services_dict() (as a dict)
"""
# For reading a string as a CSV
from io import StringIO

# For memoization.  This is crucial; these functions are slow.
from functools import cache

from jinja2 import Template  # for typehints

# We need PANDAS for this
import pandas as pd

# Mine
from timetable_kit.debug import debug_print
from timetable_kit.load_resources import (
    # For actually retrieving the desired CSV file from the package, as a string
    get_connecting_services_csv,
    # For retrieving the CSS files which go with the SVGs
    get_logo_css,
    # For templates for producing the HTML fragments to be used in the final timetable
    template_environment,
)

### GLOBALS ####
# This is the source filename
connecting_services_csv_filename = "connecting_services.csv"


# Internal use: Jinja templates after loading them
# Load once, save using memoization
@cache
def _get_connecting_service_logo_tpl() -> Template:
    """Return Jinja template for connecting service logo HTML.

    Memoized.
    """
    return template_environment.get_template("connecting_service_logo.html")


@cache
def _get_connecting_service_logo_key_tpl() -> Template:
    """Return Jinja template for connecting service logo key HTML.

    Memoized.
    """
    return template_environment.get_template("connecting_service_logo_key.html")


# Not memoized!
def _generate_logo_html(df_row: pd.Series) -> str:
    """Apply JINJA template to a row and get a value for a new
    column, which will be the HTML to refer to the logo (in a station name box)"""
    params = df_row.to_dict()
    output = _get_connecting_service_logo_tpl().render(params)
    return output


# Not memoized!
def _generate_logo_key_html(df_row: pd.Series) -> str:
    """Apply JINJA template to a row and get a value for a new
    column, which will be the HTML to explain the logo in the symbol key for the
    timetable."""
    params = df_row.to_dict()
    output = _get_connecting_service_logo_key_tpl().render(params)
    return output


@cache
def get_connecting_services_df() -> pd.DataFrame:
    """Return the DataFrame of connecting services information.

    Memoized.  Computes on first use, then caches permanently.

    Initialized from a .csv file in the package.  Takes a long time to construct.
    """
    debug_print(1, "Initializing get_connecting_services_df()")

    # First acquire the CSV file as a string
    connecting_services_csv_str = get_connecting_services_csv(
        connecting_services_csv_filename
    )

    # Treat the string as a file
    pseudo_file = StringIO(connecting_services_csv_str)

    # Now turn it into a DataFrame
    # (this is what we will return and cache)
    connecting_services_df = pd.read_csv(
        pseudo_file, index_col=False, header=0, dtype=str
    )

    # Add a column for the SVG filename:
    connecting_services_df["svg_filename"] = (
        connecting_services_df["logo_filename"] + ".svg"
    )
    # Add a column for the CSS fragment filename:
    connecting_services_df["css_filename"] = (
        connecting_services_df["logo_filename"] + ".css"
    )
    # Add a column for the CSS class names:
    # Must come before the Jinja template usage!
    connecting_services_df["class"] = connecting_services_df["service_code"] + "_logo"

    # Before applying Jinja, we have to replace NaNs in the logo_filename and suffix column with
    # "" or something falsy.  Do this in place.
    connecting_services_df.fillna("", inplace=True)

    # Apply Jinja templates to the dataframe -- axis = "columns" applies function to each row
    connecting_services_df["logo_html"] = connecting_services_df.apply(
        _generate_logo_html, axis="columns"
    )
    connecting_services_df["logo_key_html"] = connecting_services_df.apply(
        _generate_logo_key_html, axis="columns"
    )

    # Reset the DataFrame index, in place, to be service_code
    # Must be done after generating "class" column
    # Must be done before most things which use connecting_services_df are called
    # (including get_filenames_for_all_logos and get_css_for_all_logos)
    connecting_services_df.set_index("service_code", inplace=True)

    debug_print(1, "Initialized get_connecting_services_df()")
    # Return (and cache!) the DataFrame
    return connecting_services_df


@cache
def get_connecting_services_dict() -> dict[str, dict[str, str]]:
    """Return the dict of connecting services information.

    Memoized.  Computes on first use, then caches permanently.

    Format is service_code->{column->entry}
    """
    # Depends on initializing get_connecting_services_df() first
    connecting_services_dict = get_connecting_services_df().to_dict(orient="index")
    debug_print(1, "Connecting services dict initialized")
    # Return (and cache!) the dict
    return connecting_services_dict


def get_filenames_for_all_logos() -> list[str]:
    """Get the list of filenames for logos (without directories), for installing with
    the HTML files."""
    logo_svg_filenames = get_connecting_services_df()["svg_filename"].tolist()
    # Pull the appropriate column, convert to a list
    # debug_print(1, logo_svg_filenames)
    filtered_logo_svg_filenames = [
        filename
        for filename in logo_svg_filenames
        if not pd.isna(filename) and filename
    ]
    return filtered_logo_svg_filenames


def get_css_for_all_logos() -> str:
    """Get the CSS code to style all the icons we're using."""
    logo_css_filenames = get_connecting_services_df()["css_filename"].tolist()
    logo_css_list = [
        get_logo_css(filename)
        for filename in logo_css_filenames
        if not pd.isna(filename) and filename
    ]
    logo_css_all = "".join(logo_css_list)
    return logo_css_all


##### TESTING CODE ######
if __name__ == "__main__":
    print(get_connecting_services_dict())
