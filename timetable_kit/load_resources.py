#! /usr/bin/env python3
# load_resources.py
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Load resources, mostly jinja2 templates

This module has helpers for loading jinja2 templates.

It is also used to find and load other resources,
abusing the jinja2 loader system since it's better than
any other systems I've seen.

Resources are loaded so that the user can override them.
Current scheme:
Priority 1 location -- current directory
Priority 2 location -- suitable subdirectory of current
Priority 3 location -- suitable subdirectory associated with THIS module

Several loaders are provided:
template_loader -- looks in "templates" folder
font_loader -- looks in "fonts" folder
icon_loader -- looks in "icons" folder
logo_loader -- looks in "logos" folder, or in connecting_services/logos
connecting_services_csv_loader -- looks in "connecting_services"

Matching jinja2 environments are available:
template_environment
font_environment
icon_environment
logo_environment
connecting_services_csv_environment

These functions are provided:
get_font_css(fontname: str) -> str
get_icon_css(filename: str) -> str
get_icon_svg(filename: str) -> str
get_logo_css(filename: str) -> str
get_logo_svg(filename: str) -> str
get_connecting_services_csv(filename: str) -> str
"""

from jinja2 import (
    Environment,
    ChoiceLoader,
    FileSystemLoader,
    PackageLoader,
)

# Here are the loaders and environments
# Note that the PackageLoader is grabbing the parent package
# of load_resources, which is undocumented behavior (FIXME)
# but works
template_loader = ChoiceLoader(
    [
        FileSystemLoader([".", "templates"]),
        PackageLoader("timetable_kit.load_resources", package_path="templates"),
    ]
)
template_environment = Environment(
    loader=template_loader,
    autoescape=lambda x: False,
)

font_loader = ChoiceLoader(
    [
        FileSystemLoader([".", "fonts"]),
        PackageLoader("timetable_kit.load_resources", package_path="fonts"),
    ]
)
font_environment = Environment(
    loader=font_loader,
    autoescape=lambda x: False,
)

icon_loader = ChoiceLoader(
    [
        FileSystemLoader([".", "icons"]),
        PackageLoader("timetable_kit.load_resources", package_path="icons"),
    ]
)
icon_environment = Environment(
    loader=icon_loader,
    autoescape=lambda x: False,
)

logo_loader = ChoiceLoader(
    [
        #        FileSystemLoader([".", "logos"]),
        PackageLoader(
            "timetable_kit.load_resources", package_path="connecting_services/logos"
        ),
    ]
)
logo_environment = Environment(
    loader=logo_loader,
    autoescape=lambda x: False,
)

connecting_services_csv_loader = ChoiceLoader(
    [
        #        FileSystemLoader(["."]),
        PackageLoader(
            "timetable_kit.load_resources", package_path="connecting_services"
        ),
    ]
)
connecting_services_csv_environment = Environment(
    loader=connecting_services_csv_loader,
    autoescape=lambda x: False,
)


def get_font_css(fontname: str) -> str:
    """
    Load a font CSS file (the ".css" will be appended -- don't include it) and return it as a string.

    This uses Jinja2, font_loader, and font_environment.
    """
    (font_css_str, returned_filename, uptodate) = font_loader.get_source(
        font_environment, fontname + ".css"
    )
    return font_css_str


def get_icon_css(filename: str) -> str:
    """
    Load an icon CSS file (specify full filename including .css) and return it as a string.

    This uses Jinja2, icon_loader, and icon_environment.
    """
    (icon_css_str, returned_filename, uptodate) = icon_loader.get_source(
        icon_environment, filename
    )
    return icon_css_str


def get_icon_svg(filename: str) -> str:
    """
    Load an icon SVG file (specify full filename including .svg) and return it as a string.

    This uses Jinja2, icon_loader, and icon_environment.
    Technically this is the same code as get_icon_css right now.
    """
    (icon_svg_str, returned_filename, uptodate) = icon_loader.get_source(
        icon_environment, filename
    )
    return icon_svg_str


def get_logo_css(filename: str) -> str:
    """
    Load a logo CSS file (specify full filename including .css) and return it as a string.

    This uses Jinja2, logo_loader, and logo_environment.
    """
    (logo_css_str, returned_filename, uptodate) = logo_loader.get_source(
        logo_environment, filename
    )
    return logo_css_str


def get_logo_svg(filename: str) -> str:
    """
    Load a logo SVG file (specify full filename including .svg) and return it as a string.

    This uses Jinja2, logo_loader, and logo_environment.
    Technically this is the same code as get_logo_css right now.
    """
    (logo_svg_str, returned_filename, uptodate) = logo_loader.get_source(
        logo_environment, filename
    )
    return logo_svg_str


def get_connecting_services_csv(filename: str) -> str:
    """
    Load a file (specify full filename) from the connecting_services subpackage and return it as a string.
    This uses Jinja2, logo_loader, and logo_environment.
    """
    (
        connecting_services_csv_str,
        returned_filename,
        uptodate,
    ) = connecting_services_csv_loader.get_source(
        connecting_services_csv_environment, filename
    )
    return connecting_services_csv_str


# TESTING
if __name__ == "__main__":
    page_tpl = template_environment.get_template("page_standard.html")

    page_tpl_params = {
        "lang": "en-US",
        "encoding": "utf-8",
        "title": "Test Title",
        "heading": "Test Heading",
        "timetable": "<p>No timetable</p>",
        "symbol_key": "<p>No Symbol Key</p>",
        "external_stylesheet": "foobar.css",
    }
    rendered_page = page_tpl.render(page_tpl_params)
    with open("test_results_1.html", "w") as outfile:
        print(rendered_page, file=outfile)

    page_tpl_params = {
        "lang": "en-US",
        "encoding": "utf-8",
        "title": "Test Title",
        "heading": "Test Heading",
        "timetable": "<p>No timetable</p>",
        "symbol_key": "<p>No Symbol Key</p>",
        "internal_stylesheet": "Yes",  # MyPy wants a str here; we just need truthy
    }
    rendered_page = page_tpl.render(page_tpl_params)
    with open("test_results_2.html", "w") as outfile:
        print(rendered_page, file=outfile)
    print("Done.")
