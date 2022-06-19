Hartford Line Specs
===================

This directory contains specs for combined Amtrak Hartford Line / CTrail Hartford Line timetables.

These require merging the GTFS, by running

* amtrak/get_gtfs.py
* hartford_line/get_gtfs.py
* hartford_line/merge_gtfs.py

Then they require invoking the timetable generator in a way similar to this:

* ../timetable.py -i . --gtfs ../hartford_line/merged-gtfs.zip --specs *.json

Sorry about the complexity.
