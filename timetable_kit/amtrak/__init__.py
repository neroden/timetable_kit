# antrak/__init.py__
# Init file for amtrak submodule of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

# I'll be quite honest; I don't know what I'm doing here.
# This seems to work to allow the parent package to say
#   import timetable_kit.amtrak
# and then use
#   amtrak.special_data.whatever
# later on.  This doesn't seem to work without these lines.
from . import (
    special_data,
    station_name_styling,
    )
