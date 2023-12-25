#! /usr/bin/env python3
# text_assembly.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Module for assembling small bits of text, mostly for disclaimers.

Contains bits which don't require tsns, but which are loaded early, to
avoid circular dependencies.
"""
import html  # for html.escape


def href_wrap(text: str, url: str, doing_html: bool = True) -> str:
    """Given text and a URL, wrap the text in an HREF anchor pointing to the
    URL.

    Escapes text and URL properly.

    if doing_html is false, prints text ( url ).
    """
    if doing_html:
        cooked_url = html.escape(url, quote=True)
        cooked_text = html.escape(text)
        return f'<a href="{cooked_url}">{cooked_text}</a>'
    else:
        # Plaintext version: print the URL.
        return f"{text} ( {url} )"


def and_clause(items: list[str]) -> list[str]:
    """Given a list of pieces of text, returns a new list of pieces of text,
    with the appropriate words added to make it an "and" clause if spaces are
    put in between.

    With an empty list, returns an empty list.  The odd interface is
    designed to make this work correctly if run through " ".join()
    """
    if len(items) == 0:
        return []

    if len(items) == 1:
        return items

    if len(items) == 2:
        return [items[0], "and", items[1]]

    # More than two items.  Use Oxford comma.
    comma_items = [item + "," for item in items[0:-1]]
    return [*comma_items, "and", items[-1]]


def or_clause(items: list[str]) -> list:
    """Given a list of pieces of text, returns a new list of pieces of text,
    with the appropriate words added to make it an "or" clause if spaces are
    put in between.

    With an empty list, returns an empty list.  The odd interface is
    designed to make this work correctly if run through " ".join()
    """
    if len(items) == 0:
        return []

    if len(items) == 1:
        return items

    if len(items) == 2:
        return [items[0], "or", items[1]]

    # More than two items.  Use Oxford comma.
    comma_items = [item + "," for item in items[0:-1]]
    return [*comma_items, "or", items[-1]]


def station_name_to_multiline_text(
    city_state_name: str,
    facility_name: str | None,
    station_code: str,
    major: bool = False,
) -> str:
    """Take a disassembled station name and assemble it to multi-line text.

    The format is:

    Chicago, IL (CHI)
    Union Station
    """
    # Major stations are in all uppercase.
    # Other stations are not.
    if major:
        city_state_name = city_state_name.upper()

    if facility_name:
        fancy_name = f"{city_state_name} ({station_code})\n - {facility_name}"
    else:
        fancy_name = f"{city_state_name} ({station_code})"

    return fancy_name


def station_name_to_single_line_text(
    city_state_name: str,
    facility_name: str | None,
    station_code: str,
    major: bool = False,
) -> str:
    """Take a disassembled station name and assemble it to single-line text.

    The format is:

    Chicago, IL - Union Station (CHI)

    or
    Chicago, IL (CHI)
    """
    # Major stations are in all uppercase.
    # Other stations are not.
    if major:
        city_state_name = city_state_name.upper()

    if facility_name:
        fancy_name = f"{city_state_name} - {facility_name} ({station_code})"
    else:
        fancy_name = f"{city_state_name} ({station_code})"

    return fancy_name


# TESTING
if __name__ == "__main__":
    print(station_name_to_single_line_text("Chicago, IL", "Union Station", "CHI", True))
    print(
        station_name_to_single_line_text("Chicago, IL", "Union Station", "CHI", False)
    )
    print(station_name_to_multiline_text("Chicago, IL", "Union Station", "CHI", True))
    print(station_name_to_multiline_text("Chicago, IL", "Union Station", "CHI", False))
