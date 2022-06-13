Timetable Kit
*************

Timetable Kit (timetable_kit) is a Python toolkit for generating human-readable timetables from `General Transit Feed Specification (GTFS) <https://en.wikipedia.org/wiki/GTFS>` data.

For a sample of the sort of timetable you can make with it, see the files in https://github.com/neroden/timetable_kit/tree/main/samples/

Development status
==================
This is currently a work in progress but is quite usable to create Amtrak timetables.
It has not yet been generalized to create non-Amtrak timetables.
Interfaces remain in a state of flux as needs are discovered while creating particular timetables.

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

Further Documentation
=====================
Look in the HOWTO file for information on setting this up as an editable module.
Look in the timetable_kit folder for the README.rst there for further info on using the program.

Authors
=======
Copyright 2021, 2022 Nathanael Nerode.

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

Sample
======

.. image:: https://github.com/neroden/timetable_kit/tree/main/samples/upstate-ny-to-western-vermont-services.jpg
