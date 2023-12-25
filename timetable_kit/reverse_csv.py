#! /usr/bin/env python3
# reverse_csv.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

import sys
import pandas as pd
from pandas import DataFrame

"""
This simply reverses the rows in a CSV file
"""

# TO DO: do a smarter parse of this.
# Keep header rows at the top,
# Swap order of reversed columns vs. non-reversed columns,
# swap "reverse" vs non-reverse column-options.
# However, that can all be done in a spreadsheet easily.
# This part cannot.

if __name__ == "__main__":
    # Simple interface.
    filename = sys.argv[1]
    out_filename = filename.removesuffix(".csv") + "_reversed.csv"

    tt_spec = pd.read_csv(filename, index_col=False, header=None, dtype=str)
    reversed_tt_spec = tt_spec[::-1]

    reversed_tt_spec.to_csv(out_filename, index=False, header=False)
    print("reversed.")
