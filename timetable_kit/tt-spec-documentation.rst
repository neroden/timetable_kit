=======
TT-SPEC
=======
The "tt-spec" file format is a template used to generate the timetable
This document describes format as currently implemented.
It consists of a CSV file (foo.csv) and a JSON file (foo.json).

The tt-spec format remains a work in progress and may change at any time.

RATIONALE
---------
The timetable generating kit generates a pretty timetable, as HTML, PDF, or CSV, from several things:
- GTFS static data
- Amtrak station name information (in json form) from Amtrak's website
- Other Amtrak information from various sources (some embedded in the program)
- A template, written by the user, in "tt-spec" format.

It is necessary to have a template system because timetable design is actually
an art.  A timetable can list a train but not all the stations it goes to;
a station but not all the trains that stop at it; connecting trains; and notes like
"continues to Chicago".  In traditional Amtrak timetables, the same train might be
listed in four different timetables, but from different perspectives: the Coast Starlight,
for instance, has its own timetable, and appears in the Pacific Surfliner, Cascades,
San Joaquins, and California Coastal Services timetables as well.  

Note the following:
Amtrak train numbers are in the "trip_short_name" field of GTFS static data
Amtrak station codes are in the "stop_id" field of GTFS static data.
I will use "trip_short_name" and "train number" interchangeably.
I will used "station code" and "stop_id" interchangeably.

CSV FILE FORMAT
---------------
The main part of the tt-spec format is a CSV file.  It can (and should) be edited in a spreadsheet program.
For convenience, it should have a ".csv" suffix.

There are two varieties: a complete spec and a shorthand spect.

The top left cell is a "key" cell: it is blank for a complete spec.
For a "shorthand" spec it contains key information.

LEFT COLUMN
-----------
The left column (except for the top left key cell) contains station codes (stop_id) in order,
exactly the order the rows will appear in the timetable.

SPECIAL ROWS
------------
A blank cell can be left in the left column to use a line for something other than station times, free-form.
This might be used to provide a line which has a "header" for a "connecting train" section.

The special code "route-name" in the left column can be used to generate cells containing the name of the train route (route_long_name).  For Amtrak, if this is "Amtrak Thruway Connecting Service", instead the name of the agency (agency_name) will be inserted.

The special code "days" or "days-of-week" in the left column will generate a row with codes like "Daily", "MoWeFr", "SaSu", etc.  For each column where you want such a day to be specified, you must specify a station code in this row and that column.  (This is because the days depend on the station, for trains crossing midnight or in a different timezone than the agency timezone.)  The first station in the timetable is probably a good choice.  To leave out this notation for a particular column, simply omit the station code.

The special code "updown" will generate "Read Up" and "Read Down" notices.  See the "reverse" option in column-options below.

SHORTHAND SPEC
--------------
For a "shorthand" spec, the key cell contains the words "stations of XXX", 
where XXX is a train number (trip_short_name).  This will fill the left column with all the stations
from train number XXX in the correct order.  This makes simple timetables simpler, but doesn't allow all layouts.

If this is done, there should be only one row in the spec (the top row)
Or the special second row "column-options" may be included (see below),
or perhaps extra free-form decorative header rows.

Since the left column will be appended to the spec, any actual station rows listed will come before
the automatically generated stations, which could give strange results.

TOP ROW
-------
The top row (except for the leftmost Key cell) contains train numbers (trip_short_name) in order, 
in exactly the order the columns will appear in the timetable.

Several train numbers separated by slashes can be used to put several trains in one column, for connecting services, splitting/joining trains, etc.

A train number followed by a space and a day of the week ("monday" for instance) extracts the schedule for that specific day of the week.  This is used when the same train number has different schedules on different days of the week: a bad and confusing practice, but one which is done by some transit agencies and allowed by GTFS.
This is not well tested.  It must be exactly one space and the day of the week must be lowercase, so "91 monday".

SPECIAL COLUMNS
---------------
The special code "station" or "stations in the top row can be used to generate cells containing the name and details of the station.  This is retrieved from the Amtrak station data on the Web which is on the web in json format; the json files for the station data must be downloaded in advance, using './amtrak/json_stations.py download' into the ./amtrak/stations/ directory.  This is to avoid beating too hard on Amtrak's website.

The special code "services" in the top row can be used to generate cells containing icons for the station services.  So far only accessibility is implemented.

The special code "timezone" in the top row will generate a column with codes for the timezones of the stations.  Strongly
recommended for any train which crosses two timezones.

The special code "ardp" generates cells containing "Ar" and "Dp", or blank ***not implemented

Multiple trains can be listed in a single cell, separated by slashes, such as 314/304.
This will allow them to share a single column.  The time for the first train will be used, unless it doesn't
stop at that station, in which case the second train will be checked, etc.

Be careful about using this as it is fragile: it is intended for splitting trains like the Lake Shore Limited, or
"designed" connecting services such as Lincoln Service / Missouri River Runner at St Louis.
This will give a complex stacked cell for "train name".  *** needs testing
You will want to do some manual cells (see below).


COLUMN-OPTIONS IN SECOND ROW
----------------------------
If the first column of the second row contains the text "column-options" (without the quotes),
then the second row is treated as a list of specifications for how to render the columns.

It MUST be the second row.

This row will be entirely removed before rendering the timetable; it does not generate a real row.

If a cell is blank, this means that column should be rendered with default options.
If there's more than one option for a column, they are separated by WHITESPACE.

Implemented options:
reverse -- This column should read bottom to top (earlier times below later times).  (Default: top to bottom.)
days -- include string for days of operation (MoWeFr) in the time cells for this column
long-days-box -- make the box for the days long enough to hold SuMoTuWeTh (five days) rather than the default three.
short-days-box -- make the box for days only long enough to hold Mo (one day) rather than the default three.
ardp -- include "Ar" and "Dp" in this column

No other options have been defined yet.
Options which I might implement, but have not implemented, include:
color -- background colors for this column.  If the train numbers are separated by slashes, so are the background colors?
tz -- include timezone in this column

The "days" option is suitable for less-than-daily trains which run across midnight.
Less-than-daily trains which only run on one day might better have a day listed in
a column header (see above).


REST OF SPEC
------------
The internal cells (not the top row or left column) of the table should be mostly left blank.
The program fills these in from the GTFS and Amtrak station data.


SPECIAL CODES IN CELLS
----------------------
A cell to be filled in with a time may contain a special code.

This should be a (tsn / train number) saying which train's departure/arrival times to use, followed by the
word "first" or "last".  So "8 first" or "28 last".  

This is the only way to override the default "first train listed wins" behavior.
This will also suppress the display of both arrival and departure time:
"first" will only list departure time, and "last" will only list arrival time.
They will also suppress the use of "R" and "D" notations, which are obvious on the first and last trains.

These special codes are intended to be used only in four situations:
-- first station on the timetable for a train
-- last station on the timetable for a train
-- station where a train splits (list the station on two lines, and specify which line gets which tsn)
-- station where a train connects to another (list the station on two lines, and specify which line gets which tsn)

A single train number such as "8" will simply say which train to use out of several.

For technical reasons, "8 first last" will be accepted as a special code, but it may cause nonsensical behavior.

A cell may also contain the special code "blank". This is for clarity.  It will be equivalent to putting a single
space character in the cell.

CELLS WITH FREE WRITTEN TEXT
----------------------------
If you include any other text, it will be copied into the final table.
Examples include putting "to Chicago" in the cell after the last listed station for a train which
continues to Chicago after leaving the last station listed in the timetable.

Free-written text should be HTML (important if you have line breaks or want to color it).
Unfortunately, that means it will pass through as HTML in the plaintext/csv output; 
the plaintext/csv output is intended to be manually manipulated by a user, however, so this is probably OK for now.

It will get the "special-cell" CSS class; if you want any other decoration, you'll have to wrap it in a <span>,
or reference it by its cell number.  

The resulting timetable will have "col0", "col1", "row0", "row1", etc. classes (produced by PANDAS) so you can reference an
individual cell if you need to.  For these purposes, the indexes are 0-based and ignore the template's top row and left
column (which will not be present in the final timetable.

There may be additional special codes for these internal cells.
So don't count on the free-writing interface 100%.
For now, all the special codes start with a train number.

JSON FILE
-----------
Associated with the .csv file is a .json file with the same primary name.
(so, for cz.csv, use cz.json)

This is a JSON file with a list of key-value pairs.  So far the defined keys are:
::
 {
    "title": "This goes in the title bar of the HTML page",
    "heading": "This is the heading at the top of the page",
    "for_rpa": "If this is present, the timetable will be credited as being made for RPA"
    "output_subdir": "after_20220528"
    "output_filename": "special",
    "reference_date": "20220528",
    "top_text": "This will be printed prominently near the top of the timetable: should be used for special notes for this particular timetable or these particular trains.  Used for merged/split trains.",
    "bottom_text": "This will be printed less prominently underneath the symbol key.  Useful for noting seasonal stations, ticketing restrictions (no Homewood to Chicago tickets except for connecting passengers), or other oddities.",
    "key_on_right": "If present, put the symbol key on the right instead of under the timetable (for long timetables)",
    "key_baggage": "If present, include the key for checked baggage",
    "key_d": "If present, include the key for 'discharge passengers only' (D) ",
    "key_r": "If present, include the key for 'receive passengers only' (R) ",
    "key_l": "If present, include the key for 'may leave before time shown' (L) ",
    "key_f": "If present, include the key for flag stops",
    "key_tz": "If present, include the key for time zones",
    "train_numbers_side_by_side": "If present and truthy, put train numbers at the top of a column side by side like 7/27, desired for trains which split; the default is to stack them one over another like 280 over 6280, desired for connecting trains."
 }

reference_date is critically important and is required unless passed at the command line.
This filters the GTFS data to find the data valid for a particular reference date, which is necessary
to get a representative timetable.  It is annoying to have to change this in the aux file whenever you want
to make a new timetable, but it is what it is.

reference_date can be overridden by the command line, and probably should be when experimenting.

output_subdir is the name of a subdirectory of output_dir to put the output in; 
this is useful if you are making one set of timetables for one time period,
and one set for another time period, at the same time.

output_filename is the base filename of the output files (so, "special.html", "special.pdf" will be produced).
If omitted, this defaults to the same base filename as the spec file; this is here in case you want a *different*
output file name from the file name for the spec file.

In addition, every key in the .json file is passed through to the Jinja2 templates, allowing for flexibility.


ADDITIONAL TOOLS
================
These commands may be helpful in preparing spec files:

find_trains.py -- get the trains running from station A to station B
get_station_list.py -- get the list of stations which a particular train stops at
compare.py -- find timing differences on a route between similar services listed in GTFS
