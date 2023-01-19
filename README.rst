Timetable Kit
*************

Timetable Kit (timetable_kit) is a Python toolkit for generating human-readable timetables from `General Transit Feed Specification (GTFS) <https://en.wikipedia.org/wiki/GTFS>` data.

Development status
==================
Timetable_kit remains under active development.
It is quite usable to create Amtrak timetables and VIA Rail Canada timetables, though there remain some issues with VIA timetable generation.

It has not yet been generalized to create timetables in general.

Interfaces are moderately stable: old spec files should continue to work, mostly.
New options continue to be added in spec files.
Command line options remain in a state of flux.
The interface will change as needs are discovered while creating particular timetables.

Directory Structure
===================
In keeping with the universal, if bizarre, Python package source directory structure,
the entire package is in a subdirectory called timetable_kit.

The only exceptions are HOWTO, certain build files, this file, and LICENSE.

In particular, data resources and documentation are all inside the package directory at
this time.  This may change.

Dependencies
============
Timetable Kit requires Python 3.10, because it uses the match/case statement.

It relies on `GTFS Kit <https://github.com/mrcagney/gtfs_kit>` to parse GTFS.

Like GTFS Kit, it uses `PANDAS <https://pandas.pydata.org>` to do the heavy lifting.
It was tested with PANDAS 1.4.

Timetable Kit also requires the jinja2 package.  PANDAS depends on jinja2, but also
timetable_kit uses the Jinja2 template system directly.

It uses Weasyprint to convert HTML timetables to PDF timetables.

It's packaged as a package with Poetry, so presumably requires Poetry to install.

One of the tools uses the LXML module to parse Amtrak's station web pages.

It uses pdftk-java (command-line tool must be installed and in path) to sew single-page PDF timetables together into multi-page timetables.
You don't need pdftk-java unless you want to make multi-page PDFs.  You can also sew the pages together yourself
using your preferred tool.

It uses VIPS (libvips) (command-line tool must be installed and in path) so convert single-page PDF timetables to JPG.
You don't need vips unless you want to make JPG output.  You can also do this conversion yourself using your
preferred tool.


Further Documentation
=====================
Look in the HOWTO file for information on setting this up as an editable module.
Look in the timetable_kit folder for the README.rst there for further info on using the program.

Authors
=======
Copyright 2021, 2022, 2023 Nathanael Nerode.

Some fonts and icons are from other sources and have their own authors, copyrights,
and licenses, noted in their directories or files.

Licenses
========
The timetable_kit software is licensed under GNU Affero GPL v.3 or later.
A copy of this is in the LICENSE file.

Produced timetables might contain some copyrightable material from timetable_kit.

Any copyrighted material from timetable_kit which appears in generated timetables and
stylesheets is addtionally licensed under the 
Creative Commons Attribution 4.0 International License.
To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/
or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

Some fonts and icons are from other sources and have their own copyrights and licenses.
They are all free, libre, and open-source.  See their subdirectories for more information.

The Spartan font is copyright Matt Bailey and Mirko Velimirovic.
It is licensed under the the Open Font License.  See fonts/Spartan and fonts/Spartan/OFL.txt
for more information.

The SpartanTT font is a derivative of the Spartan font specifically for timetables.
It has extremely small, entirely functional changes which are probably uncopyrightable.
It is also under the Open Font License.  See README.Spartan for more information on the changes.

Examples
=========

This are some (probably out of date) timetables made using timetable_kit.

.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/richmond-weekday-nb.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/jasper-prince-rupert.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/upstate-ny-to-western-vermont-services.jpg
