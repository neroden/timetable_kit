VIA Rail subpackage
-------------------

Successfully making VIA timetables.

Note that WE DO NOT READ calendar_dates.txt.  VIA uses this to suspend services.  You MUST check it manually.

The best source of VIA station codes is https://cptdb.ca/wiki/index.php/VIA_Rail_Canada_stations
MTRL = Montreal
TRTO = Toronto

You need to specify the agency.::
    ./timetable.py --agency via
    ./list_trains.py --agency via HLFX TRTO

This works::

  * timetable.py --agency via --get-gtfs
  * timetable.py --agency via ocean
