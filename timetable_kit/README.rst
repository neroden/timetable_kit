What's Here
***********

This is the directory for the actual timetable_kit package.
In python packaging style, this is always a subdirectory of the source control system
root directory (I don't know why, but I'll follow the style.)

timetable.py contains the main program.  It should be executed at the command line.

Note that the system holds and manipulates the entire GTFS database in memory, with substantial overhead, as well as loading many heavyweight python packages.
A quick test found it maxing out at 1.66 gigabytes of virtual memory and 685 megabytes resident on Amtrak's database.  This should be manageable on modern computers.  A GTFS dataset significantly larger than Amtrak's 35MB dataset, however, may cause problems.

Before running it to generate an Amtrak timetable, you will have to download the
Amtrak GTFS file and the Amtrak stations database.  This is done in the amtrak/
folder (see the file amtrak/README.rst in that folder).

You will also need to write a tt-spec: this consists of a CSV file and a JSON file each in a special format.
tt-spec-documentation.rst contains documentation on the tt-spec format and future plans for it.

find_trains.py gets all the trains from one station to another station (one way).
get_station_list.py gets all the stations served by a particular train (in order).
These are intended as utilities for designing your tt-spec files.

NOTES contains various notes on things learned, work in progress, etc.
TODO is my to-do list.

This is an unfinished work in progress.  It has not yet had a release and does not yet
have version numbers.
