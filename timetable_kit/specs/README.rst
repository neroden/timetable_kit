This directory contains spec files for Amtrak.

The naming format for long-distance trains uses the full name of the train route or routes involved, except as follows:

* The word "service" is always omitted
* For separate winter and summer schedules, "winter" and "summer" are suffixed
* Where a schedule is changing in the near future, "future" is suffixed

The naming format for regional timetables with many services varies:

* If the service has a name, like "Empire Service" or "Silver Service", this is used without the word "service"
* If it doesn't, a state or regional name is used like "Virginia" or "Carolinas"
* Where there are separate east and west or north and south timetables, "e", "w", "n", "s" are suffixed
* Where multiple pages are necessary, a number like "1" is suffixed

For connecting buses and similar services, all should have "cxn" in the spec name:

* The primary service which it connects to is abbreviated with an acronym, followed by "cxn", followed by a name for the bus service.
* The acronyms for long-distance trains are CS, EB, CZ, SWC, SL, TE, CONO, LSL, CL.  Cardinal, Crescent, and Silver are spelled out.
* The Northeast Corridor gets the NEC acronym.
* Other regional services are spelled out.

Other notes on file naming:

* Use only lowercase.
* Use dashes to separate words.

Notes on particularly difficult timetables:

* coast-starlight: requires a patch to Amtrak GTFS (see amtrak/gtfs_cleanup.py)
* crescent: the same train number has different schedules on different days
* sunset-limited: thinks it's running to Orlando (timetable accounts for this)
