What's Here
***********

This is the directory for the actual timetable_kit package.
In python packaging style, this is always a subdirectory of the source control system
root directory (I don't know why, but I'll follow the style.)

timetable.py contains the main program.  It should be executed at the command line.

Note that the system holds and manipulates the entire GTFS database in memory, with substantial overhead, as well as loading many heavyweight python packages.
A quick test found it maxing out at 1.21 gigabytes of virtual memory and 247 megabytes resident on Amtrak's database.  This should be manageable on modern computers.  However, a GTFS dataset significantly larger than Amtrak's dataset may cause problems.  Amtrak's dataset is 110MB uncompressed, but most of that is the shapes.txt file which we ignore.  Amtrak's stop_times.txt file is only 1.2M.  It may be quite slow on a much larger dataset.

However, timetable_kit's fundamental strategy is to filter the dataset to only the relevant data first, then make the timetable.  So it should be amenable to swapping once the filtering stage is done.  The filtering stage may be a heavy memory user on a large dataset, however.  If you have a huge dataset, it may be advisable to filter it for the relevant routes and feed a smaller dataset into this program.

Before runnning it to generate any timetable, you will have to download the relevant GTFS for the agency.  This is now automated for some agencies with:
* ./timetable.py --agency amtrak --get-gtfs

Before running it to generate an Amtrak timetable, you will have to download the Amtrak stations database.  This is done in the amtrak/
folder (see the file amtrak/README.rst in that folder).

If you don't already have one, you will also need to write a tt-spec: this consists of a CSV file and a TOML (aux) file each in a special format.
tt-spec-documentation.rst contains documentation on the tt-spec format and future plans for it.

* list_trains.py gets all the trains from one station to another station (one way).
* list_stations.py gets all the stations served by a particular train (in order).
* make_spec.py > output.csv can be used to make a prototype tt-spec CSV file, but it *will* need to be edited by hand in a spreadsheet.
* compare.py can be used to check services on different dates for changes.
These are intended as utilities for designing your tt-spec files.

If you want to add additional templates, icons, or fonts, put them in ~/.local/share/timetable_kit/[templates, icons, fonts]



NOTES contains various notes on things learned, work in progress, etc.
TODO is my to-do list.
PHILOSOPHY.rst contains an explanation of the underlying design philosophy of the program.  If you're submitting patches, they should correspond to this philosophy.

This is an unfinished work in progress.
It has not yet had a release and does not yet have version numbers.
