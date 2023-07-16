Hartford Line
=============

The Hartford Line schedule supplements Amtrak schedules.  To make a joint timetable, we need to merge the feeds.  This subpackage handles stuff related to that.

In order to actually get and merge the feeds, the user has to run the following:

* amtrak/get_gtfs.py
* hartford_line/get_gtfs.py
* hartford_line/merge_gtfs.py

The Hartford Line GTFS is downloaded to hartford_line/gtfs_raw

The merged GTFS is at hartford_line/gtfs
