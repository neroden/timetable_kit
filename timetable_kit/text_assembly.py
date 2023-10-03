# text_assembly.py
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Module for assembling small bits of text, mostly for disclaimers.

Contains bits which don't require tsns, but which are loaded early,
to avoid circular dependencies.

"""

import html  # for html.escape


def href_wrap(text: str, url: str, doing_html: bool = True) -> str:
    """
    Given text and a URL, wrap the text in an HREF anchor pointing to the URL.

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
    """
    Given a list of pieces of text, returns a new list of pieces of text,
    with the appropriate words added to make it an "and" clause if spaces are put
    in between.

    With an empty list, returns an empty list.  The odd interface is designed
    to make this work correctly if run through " ".join()
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
    """
    Given a list of pieces of text, returns a new list of pieces of text,
    with the appropriate words added to make it an "or" clause if spaces are put
    in between.

    With an empty list, returns an empty list.  The odd interface is designed
    to make this work correctly if run through " ".join()
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
