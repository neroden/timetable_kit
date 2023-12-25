# convenience_types.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Types used for extra type-checking."""

# Do this after working our way through the codebase to fix all calls
# from typing import NewType

# Do this for now
from typing import TypeAlias, NewType, NamedTuple

# This must be a date in YYYYMMDD format
# type GTFSDate = NewType("GTFSDate", str)
GTFSDate: TypeAlias = str

# This must be one of the GTFS_DAYS listed in feed_enhanced.py
# type GTFSDay = NewType("GTFSDay", str)
GTFSDay: TypeAlias = str


# Shared by timetable.py and page_layout.py
class HtmlAndCss(NamedTuple):
    """Container for fragment of HTML and associated fragment of CSS.

    The implementation of the container as dict vs. tuple is an
    implementation detail. It may change.
    """

    html_text: str
    css_text: str
