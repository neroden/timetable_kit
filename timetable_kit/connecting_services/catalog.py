# connecting_services/catalog.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
This module holds the list of known connecting services, with
their icon files, CSS files, CSS class names, etc.

It is automatically extracted from a CSV file in this package,
specified in connecting_agencies_csv_filename

The exported data is connecting_agencies_df (as a DataFrame)
and connecting_agencies_dict (as a dict)
"""


# For reading a string as a CSV
from io import StringIO

# We need PANDAS for this
import pandas as pd

# Mine
from timetable_kit.debug import debug_print

# FIXME: can we put this into the subpackage?  Is there a cleaner approach?
# For actually retrieving the desired CSV file from the package, as a string
import timetable_kit.load_resources
from timetable_kit.load_resources import get_connecting_agencies_csv

# For retrieving the CSS files which go with the SVGs
from timetable_kit.load_resources import get_logo_css

# This is the source filename
connecting_agencies_csv_filename = "connecting_agencies.csv"

# This is the global -- it's a public interface.
connecting_agencies_dict = None
# This is also a global -- useful sometimes.
connecting_agencies_df = None


def initialize_connecting_agencies_dict():
    """
    Initialize the connecting agencies DataFrame and dictionary from a suitable file in the package.
    """
    print("Initializing connecting agencies dict")

    # First acquire the CSV file as a string
    # This is a read-only global:
    # global connecting_agencies_database_filename
    connecting_agencies_csv_str = get_connecting_agencies_csv(
        connecting_agencies_csv_filename
    )

    # Treat the string as a file
    pseudo_file = StringIO(connecting_agencies_csv_str)

    # Now turn it into a dataframe (and hang onto it, this is a global)
    global connecting_agencies_df
    connecting_agencies_df = pd.read_csv(
        pseudo_file, index_col=False, header=0, dtype=str
    )

    # Enhance it with derived columns
    connecting_agencies_df["svg_filename"] = (
        connecting_agencies_df["logo_filename"] + ".svg"
    )
    connecting_agencies_df["css_filename"] = (
        connecting_agencies_df["logo_filename"] + ".css"
    )
    connecting_agencies_df["class"] = connecting_agencies_df["agency_code"] + "_logo"

    # Reset the index, in place
    connecting_agencies_df.set_index("agency_code", inplace=True)

    # Now create the dict.
    global connecting_agencies_dict
    connecting_agencies_dict = connecting_agencies_df.to_dict(orient="index")

    print("Connecting agencies dict initialized")


def get_filenames_for_all_logos() -> list[str]:
    """
    Get the list of filenames for logos (without directories), for installing with the HTML files
    """
    # Pull the appropriate column, convert to a list
    logo_svg_filenames = connecting_agencies_df["svg_filename"].tolist()
    debug_print(1, logo_svg_filenames)
    return logo_svg_filenames


def get_css_for_all_logos() -> str:
    """
    Get the CSS code to style all the icons we're using.
    """
    logo_css_filenames = connecting_agencies_df["css_filename"].tolist()
    logo_css_list = [get_logo_css(filename) for filename in logo_css_filenames]
    logo_css_all = "".join(logo_css_list)
    return logo_css_all


###### INITIALIZATION CODE ######
# Initialize the global when this file is loaded.
initialize_connecting_agencies_dict()

##### TESTING CODE ######
if __name__ == "__main__":
    print(connecting_agencies_dict)
