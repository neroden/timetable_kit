# connecting_services/catalog.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module holds the list of known connecting services, with
their icon files, CSS files, CSS class names, etc.

It is automatically extracted from a CSV file in this package,
specified in connecting_services_csv_filename

The exported data is connecting_services_df (as a DataFrame)
and connecting_services_dict (as a dict)
"""


# For reading a string as a CSV
from io import StringIO

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

# This is the global -- it's a public interface.
connecting_services_dict = None
# This is also a global -- useful sometimes.
connecting_services_df = None

# Internal use: Jinja templates after loading them
_connecting_service_logo_tpl = None
_connecting_service_logo_key_tpl = None


def _generate_logo_html(df_row):
    """
    A clever routine to apply JINJA template to a row and get a value for a new column,
    which will be the HTML to refer to the logo (in a station name box)
    """
    # Note that a single row is a Series, so this is Series.todict
    params = df_row.to_dict()
    output = _connecting_service_logo_tpl.render(params)
    return output


def _generate_logo_key_html(df_row):
    """
    A clever routine to apply JINJA template to a row and get a value for a new column,
    which will be the HTML to explain the logo in the symbol key for the timetable
    """
    # Note that a single row is a Series, so this is Series.todict
    params = df_row.to_dict()
    output = _connecting_service_logo_key_tpl.render(params)
    return output


def _generate_full_name_nbsp(df_row):
    """
    Given a row, take the "full_name" entry and generate a version with nonbreaking spaces
    """
    full_name = df_row["full_name"]
    full_name_nbsp = full_name.replace(" ", "&nbsp;")
    return full_name_nbsp


def _generate_alt_nbsp(df_row):
    """
    Given a row, take the "alt" entry and generate a version with nonbreaking spaces
    """
    alt = df_row["alt"]
    alt_nbsp = alt.replace(" ", "&nbsp;")
    return alt_nbsp


def _generate_suffix_nbsp(df_row):
    """
    Given a row, take the "suffix" entry and generate a version with nonbreaking spaces
    """
    suffix = df_row["suffix"]
    suffix_nbsp = suffix.replace(" ", "&nbsp;")
    return suffix_nbsp


### FUNCTIONS ###
def _initialize():
    """
    Initialize the connecting services DataFrame and dict from a suitable file in the package.
    """
    # Don't print these, it interferes with output because debug_level isn't set yet.
    # Consider wrapping the dict in a function and memoizing.  TODO
    # debug_print(1, "Initializing connecting_services_df")

    # First acquire the CSV file as a string
    # This is a read-only global:
    # global connecting_services_database_filename
    connecting_services_csv_str = get_connecting_services_csv(
        connecting_services_csv_filename
    )

    # Treat the string as a file
    pseudo_file = StringIO(connecting_services_csv_str)

    # Now turn it into a dataframe (and hang onto it, this is a global)
    global connecting_services_df
    connecting_services_df = pd.read_csv(
        pseudo_file, index_col=False, header=0, dtype=str
    )

    # Don't print these, it interferes with output because debug_level isn't set yet.
    # Consider wrapping the dict in a function and memoizing.  TODO
    # debug_print(1, "Adding computed columns to connecting_services_df")

    # This one is used to install the logo files:
    connecting_services_df["svg_filename"] = (
        connecting_services_df["logo_filename"] + ".svg"
    )
    # This to accumulate CSS fragments:
    connecting_services_df["css_filename"] = (
        connecting_services_df["logo_filename"] + ".css"
    )
    # Make the "full name" (used for the link in the key) have nonbreaking spaces:
    connecting_services_df["full_name_nbsp"] = connecting_services_df.apply(
        _generate_full_name_nbsp, axis=1
    )
    # Make the "alt" (used as the key when there's no logo) have nonbreaking spaces:
    connecting_services_df["alt_nbsp"] = connecting_services_df.apply(
        _generate_alt_nbsp, axis=1
    )
    # Make the "suffix" (used when the same logo covers several services) have nonbreaking spaces:
    connecting_services_df["suffix_nbsp"] = connecting_services_df.apply(
        _generate_suffix_nbsp, axis=1
    )
    # This is the CSS class names:
    # Must come before the Jinja template usage!
    connecting_services_df["class"] = connecting_services_df["service_code"] + "_logo"

    # Before applying Jinja, we have to replace NaNs in the logo_filename and suffix column with
    # "" or something falsy.  Do this in place.
    connecting_services_df.fillna("", inplace=True)

    # Load the Jinja template environments to generate HTML
    global _connecting_service_logo_tpl
    global _connecting_service_logo_key_tpl
    _connecting_service_logo_tpl = template_environment.get_template(
        "connecting_service_logo.html"
    )
    _connecting_service_logo_key_tpl = template_environment.get_template(
        "connecting_service_logo_key.html"
    )
    # Apply Jinja templates to the dataframe -- axis = 1 applies to each row
    connecting_services_df["logo_html"] = connecting_services_df.apply(
        _generate_logo_html, axis=1
    )
    connecting_services_df["logo_key_html"] = connecting_services_df.apply(
        _generate_logo_key_html, axis=1
    )

    # Don't print these, it interferes with output because debug_level isn't set yet.
    # Consider wrapping the dict in a function and memoizing.  TODO
    # debug_print(1, "Initializing connecting services dict")

    # Reset the DataFrame index, in place, to be service_code
    # Must be done after generating "class" column
    # Must be done before most things which use connecting_services_df are called
    # (including get_filenames_for_all_logos and get_css_for_all_logos)
    connecting_services_df.set_index("service_code", inplace=True)

    # Now create the dict. service_code->{column->entry}
    global connecting_services_dict
    connecting_services_dict = connecting_services_df.to_dict(orient="index")

    # Don't print these, it interferes with output because debug_level isn't set yet.
    # Consider wrapping the dict in a function and memoizing.  TODO
    # debug_print(1, "Connecting services dict initialized")


def get_filenames_for_all_logos() -> list[str]:
    """
    Get the list of filenames for logos (without directories), for installing with the HTML files
    """
    # Pull the appropriate column, convert to a list
    logo_svg_filenames = connecting_services_df["svg_filename"].tolist()
    debug_print(1, logo_svg_filenames)
    filtered_logo_svg_filenames = [
        filename
        for filename in logo_svg_filenames
        if not pd.isna(filename) and filename
    ]
    return filtered_logo_svg_filenames


def get_css_for_all_logos() -> str:
    """
    Get the CSS code to style all the icons we're using.
    """
    logo_css_filenames = connecting_services_df["css_filename"].tolist()
    logo_css_list = [
        get_logo_css(filename)
        for filename in logo_css_filenames
        if not pd.isna(filename) and filename
    ]
    logo_css_all = "".join(logo_css_list)
    return logo_css_all


###### INITIALIZATION CODE ######
# Initialize the globals when this file is loaded.
# Three stages.
_initialize()

##### TESTING CODE ######
if __name__ == "__main__":
    print(connecting_services_dict)
