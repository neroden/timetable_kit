#! /usr/bin/env python3
# icons.py
# Part of timetable_kit
# Copyright 2022, 2023, 2024 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Stuff for dealing with icons.

This is intended to be flexible in the future. Weasyprint can only handle icons
referenced as img, or direct inline SVGs, but NOT referenced inline SVGs.

Referenced inline SVGs would be ideal for HTML-on-web output.

For now, we do strictly icons referenced as img.
"""
# Practically everything in this entire module is memoized.
# Compute-once, use-repeatedly.

from functools import cache  # For memoization

from timetable_kit.load_resources import (
    # For retrieving CSS files which go with the SVG files
    get_icon_css,
    # For templates for producing HTML fragments
    template_environment,
)


# Called once to copy the files
def get_filenames_for_all_icons() -> list[str]:
    """Determine the list of icon filenames which must be copied."""
    icon_filenames = [
        "accessible.svg",
        "inaccessible-ncn.svg",
        "baggage-ncn.svg",
        "bus-ncn.svg",
        "bed-solid.svg",
    ]
    return icon_filenames


# Called once per HTML document
def get_css_for_all_icons() -> str:
    """Get the CSS code to style all the icons we're using."""
    full_css = "\n".join(
        [
            get_accessible_icon_css(),
            get_inaccessible_icon_css(),
            get_baggage_icon_css(),
            get_bus_icon_css(),
            get_sleeper_icon_css(),
        ]
    )
    return full_css


# Use if icon is not available
accessible_letter = "W"


@cache
def get_accessible_icon_html(doing_html=True) -> str:
    """Return suitable HTML or plaintext for displaying the "wheelchair access" icon.

    Amtrak's data does not show full accessibility.  This is being used for basic
    platform accessibility at this time.
    """
    if not doing_html:
        return accessible_letter

    accessible_icon_tpl = template_environment.get_template("icon_accessible.html")
    params = {"accessible_letter": accessible_letter}
    return accessible_icon_tpl.render(params)


def get_accessible_icon_css():
    """Return suitable CSS for the wheelchair icon (loaded from a file)"""
    return get_icon_css("accessible.css")


# Use if icon is not available
inaccessible_letter = "N"


@cache
def get_inaccessible_icon_html(doing_html=True) -> str:
    """Return suitable HTML or plaintext for displaying the "no wheelchair access" icon."""
    if not doing_html:
        return inaccessible_letter

    inaccessible_icon_tpl = template_environment.get_template("icon_inaccessible.html")
    params = {"inaccessible_letter": inaccessible_letter}
    return inaccessible_icon_tpl.render(params)


def get_inaccessible_icon_css():
    """Return suitable CSS for the no-wheelchair icon (loaded from a file)"""
    return get_icon_css("inaccessible-ncn.css")


# Unicode has a "baggage claim" symbol :baggage_claim:
# ... but it's not appropriate and not supported by
# the fonts in Weasyprint.  :-(
# U+1F6C4

# Use if icon is not available
baggage_letter = "G"


@cache
def get_baggage_icon_html(doing_html=True) -> str:
    """Return suitable HTML or plaintext for displaying the baggage icon."""
    if not doing_html:
        return baggage_letter

    baggage_icon_tpl = template_environment.get_template("icon_baggage.html")
    params = {"baggage_letter": baggage_letter}
    return baggage_icon_tpl.render(params)


def get_baggage_icon_css():
    """Return suitable CSS for the baggage icon (loaded from a file)"""
    return get_icon_css("baggage-ncn.css")


# Use if icon is not available
bus_letter = "B"


@cache
def get_bus_icon_html(doing_html=True) -> str:
    """Return suitable HTML or plaintext for displaying the bus icon."""
    if not doing_html:
        return bus_letter

    bus_icon_tpl = template_environment.get_template("icon_bus.html")
    params = {"bus_letter": bus_letter}
    return bus_icon_tpl.render(params)


def get_bus_icon_css():
    """Return suitable CSS for the no-wheelchair icon (loaded from a file)"""
    return get_icon_css("bus-ncn.css")


# Use if icon is not available
sleeper_letter = "S"


@cache
def get_sleeper_icon_html(doing_html=True) -> str:
    """Return suitable HTML or plaintext for displaying the sleeper icon."""
    if not doing_html:
        return sleeper_letter

    sleeper_icon_tpl = template_environment.get_template("icon_sleeper.html")
    params = {"sleeper_letter": sleeper_letter}
    return sleeper_icon_tpl.render(params)


def get_sleeper_icon_css():
    """Return suitable CSS for the sleeper icon (loaded from a file)"""
    return get_icon_css("bed-solid.css")
