Amtrak Subpackage
*****************

This contains python modules which are entirely specific to Amtrak.

Before making an Amtrak timetable, you currently need to run the following scripts
within this directory to download the Amtrak station database and the Amtrak GTFS files:

python3 ./json_stations.py download
python3 ./get_gtfs.py

Right now the timetable_kit package is really only designed to make
Amtrak timetables, but the hope is that the rest of the package can 
be made indepenent of Amtrak, with the Amtrak-specific stuff here.

This has several scripts:

* get_gtfs.py -- download Amtrak's GTFS
* json_stations.py -- download and process Amtrak's station database
* station_url.py -- get the URL for the JSON station details for a station
* accessibility_check.py -- make lists of Amtrak's stations with access problems
* get_wiki_stations.py -- get Amtrak's station list from Wikipedia -- needs lxml installed
    This is used by the accessibility_check.py
* wiki_station_cleanup.py -- Clean up data from Wikipedia

