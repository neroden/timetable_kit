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

from timetable_kit.load_resources import get_icon_svg, get_icon_css


def get_css_for_all_icons() -> str:
    """
    Get the CSS code to style all the icons we're using.
    """
    full_css = "\n".join(
        [
            get_baggage_icon_css(),
            get_accessible_icon_css(),
            get_inaccessible_icon_css(),
        ]
    )
    return full_css


# Unicode has a "baggage claim" symbol :baggage_claim:
# ... but it's not appropriate and not supported by
# the fonts in Weasyprint.  :-(
# U+1F6C4

baggage_img_str = " ".join(
    [
        "<img",
        'class="baggage-icon-img"',
        'src="icons/baggage-ncn.svg"',
        'alt="Baggage"',
        'title="Checked Baggage">',
    ]
)

baggage_span_str = "".join(
    [
        '<span class="baggage-symbol">',
        baggage_img_str,
        "</span>",
    ]
)


def get_baggage_icon_html(embedded_svg=False) -> str:
    """
    Return suitable HTML for displaying the baggage icon.
    """
    return baggage_span_str
    # TODO: provide the alternate versions.
    if not embedded_svg:
        return baggage_span_str
    if embedded_svg:  # not tested
        str = get_icon_svg("baggage-ncn.svg")
        return str
    return ""


def get_baggage_icon_css():
    """
    Return suitable CSS for the baggage icon (loaded from a file)
    """
    return get_icon_css("baggage-ncn.css")


accessible_img_str = " ".join(
    [
        "<img",
        'class="accessible-icon-img"',
        'src="icons/accessible.svg"',
        'alt="Wheelchair accessible"',
        'title="Wheelchair accessible">',
    ]
)


accessible_span_str = "".join(
    [
        '<span class="accessible-symbol">',
        accessible_img_str,
        "</span>",
    ]
)


def get_accessible_icon_html(embedded_svg=False) -> str:
    """
    Return suitable HTML for displaying the "wheelchair access" icon.

    Amtrak data does not show full accessibility.  This is being used for basic
    platform accessibility at this time.
    """
    return accessible_span_str


def get_accessible_icon_css():
    """
    Return suitable CSS for the wheelchair icon (loaded from a file)
    """
    return get_icon_css("accessible.css")


inaccessible_img_str = " ".join(
    [
        "<img",
        'class="inaccessible-icon-img"',
        'src="icons/inaccessible-ncn.svg"',
        'alt="Inaccessible for wheelchairs"',
        'title="Not wheelchair accessible">',
    ]
)

inaccessible_span_str = "".join(
    [
        '<span class="inaccessible-symbol">',
        inaccessible_img_str,
        "</span>",
    ]
)


def get_inaccessible_icon_html(embedded_svg=False) -> str:
    """
    Return suitable HTML for displaying the "no wheelchair access" icon.
    """
    return inaccessible_span_str


def get_inaccessible_icon_css():
    """
    Return suitable CSS for the no-wheelchair icon (loaded from a file)
    """
    return get_icon_css("inaccessible-ncn.css")
