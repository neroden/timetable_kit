#! /usr/bin/env python3
# icons.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Stuff for dealing with icons.

This is intended to be flexible in the future.
Weasyprint can only handle icons referenced as img,
or direct inline SVGs, but NOT referenced inline SVGs.

Referenced inline SVGs would be ideal for HTML-on-web output.

For now, we do strictly icons referenced as img.
"""

from timetable_kit.load_resources import get_icon_svg

# Unicode has a "baggage claim" symbol :baggage_claim:
# ... but it's not appropriate and not supported by
# the fonts in Weasyprint.  :-(
# U+1F6C4

baggage_img_str = " ".join(
    [
        "<img",
        'class="icon-img"',
        'src="icons/baggage-ncn.svg"',
        'alt="Baggage"',
        'title="Checked Baggage">',
    ]
)


def get_baggage_icon_html(embedded_svg=False) -> str:
    """
    Return suitable HTML for displaying the baggage icon.
    """
    # TODO: provide the alternate versions.
    if not embedded_svg:
        return baggage_img_str
    if embedded_svg:  # not tested
        str = get_icon_svg("baggage-ncn.svg")
        return str
    return icons_css


inaccessible_img_str = " ".join(
    [
        "<img",
        'class="icon-img"',
        'src="icons/inaccessible.svg"',
        'alt="Inaccessible for wheelchairs"',
        'title="Not wheelchair accessible">',
    ]
)


def get_inaccessible_icon_html(embedded_svg=False) -> str:
    """
    Return suitable HTML for displaying the "no wheelchair access" icon.
    """
    return inaccessible_img_str


accessible_img_str = " ".join(
    [
        "<img",
        'class="icon-img"',
        'src="icons/accessible.svg"',
        'alt="Accessible for wheelchairs"',
        'title="Wheelchair accessible">',
    ]
)


def get_accessible_icon_html(embedded_svg=False) -> str:
    """
    Return suitable HTML for displaying the "wheelchair access" icon.

    Amtrak data does not show full accessibility.  This is being used for basic
    platform accessibility at this time.
    """
    return accessible_img_str


# Testing code
if __name__ == "__main__":
    pass
