# styler.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Module to render a timetable (in the form of laid-out DataFrames) into HEML

Created when PANDAS's Styler wasn't doing what I wanted.
"""

import sys # for sys.exit

import pandas as pd
from pandas import DataFrame

# My packages
from timetable_kit.debug import debug_print
# Type to store laid-out timetable as a set of dataframes
from timetable_kit.timetable_class import Timetable
# For the Jinja templates
from timetable_kit.load_resources import template_environment

# Internal use: Jinja templates after loading
_table_tpl: str | None = None

def get_table_tpl():
    """Get the Jinja template for a whole table.

    Memoized
    """
    global _table_tpl
    if _table_tpl is None:
        _table_tpl = template_environment.get_template("table.html")
    assert _table_tpl is not None
    return _table_tpl

def render(t: Timetable):
    """Render a timetable to HTML, using Jinja"""
    # Recall that Python dataframe data can be accessed as:
    # df[col][row]
    # Do this in Jinja

    table_tpl = get_table_tpl()
    params = {
        "table_attributes": t.table_attributes,
        "row_nums": t.row_nums,
        "col_nums": t.col_nums,
        # These four are DataFrames
        "text": t.text,
        "classes": t.classes,
        "th": t.th,
        "attributes": t.attributes,
    }
    output = table_tpl.render(params)
    print(output)
    sys.exit(1)

