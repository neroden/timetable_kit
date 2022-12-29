Connecting Services Subpackage
******************************

This contains python modules for adding the logo of a connecting service to a station info box on a timetable, with a link to the connecting service.

This is a work in progress.

connecting_agencies.csv
-----------------------
This is a small database.  The columns are as follows:

agency_code - internal code for the agency; this is used elsewhere to specify which stations have connections with this agency.
logo_filename - filename for the SVG logo for the agency (found in the logos folder under this package), with no suffix.
alt - code to use in the timetable if logo is not present or there are no graphics.  Keep SHORT
title - mouseover text for the logo.  Can be more descriptive
full_name - description of the agency for the key at the bottom of the timetable.  Can be more descriptive.
url - agency's URL
