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
fragment_loader -- looks in "fragments" folder
fonts_loader -- looks in "fonts" folder

Two matching jinja2 environments are available:
template_environment
fragment_environment
fonts_environment

These functions are provided:
get_fragment(filename: str) -> str
get_font_css(fontname: str) -> str
"""

import jinja2
from jinja2 import (
    Environment,
    ChoiceLoader,
    FileSystemLoader,
    PackageLoader,
    )

# Here are the loaders and environments
template_loader = ChoiceLoader([
    FileSystemLoader(['.', "templates"]),
    PackageLoader("load_resources", package_path="templates"),
    ])
template_environment = Environment(
    loader = template_loader,
    autoescape = lambda x: False,
    )

fragment_loader = ChoiceLoader([
    FileSystemLoader(['.', "fragments"]),
    PackageLoader("load_resources", package_path="fragments"),
    ])
fragment_environment = Environment(
    loader = fragment_loader,
    autoescape = lambda x: False,
    )

font_loader = ChoiceLoader([
    FileSystemLoader(['.', "fonts"]),
    PackageLoader("load_resources", package_path="fonts"),
    ])
font_environment = Environment(
    loader = font_loader,
    autoescape = lambda x: False,
    )

icon_loader = ChoiceLoader([
    FileSystemLoader(['.', "icons"]),
    PackageLoader("load_resources", package_path="icons"),
    ])
icon_environment = Environment(
    loader = icon_loader,
    autoescape = lambda x: False,
    )

"""
Load a fragment file and return it as a string.

This uses Jinja2, fragment_loader, and fragment_environment.
"""
def get_fragment(filename: str) -> str:
    (fragment_str, returned_filename, uptodate) = (
        fragment_loader.get_source(fragment_environment, filename)
        )
    return fragment_str

"""
Load a font CSS file (the ".css" will be appended -- don't include it) and return it as a string.

This uses Jinja2, font_loader, and font_environment.
"""
def get_font_css(fontname: str) -> str:
    (font_css_str, returned_filename, uptodate) = (
        font_loader.get_source(font_environment, fontname + ".css")
        )
    return font_css_str

"""
Load an icon CSS file (specify full filename including .css) and return it as a string.

This uses Jinja2, icon_loader, and icon_environment.
"""
def get_icon_css(filename: str) -> str:
    (icon_css_str, returned_filename, uptodate) = (
        icon_loader.get_source(icon_environment, filename)
        )
    return icon_css_str


# TESTING
if __name__ == "__main__":
    page_tpl = template_environment.get_template("page_standard.html")

    page_fragment = get_fragment("page.css")
    print( "The page.css fragment is:" )
    print( page_fragment )

    page_tpl_params = {
        'lang' : "en-US",
        'encoding' : "utf-8",
        'title' : "Test Title",
        'heading' : "Test Heading",
        'timetable' : "<p>No timetable</p>",
        'symbol_key' : "<p>No Symbol Key</p>",
        'external_stylesheet' : "foobar.css",
        }
    rendered_page = page_tpl.render(page_tpl_params)
    with open("test_results_1.html", "w") as outfile:
        print(rendered_page, file=outfile)

    page_tpl_params = {
        'lang' : "en-US",
        'encoding' : "utf-8",
        'title' : "Test Title",
        'heading' : "Test Heading",
        'timetable' : "<p>No timetable</p>",
        'symbol_key' : "<p>No Symbol Key</p>",
        'internal_stylesheet' : True,
        }
    rendered_page = page_tpl.render(page_tpl_params)
    with open("test_results_2.html", "w") as outfile:
        print(rendered_page, file=outfile)
    print("Done.")
