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

from timetable_kit.load_resources import get_icon_css


def get_filenames_for_all_icons() -> list[str]:
    """
    Determine the list of icon filenames which must be copied
    """
    icon_filenames = [
        "accessible.svg",
        "inaccessible-ncn.svg",
        "baggage-ncn.svg",
        "bus-ncn.svg",
        "bed-solid.svg",
    ]
    return icon_filenames


def get_css_for_all_icons() -> str:
    """
    Get the CSS code to style all the icons we're using.
    """
    full_css = "\n".join(
        [
            get_baggage_icon_css(),
            get_accessible_icon_css(),
            get_inaccessible_icon_css(),
            get_sleeper_icon_css(),
            get_bus_icon_css(),
        ]
    )
    return full_css


# Unicode has a "baggage claim" symbol :baggage_claim:
# ... but it's not appropriate and not supported by
# the fonts in Weasyprint.  :-(
# U+1F6C4

# Use if icon is not available
baggage_letter = "G"

baggage_img_str = " ".join(
    [
        "<img",
        'class="baggage-icon-img"',
        'src="icons/baggage-ncn.svg"',
        'alt="' + baggage_letter + '"',
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


def get_baggage_icon_html(embedded_svg=False, doing_html=True) -> str:
    """
    Return suitable HTML for displaying the baggage icon.

    If doing_html=False, return a suitable capital letter
    """
    if doing_html:
        return baggage_span_str
    else:
        return baggage_letter


def get_baggage_icon_css():
    """
    Return suitable CSS for the baggage icon (loaded from a file)
    """
    return get_icon_css("baggage-ncn.css")


# Use if icon is not available
accessible_letter = "W"

accessible_img_str = " ".join(
    [
        "<img",
        'class="accessible-icon-img"',
        'src="icons/accessible.svg"',
        'alt="' + accessible_letter + '"',
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


def get_accessible_icon_html(doing_html=True) -> str:
    """
    Return suitable HTML for displaying the "wheelchair access" icon.

    Amtrak's data does not show full accessibility.  This is being used for basic
    platform accessibility at this time.
    """
    if doing_html:
        return accessible_span_str
    else:
        return accessible_letter


def get_accessible_icon_css():
    """
    Return suitable CSS for the wheelchair icon (loaded from a file)
    """
    return get_icon_css("accessible.css")


# Use if icon is not available
inaccessible_letter = "N"

inaccessible_img_str = " ".join(
    [
        "<img",
        'class="inaccessible-icon-img"',
        'src="icons/inaccessible-ncn.svg"',
        'alt="' + inaccessible_letter + '"',
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


def get_inaccessible_icon_html(doing_html=True) -> str:
    """
    Return suitable HTML for displaying the "no wheelchair access" icon.
    """
    if doing_html:
        return inaccessible_span_str
    else:
        return inaccessible_letter


def get_inaccessible_icon_css():
    """
    Return suitable CSS for the no-wheelchair icon (loaded from a file)
    """
    return get_icon_css("inaccessible-ncn.css")


# Use if icon is not available
bus_letter = "B"

bus_img_str = " ".join(
    [
        "<img",
        'class="bus-icon-img"',
        'src="icons/bus-ncn.svg"',
        'alt="' + bus_letter + '"',
        'title="Bus">',
    ]
)

bus_span_str = "".join(
    [
        '<span class="bus-symbol">',
        bus_img_str,
        "</span>",
    ]
)


def get_bus_icon_html(doing_html=True) -> str:
    """
    Return suitable HTML for displaying the bus icon.
    """
    if doing_html:
        return bus_span_str
    else:
        return bus_letter


def get_bus_icon_css():
    """
    Return suitable CSS for the no-wheelchair icon (loaded from a file)
    """
    return get_icon_css("bus-ncn.css")


# Use if icon is not available
sleeper_letter = "S"

sleeper_img_str = " ".join(
    [
        "<img",
        'class="sleeper-icon-img"',
        'src="icons/bed-solid.svg"',
        'alt="Sleeper"',
        'title="Sleeping Car Service">',
    ]
)

sleeper_span_str = "".join(
    [
        '<span class="sleeper-symbol">',
        sleeper_img_str,
        "</span>",
    ]
)


def get_sleeper_icon_html(doing_html=True) -> str:
    """
    Return suitable HTML for displaying the sleeper icon.
    """
    if doing_html:
        return sleeper_span_str
    else:
        return sleeper_letter


def get_sleeper_icon_css():
    """
    Return suitable CSS for the sleeper icon (loaded from a file)
    """
    return get_icon_css("bed-solid.css")
