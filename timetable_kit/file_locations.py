# file_locations.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Keep track of locations for data files."""

from os import PathLike
from pathlib import Path

from xdg_base_dirs import xdg_data_home


def get_timetable_kit_data_home(system: bool = False) -> Path:
    """Returns the base data storage directory for timetable_kit.

    Typically ~/.local/share/timetable_kit.
    """
    if system:
        _data_home = Path("/var/lib")
    else:
        _data_home = xdg_data_home()  # ~/.local/share
    return _data_home / "timetable_kit"


def get_search_list(base: PathLike) -> list[Path]:
    """Given a relative base resource type to search for (like "templates"), give a list of directories to search

    Typically [".","./templates","~/.local/share/timetable_kit/templates","/var/lib/timetable_kit/templates"]
    """
    base = Path(base)
    assert not base.is_absolute()
    return [
        Path("."),
        base,
        xdg_data_home() / "timetable_kit" / base,
        Path("/var/lib/timetable_kit") / base,
    ]
