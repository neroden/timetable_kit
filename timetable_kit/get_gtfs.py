#! /usr/bin/env python3
# amtrak/get_gtfs.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Retrieve an agency's static GTFS data from the canonical location.

Store in appropriate directory: ~/.local/share/timetable_kit/<agency>/gtfs

Should not depend on anything else in timetable_kit,
since it's used during initalization of every <agency>/get_gtfs.py file.
"""

from typing import Self

import sys  # for sys.exit
from os import PathLike
from pathlib import Path
import shutil  # for rmtree


from xdg_base_dirs import xdg_data_home  # for where to put the files

from zipfile import ZipFile


import requests


def move_old_dir(dir: PathLike):
    """Move a named dir out of the way to dir.old"""
    # Move the directory out of the way as dir.old
    dir_old = str(dir) + ".old"
    if Path(dir_old).exists:
        try:
            shutil.rmtree(dir_old)
        except OSError as e:
            print(f"Failed to remove {dir_old} - at {e.filename} raised {e.strerror}.")
    dir.rename(dir_old)


def move_old_file(file: PathLike):
    """Move a named file out of the way to file.old"""
    # Move the file out of the way as file.old
    file_old = Path(str(file) + ".old")
    if file_old.exists():
        try:
            file_old.unlink()
        except OSError as e:
            print(f"Failed to remove {file_old} - at {e.filename} raised {e.strerror}.")
    file.rename(file_old)


class AgencyGTFSFiles:
    """Handles downloading agency GTFS, saving it, and loading it as needed"""

    def __init__(
        self: Self,
        agency_subdir: str,
        url: str,
        system: bool = False,
    ) -> None:
        """Initialize the locations for an agency's GTFS files.

        url: URL to download the zipped GTFS file from
        agency_subdir: name of subdir to use for agency data (eg "amtrak")
        system: Install in system directories rather than user home directory (not tested)
        """
        if system:
            _data_home = Path("/var/lib")
        else:
            _data_home = xdg_data_home()
        _ttkit_data_home = _data_home / "timetable_kit"
        self.agency_dir: Path = (
            _ttkit_data_home / agency_subdir
        )  # ~/.local/share/timetable_kit/amtrak

        self._file: Path = self.agency_dir / "gtfs.zip"  # File for zipped GTFS
        self._dir: Path = self.agency_dir / "gtfs"  # Directory for unzipped GTFS

        self._url: str = url  # URL to download zipped GTFS file from

    def download(self: Self) -> bytes:
        """Download GTFS from specified URL and return it as bytes."""
        print(f"Starting GTFS download from {self._url}")
        # We probably should have a timeout here but make it long: a whole minute
        response = requests.get(self._url, timeout=60)
        if response.status_code != requests.codes.ok:
            print(f"Download of {self._url} failed with error {response.status_code}.")
            response.raise_for_status()  # Raise an error
        print(f"Downloaded GTFS from {self._url}")
        return response.content

    def save(self: Self, gtfs_zipped_data: bytes):
        """Save zipped GTFS file in a canonical local location."""
        self.agency_dir.mkdir(parents=True, exist_ok=True)
        if self._file.exists():
            move_old_file(self._file)

        with open(self._file, "wb") as binary_zip_file:
            binary_zip_file.write(gtfs_zipped_data)
            print(f"Wrote GTFS data to {self._file}")

    def unzip(self: Self):
        """Unzip GTFS file from a canonical local location to a canonical local location.

        This is used directly by the program.
        """
        if self._dir.exists():
            move_old_dir(self._dir)

        self._dir.mkdir(parents=True, exist_ok=False)
        with ZipFile(self._file, "r") as my_zip:
            my_zip.extractall(path=self._dir)
            print(f"Extracted {self._file} to {self._dir}")

    def download_and_save(self: Self):
        """Download, save, and extract GTFS."""
        binary_data = self.download()
        self.save(binary_data)
        self.unzip()

    def is_downloaded(self: Self) -> bool:
        """Return true if there is a GTFS file in the appropriate location

        Used to avoid redundant downloading
        """
        return self._file.exists()

    def get_path(self: Self):
        """Return the path to the GTFS file (file or dir)

        For use by all the tools
        """
        # Let's keep it an implementation detail whether to get the
        # zipped or unzipped version
        return self._dir
