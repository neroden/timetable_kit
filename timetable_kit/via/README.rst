VIA Rail subpackage
-------------------

Successfully making VIA timetables.

Note that WE DO NOT READ calendar_dates.txt.  VIA uses this to suspend services.  You MUST check it manually.

The best source of VIA station codes is https://cptdb.ca/wiki/index.php/VIA_Rail_Canada_stations
MTRL = Montreal
TRTO = Toronto

First, remember to download the GTFS data for VIA::

    python ./via/get_gtfs.py

When you want Via stuff you need to specify the agency to be "via", for example::

    python ./list_trains.py --agency via HLFX MTRL

When generating a timetable you also need to specify an author::

    python ./timetable.py --agency via -i specs_via ocean --author NAME


Work in progress.