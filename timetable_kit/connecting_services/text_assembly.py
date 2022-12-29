#! /usr/bin/env python3
# connecting_services/text_assembly.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3>

"""
This module assembles suitable HTML or text strings for connecting agencies.
"""

# This contains the actual data
from timetable_kit.connecting_services.catalog import connecting_agencies_dict

# This is a string for str.format()
# This references elements of the dict for the service.
# This one is for the actual image:
_template_img_str = " ".join(
    [
        "<img",
        'class="{class}"',
        'src="logos/{svg_filename}"',
        'alt="{alt}"',
        'title="{title}">',
    ]
)

# Wrap the logo in a link:
_template_anchor_str = "".join(
    [
        '<a href="{url}">',
        _template_img_str,
        "</a>",
    ]
)

# This is the span for the image used in a cell:
_template_span_str = "".join(
    [
        '<span class="connecting-service-span">',
        _template_anchor_str,
        "</span>",
    ]
)

# This is the key:
_template_key_str = "".join([_template_anchor_str, ': <a href="{url}">{full_name}</a>'])

# For text-only timetables
_template_text_str = "{alt}"
# For text-only timetables
_template_key_text_str = "{alt}: {full_name}"


def get_connecting_agency_icon_html(connecting_agency, doing_html=True):
    """
    Return suitable HTML for the connecting agency's icon.
    """
    # Fish out the data for the correct agency
    agency_dict = connecting_agencies_dict[connecting_agency]
    # Fill the template in from the agency_dict data
    if doing_html:
        return _template_span_str.format(**agency_dict)
    else:
        return _template_text_str.format(**agency_dict)


def get_connecting_agency_key_html(connecting_agency, doing_html=True):
    """
    Return suitable HTML for a key for the connecting agency.
    """
    # Fish out the data for the correct agency
    agency_dict = connecting_agencies_dict[connecting_agency]
    if doing_html:
        return _template_key_str.format(**agency_dict)
    else:
        return _template_key_text_str.format(**agency_dict)


### TESTING CODE ###
if __name__ == "__main__":
    print("Testing plaintext:")
    print(get_connecting_agency_icon_html("marc", doing_html=False))
    print(get_connecting_agency_icon_html("baltimore_lrt", doing_html=False))
    print("Testing HTML:")
    print(get_connecting_agency_icon_html("marc"))
    print(get_connecting_agency_icon_html("baltimore_lrt"))
    print("Testing key:")
    print(get_connecting_agency_key_html("marc"))
    print(get_connecting_agency_key_html("baltimore_lrt"))
