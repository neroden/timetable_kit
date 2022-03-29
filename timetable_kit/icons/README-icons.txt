README-icons.txt
Part of timetable_kit
Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

This folder contains icons used for timetable display.

----
The "suitcase-solid" SVG image is from Font Awesome Free.
In SVG form, it is subject to the CC BY 4.0 license, which requires only attribution.

"suitcase-solid-inline.svg": In order to use it in inline form, I edited it to "suitcase-solid-inline.svg".
(This is currently not used because Weasyprint can't handle inline SVGs with references.)
Inline SVG with reference is done by defining a "symbol".
The inline SVG has to have alt-text foro screen readers;
this is done by adding a "title" field as the first child of the SVG.

This is retained as a sample for future conversion to inline SVGs.

----

The "source_icons_large-suitcase.svg" image is from iconoir.com.  It is subject to the MIT license.
"large-suitcase-fixed.svg": Cleaned up the metadata.
This doesn't look as nice as the solid briefcase in tiny mode.

----
I wasn't happy with either of these, so I went to a lot of effort to make a "hollow briefcase" of my own.
This is on a 512x512 grid like the FontAwesome briefcase, but is a different shape and size,
optimized for very small font sizes.

This version, which is also simplified and cleaned up, is in baggage_ncn.svg.
This one WORKS at very small print sizes.
----

The accessibility icons were a pain too.  The one I finally used for accessible.svg
is from https://commons.wikimedia.org/wiki/File:Wheelchair_symbol.svg and is in the public
domain.  I copied this to accessible.svg.

The more modern "racing" symbol is unrecognizable in small print.
I would prefer the "round-edged variant" of the wheelchair symbol as I think it will display
better in small print but I can't find one in SVG at this time.

I want a "Non-accessible" symbol because non-accessible stations are rarer than accessible
ones at this point, but I haven't found one which is readable at small print yet.
I will probably have to make my own.

--Nathanael
