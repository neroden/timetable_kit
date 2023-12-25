# greyhound/__init__.py
# Init file for greyhound subpackage of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""timetable_kit.greyhound subpackage."""

# The singleton instance of a class, for stateful memoization
from .agency import get_singleton

# These probably belong in their own file
# FIXME
from pathlib import Path

module_location = Path(__file__).parent
gtfs_zip_local_path = module_location / "greyhound.zip"
gtfs_unzipped_local_path = module_location / "gtfs"
