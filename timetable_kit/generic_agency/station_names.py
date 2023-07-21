# generic_agency/station_names.py
# Stub file for code deduplication for station_names.py in implemented agencies
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
import re
from typing import Optional

STATION_NAME_RE = re.compile(
    # station name       facility name (optional)  station code
    r"(.+,\s[A-Z]{2})\s  (?:-\s(.+)\s)?            \(([A-Z]{3})\)",
    re.X,  # This ignores the whitespace. The actual matched spaces are the \s tokens.
)


def parse_station_name(station_name: str) -> tuple[str, Optional[str], str]:
    facility_name: Optional[str]
    (city_state_name, facility_name, station_code) = re.match(
        STATION_NAME_RE, station_name
    ).groups()
    return city_state_name, facility_name, station_code
