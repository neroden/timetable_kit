Maple Leaf
==========

The Amtrak/VIA joint Maple Leaf has a history of data quality issues.  Sometimes VIA has out-of-date information for the American stations; sometimes Amtrak has out-of-date-information for the Canadian stations.  In July 2023, *both* were true and *neither* agency had an accurate timetable in their ticketing system.

Accordingly, we attempt to make a Franken-feed out of the Via and GTFS feeds which can be used to make a reliable timetable, with Amtrak data for the American stations and VIA data for the Canadian stations.

In order to actually get and merge the feeds, the user has to run the following:

* amtrak/get_gtfs.py
* via/get_gtfs.py
* maple_leaf/merge_gtfs.py

This will generate a partially merged feed usable ONLY for making Maple Leaf timetables.

The merged file ends up in maple_leaf/gtfs.

Then run

* ./timetable.py --agency maple_leaf maple-leaf

to get a timetable.
