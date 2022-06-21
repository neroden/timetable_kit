This directory contains spec files for Amtrak.

The naming format for long-distance trains uses the full name of the train route or routes involved, except as follows:

* For separate winter and summer schedules, "winter" and "summer" are suffixed
* Where a schedule is changing in the near future, "future" is suffixed

The naming format for regional timetables with many services varies:

* If the service has a name, like "Empire Service" or "Silver Service", this is used
* If it doesn't, a state or regional name is used like "Virginia" or "Carolinas" with the word "services" (plural) after it
* For separate weekday and weekend timetables, "weekday" and "weekend" are suffixed first
* Where there are separate eastbound and westbound or northbound and southbound timetables, "eb", "wb", "nb", "sb" are suffixed next
* Where multiple pages are necessary, a number like "1" is suffixed last

For connecting buses and similar services, all should have "cxn" in the spec name:

* The primary service which it connects to is abbreviated with an acronym, followed by "cxn", followed by a name for the bus service.
* The acronyms for long-distance trains are CS, EB, CZ, SWC, SL, TE, CONO, LSL, CL.  Cardinal, Crescent, and Silver are spelled out.
* The Northeast Corridor gets the NEC acronym.
* Other regional services are spelled out.

Other notes on file naming:

* Use only lowercase.
* Use dashes to separate words.

Notes on particularly difficult timetables:

* coast-starlight: requires a patch to Amtrak GTFS (see amtrak/gtfs_cleanup.py, invoked by timetable.py)
* crescent: the same train number has different schedules on different days
* sunset-limited: thinks it's running to Orlando (timetable accounts for this)

Files to assemble individual pages into a multi-page timetable end with ".list".
Each one is a list of individual page output filenames (no suffix), in the correct order.
