# timetable_class.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Data structure to hold styles and other non-textual information for the output timetable.

Created when PANDAS's Styler wasn't doing what I wanted.
"""

import os  # for os.PathLike

import pandas as pd
from pandas import DataFrame

from jinja2 import Template  # for typehints

# My packages
from timetable_kit.debug import debug_print

# For the Jinja templates
from timetable_kit.load_resources import template_environment


class Timetable:
    """Represents a laid-out timetable with styling

    This is used both before and after layout.
    It is filled in by fill_tt_spec in an encapsulation-breaking way.
    """

    # Internal use: Jinja templates after loading
    _table_tpl: Template | None = None

    def __init__(self, spec_df: pd.DataFrame) -> None:
        """Pass in the CSV part of a spec as a dataframe, which is used only for its shape"""
        (row_index, col_index) = spec_df.axes
        # Timetable (text)
        self.text = pd.DataFrame(
            index=row_index.copy(deep=True), columns=col_index.copy(deep=True)
        )
        # Classes (for CSS)
        self.classes = pd.DataFrame(
            index=row_index.copy(deep=True), columns=col_index.copy(deep=True)
        )
        # Boolean specifying whether to use th instead of td
        self.th = pd.DataFrame(
            index=row_index.copy(deep=True), columns=col_index.copy(deep=True)
        )
        # Attributes (for CSS) -- includes "rowheader" type stuff
        self.attributes = pd.DataFrame(
            index=row_index.copy(deep=True), columns=col_index.copy(deep=True)
        )
        # These are used to tell Jinja when to stop looping.
        # We will also use the row_count and col_count in the main loop to fill the timetable,
        # but we currently pull those separately.  (FIXME)
        (self.row_count, self.col_count) = spec_df.shape

        # These would be used naively by Jinja to loop, but we need something more complex...
        # Instead, they are not currently used.
        # self.row_nums = range(0, self.row_count)
        # self.col_nums = range(0, self.col_count)

        # These are used by Jinja to loop separately on <thead> and <tbody>.
        # For now, we do it the simple way, though we could be more complex.
        # Will require revision when transposed timetables are implemented (FIXME)
        assert self.row_count >= 1
        self.thead_row_nums = range(0, 1)
        self.tbody_row_nums = range(1, self.row_count)
        # This is used by Jinja to loop over columns
        # while skipping the do-not-print column number 0.
        # Will require revision when transposed timetables are implemented (FIXME)
        assert self.col_count >= 1
        self.printable_col_nums = range(1, self.col_count)

        debug_print(1, "Copied shape of spec.")
        # Things which go on the <table> tag
        # We can get these from the TTSpec.  Fix after rearranging modules. FIXME
        self.table_attributes = ""

    def write_csv_file(self, file: os.PathLike | str) -> None:
        """Write this out as a CSV file at the given path.

        Should run after fill_tt_spec.
        """
        # Lean on DataFrame.
        # NOTE, need to include the header
        self.text.to_csv(file, index=False, header=True)
        debug_print(1, "CSV written to", file)

    @classmethod
    def get_table_tpl(cls) -> Template:
        """Get the Jinja template for a whole table.

        Memoized
        """
        if cls._table_tpl is None:
            cls._table_tpl = template_environment.get_template("table.html")
        assert cls._table_tpl is not None
        return cls._table_tpl

    def render(self) -> str:
        """Render a timetable to HTML, using Jinja"""
        # Recall that Python dataframe data can be accessed as:
        # df[col][row]
        # Do this in Jinja

        # Retrieve with memoization
        table_tpl = self.get_table_tpl()

        t = self  # Make the dict shorter...
        params = {
            "table_attributes": t.table_attributes,
            "thead_row_nums": t.thead_row_nums,
            "tbody_row_nums": t.tbody_row_nums,
            "printable_col_nums": t.printable_col_nums,
            # These four are DataFrames
            "text": t.text,
            "classes": t.classes,
            "th": t.th,
            "attributes": t.attributes,
        }
        output = table_tpl.render(params)
        return output
