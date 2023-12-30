Maple Leaf
==========

The Amtrak/VIA joint Maple Leaf has a history of data quality issues.  Sometimes VIA has out-of-date information for the American stations; sometimes Amtrak has out-of-date-information for the Canadian stations.  In July 2023, *both* were true and *neither* agency had an accurate timetable in their ticketing system.

Accordingly, we attempt to make a Franken-feed out of the Via and GTFS feeds which can be used to make a reliable timetable, with Amtrak data for the American stations and VIA data for the Canadian stations.

This is now done automatically by

* ./timetable.py --agency maple_leaf --get-gtfs

This will generate a partially merged feed usable ONLY for making Maple Leaf timetables.

Then run

* ./timetable.py --agency maple_leaf maple-leaf

to get a timetable.

Note: use the Amtrak station codes, not the VIA station codes, in the spec file.
