# timetable_class.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Data structure to hold styles and other non-textual information for the output timetable.

Created when PANDAS's Styler wasn't doing what I wanted.
"""

import pandas as pd
from pandas import DataFrame

from timetable_kit.debug import debug_print

class Timetable:
    """Represents a laid-out timetable with styling"""
    __init__(self, spec_df: DataFrame) -> None:
        """Pass in the CSV part of a spec as a dataframe, which is used only for its shape"""
        (row_index, column_index) = spec_df.axes
        # Timetable (text)
        tt = pd.DataFrame(
            index=row_index.copy(deep=True), columns=column_index.copy(deep=True)
        )
        # Classes (for CSS)
        classes_t = pd.DataFrame(
            index=row_index.copy(deep=True), columns=column_index.copy(deep=True)
        )
        # Boolean specifying whether to use th instead of td
        th_t = pd.DataFrame(
            index=row_index.copy(deep=True), columns=column_index.copy(deep=True)
        )
        # Attributes (for CSS) -- includes "rowheader" type stuff
        attributes_t = pd.DataFrame(
            index=row_index.copy(deep=True), columns=column_index.copy(deep=True)
        )
        # We will use the row_count and column_count later.
        (row_count, column_count) = spec_df.shape
        # These are needed by Jinja.
        row_nums = range(0, row_count)
        column_nums = range(0, column_count)
        debug_print(1, "Copied shape of spec.")
        # Things which go on the <table> tag
        table_attributes = ""
