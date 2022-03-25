#! /usr/bin/env python3
# baggage.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Stuff for dealing with checked baggage markings.

Uses actual icon SVG images.
Currently this is not actually used in the main program.  FIXME

It does test that the icon related files are in the right location, though.
"""

import pkgutil

# Unicode has a "baggage claim" symbol :baggage_claim:
# ... but it's not appropriate and not supported by
# the fonts in Weasyprint.  :-(
# U+1F6C4

def baggage_symbol_txt() -> str:
    """
    Return a suitable baggage code for a plaintext timetable.

    At present, this is a capital letter B.
    """
    return "B"

def baggage_symbol_html() -> str:
    """
    Return HTML for a baggage icon, used to indicate checked baggage.
    This is lifted from the icons folder as SVG.
    includes a <span class "baggage-symbol"> to allow additional fiddling for this symbol.
    """
    print("Package in sub: " + str(__package__))
    print("Module in sub: " + baggage_symbol_html.__module__)
    icons_dirname = "./icons/"
    # Main CSS for the actual timetable
    with open(icons_dirname + "suitcase-solid.svg", "r") as suitcase_svg_file:
        suitcase_svg = suitcase_svg_file.read()
    # pkgutil.get_data extracts relative to the current filename, which is great
    # decode() converts from binary string back to UTF-8
    suitcase_svg = pkgutil.get_data(__name__,"icons/baggage-embedded.svg").decode()
    return suitcase_svg

def baggage_symbol_css() -> str:
    print("Module in sub: " + baggage_symbol_html.__module__)
    icons_dirname = "./icons/"
    # Main CSS for the actual timetable
    with open(icons_dirname + "icons.css", "r") as icons_css_file:
        icons_css = icons_css_file.read()
    return icons_css

# Testing code
if __name__ == "__main__":
    print("Package: " + str(__package__))
    # Use of pkgutil.get_data fails on a main program,
    # So we import this module's symbols as a module!
    # Very hacky, but this is just a hacky test.
#    from baggage import *
    print("Package: " + str(__package__))
    print("Baggage symbol in text: ")
    print( baggage_symbol_txt() )
#    print("Baggage HTML: ")
#    print( baggage_symbol_html() )
    print("Baggage CSS: ")
    print( baggage_symbol_css() )
