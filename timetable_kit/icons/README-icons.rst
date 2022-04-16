README-icons.rst
================
Part of timetable_kit
Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

This folder contains icons used for timetable display.

Each icon in use has a matching CSS file so it'll line up properly in font context.
I may want to merge these into SpartanTT font at some point if I can find the right Unicode
code points to put them out.

Baggage icons:
==============

suitcase-solid.svg
------------------
The "suitcase-solid" SVG image is from Font Awesome Free.
In SVG form, it is subject to the CC BY 4.0 license, which requires only attribution.

"suitcase-solid-inline.svg": In order to use it in inline form, I edited it to "suitcase-solid-inline.svg".
(This is currently not used because Weasyprint can't handle inline SVGs with references.)
Inline SVG with reference is done by defining a "symbol".
The inline SVG has to have alt-text foro screen readers;
this is done by adding a "title" field as the first child of the SVG.

This is retained as a sample for future conversion to inline SVGs.

baggage_ncn.svg
---------------
I wasn't happy with either of these, so I went to a lot of effort to make a "hollow briefcase" of my own.
This is on a 512x512 grid like the FontAwesome briefcase, but is a different shape and size,
optimized for very small font sizes.

This version, which is also simplified and cleaned up, is in baggage_ncn.svg.
This one WORKS at very small print sizes.

Accessibility Icons
===================

accessible.svg
--------------
The accessibility icons were a pain too.  The one I finally used for accessible.svg
is from https://commons.wikimedia.org/wiki/File:Wheelchair_symbol.svg and is in the public
domain.  I copied this to accessible.svg.

The more modern "racing" symbol, also in public domain, is unrecognizable in small print.

I would prefer the "round-edged variant" of the wheelchair symbol as I think it will display
better in small print but I can't find one in SVG at this time.  

inaccessible-ncn.svg
--------------------
I decided I needed an inaccessible symbol because fully-inaccessible stations are rarer than
accessible stations and need to stand out visually; a blank space doesn't stand out.

I made this myself in Inkscape based on accessible.svg.  I place it in the public domain.
Other people's variants of this unreadable at small print.  However, I used
https://commons.wikimedia.org/wiki/File:No_Accessibility_-_Original_Handicapped_Symbol.svg
(also public domain) to find the correct color to use for the slash.

This color still looks right in greyscale, which is important.

Bed Icon
========

bed-solid.svg
-------------
The "bed-solid" SVG image is from Font Awesome Free.
In SVG form, it is subject to the CC BY 4.0 license, which requires only attribution.

rpa-logo.svg and rpa-logo-orig.svg
==================================
This is the Rail Passengers Association logo; it is copyrighted and trademarked to them,
and should only be used for things authorized by them.  Don't use it without authorization.

It's here because I had to do internal technical modifications to make it print.
Specifically, I had to eliminate the masks, which Weasyprint can't process.
