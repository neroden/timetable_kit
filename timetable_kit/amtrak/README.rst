Amtrak Subpackage
*****************

This contains python modules which are entirely specific to Amtrak.

Before making an Amtrak timetable, you currently need to run the following scripts
within this directory to download the Amtrak station database and the Amtrak GTFS files:

* ./json_stations.py download
* ./json_stations.py process
* python3 ./get_gtfs.py

Right now the timetable_kit package is really only designed to make
Amtrak timetables, but the hope is that the rest of the package can 
be made indepenent of Amtrak, with the Amtrak-specific stuff here.

Amtrak's GTFS file download location is currently hard-coded in the get_gtfs.py file.
If it changes, the new location will probably be published at Transitland (http://www.transit.land/)
and at OpenMobilityData ( https://github.com/MobilityData/mobility-database-catalogs , 
with the actual download location being in the CSV file -- see "download the CSV").

This has several scripts:

* get_gtfs.py -- download Amtrak's GTFS
* json_stations.py -- download and process Amtrak's station database
* station_url.py -- get the URL for the JSON station details for a station
* accessibility_check.py -- make lists of Amtrak's stations with access problems
* station_type.py -- is a station a train station or a bus station?

And several unused scripts:
* agency_cleanup.py
* get_wiki_stations.py -- get Amtrak's station list from Wikipedia -- not used
* wiki_station_cleanup.py -- Clean up data from Wikipedia -- not used

