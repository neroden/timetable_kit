Hartford Line Specs
===================

This directory contains specs for combined Amtrak Hartford Line / CTrail Hartford Line timetables.

These require getting and merging the GTFS, by running

* ../timetable.py --agency hartford --get-gtfs

Then they require invoking the timetable generator in a way similar to this:

* ../timetable.py --agency hartford hartford-line-valley-flyer.list
