#! /usr/bin/env python3
# baggage.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Stuff for dealing with checked baggage markings.

Uses the Unicode "checked baggage" symbol.
"""

# Unicode has a "baggage claim" symbol :baggage_claim:
# U+1F6C4
# HTML decimal: &#128708
# HTML hex:  	&#x1f6c4

def baggage_symbol_txt() -> str:
    """
    Return Unicode for the baggage claim symbol, used to indicate checked baggage
    """
    return "\U0001F6C4"

def baggage_symbol_html() -> str:
    """
    Return HTML for the baggage claim symbol, used to indicate checked baggage:
    includes a <span class "baggage-symbol"> to allow font changes for just this symbol
    """
    return '<span class="baggage-symbol">&#x1f6c4;</span>'

# Testing code
if __name__ == "__main__":
    print("Baggage symbol: " + baggage_symbol_txt() + ".")
    print("Baggage HTML: " + baggage_symbol_html() + ".")
