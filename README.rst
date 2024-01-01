Timetable Kit
*************

Timetable Kit (timetable_kit) is a Python toolkit for generating human-readable timetables from `General Transit Feed Specification (GTFS) <https://en.wikipedia.org/wiki/GTFS>` data.

The user provides a "prototype" timetable in CSV form (with stations/stops along the left column and train numbers/trip numbers along the top row), along with a TOML file specifying options.  Then timetable_kit fills in the times and other info (from GTFS) and produces either HTML & CSS, PDF, or a plaintext CSV file.

Development status
==================
Timetable_kit remains under active development.
It is quite usable to create Amtrak timetables and VIA Rail Canada timetables.

It has not yet been generalized to create timetables in general.

Interfaces are moderately stable.  New options continue to be added in spec files.
Command line options remain in a state of flux.
The interface will change as needs are discovered while creating particular timetables.

Directory Structure
===================
In keeping with the universal, if bizarre, Python package source directory structure,
the entire package is in a subdirectory called timetable_kit.

The only exceptions are HOWTO, certain build files, this file, and LICENSE.

In particular, data resources and documentation are largely inside the package directory at
this time.  This may change.

Dependencies
============
Timetable Kit requires Python 3.11, because it uses "Self."
Even if you removed those, it requires Python 3.10, because it uses the match/case statement,
and it uses it very, very intensively.

It relies on `GTFS Kit <https://github.com/mrcagney/gtfs_kit>` to parse GTFS.

Like GTFS Kit, it uses `PANDAS <https://pandas.pydata.org>` to do the heavy lifting.
It was most recently tested with PANDAS 2.1.4.

Timetable Kit also requires the jinja2 package.  Jinja2 templates are used extensively.

It uses Weasyprint to convert HTML timetables to PDF timetables.

It uses tomlkit to read & write the TOML files.

It uses xdg-base-dirs to find out where to store its data.

One of the tools uses the LXML module to parse Amtrak's station web pages.

It's packaged as a package with Poetry, so presumably requires Poetry to install.


Further Documentation
=====================
Look in the HOWTO file for information on setting this up as an editable module.
Look in the timetable_kit folder for the README.rst there for further info on using the program.

Authors
=======
Copyright 2021, 2022, 2023 Nathanael Nerode.

SpartanTT Copyright 2023 Matt Bailey, Mirko Velimirovic, Nathanael Nerode.

Some fonts, icons, and logos are from other sources and have their own authors, copyrights,
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

The font SpartanTT is licensed under the Open Font License 1.1.
See fonts/OFL.txt for more information.
https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL

Some fonts and icons are from other sources and have their own copyrights and licenses.
They are all free, libre, and open-source.  See their subdirectories for more information.

Connecting service logos in the timetable_kit/connecting_services/logos directory may be subject to other copyrights
and some might not be free, libre, or open-source.  They are mostly trademarks, used strictly to refer to the appropriate transit service or agency,
which is legal to do without asking permission under trademark law.  They can be disabled (replaced with alternate text references)
by removing the reference to the logo file in the connecting_services/connecting_services.csv file.


Examples
=========

This are some (probably out of date) timetables made using timetable_kit.

.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/maple-leaf.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/vermont-to-upstate-ny.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/empire-builder.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/michigan-services.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/ocean.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/richmond-weekday-nb.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/jasper-prince-rupert.jpg
.. image:: https://github.com/neroden/timetable_kit/raw/main/samples/canadian.jpg
