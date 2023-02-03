VIA Rail subpackage
-------------------

Successfully making VIA timetables.

Best source of VIA station codes is https://cptdb.ca/wiki/index.php/VIA_Rail_Canada_stations
MTRL = Montreal
TRTO = Toronto

You need to specify the agency.::
    ./timetable.py --agency via
    ./list_trains.py --agency via HLFX TRTO

Work in progress.

Try this::

  timetable.py --agency via -i specs_via ocean
