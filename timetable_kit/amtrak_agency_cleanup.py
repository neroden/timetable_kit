# amtrak_agency_cleanup.py
# Part of timetable_kit
# Copyright 2021, 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Subroutines to clean up Amtrak's names for agencies, which are less than helpful
"""

import pandas as pd
import gtfs_kit as gk

# This one is mine
import gtfs_type_cleanup

def indexed_agency(agency):
    """
    Take type-correted agency DataFrame.  Set agency ID (which must be an integer) as index.
    Sort by it.  Cannot be repeated.
    """
    # Not as helpful as we first supposed.
    # NOTE that this eliminates the ability to refer to it by the agency_id name;
    # it must only be "index" now
    # Requires that agency_id already be an integer
    revised_agency_3 = agency.set_index('agency_id')
    revised_agency_3.sort_index(inplace=True);
    return revised_agency_3;

# Method 1
def lookup_agency_name_1(agency, agency_id):
    """
    Takes agency_id (a string), returns agency_name (a string).  With duplicate IDs, grabs the first
    """
    return agency[(agency.agency_id == agency_id)]['agency_name'].iloc[0]

# Method 2
def lookup_agency_name_2(agency, agency_id):
    # A complex trick to generate a dict from the Pandas Dataframe
    agency_lookup_table = dict(zip(agency.agency_id, agency.agency_name))
    return agency_lookup_table[agency_id]

# Method 3
def lookup_agency_name_3(agency, agency_id):
    # Sneaky use of set_index and to_dict
    # Expand the lookup table to fill in the nameless agencies
    # oh yeah
    indexed_agency = agency.set_index('agency_id')
    agency_lookup_table = indexed_agency.to_dict()['agency_name']
    return agency_lookup_table[agency_id]

def revised_amtrak_agencies (agency):
    # Expects a type corrected agency list, but play it safe; that routine is idempotent
    revised_agency = gtfs_type_cleanup.type_corrected_agency(agency)

    # And do the irreversible indexing
    revised_indexed_agency = indexed_agency(revised_agency)

    # Manual edits to the agency lookup table for Amtrak
    # Produce a lookup table:
    agency_lookup_table = dict(zip(revised_indexed_agency.index, revised_indexed_agency.agency_name))
    # Edit the lookup table:
    agency_lookup_table[174] = "Amtrak Directly Operated Thruway Bus" # Is "Amtrak" in feed
    agency_lookup_table[192] = "Thruway Bus Operator 192"
    agency_lookup_table[1206] = "Thruway Bus Operator 1206"
    agency_lookup_table[1207] = "Thruway Bus Operator 1207"
    agency_lookup_table[1217] = "Thruway Bus Operator 1217"
    agency_lookup_table[1220] = "Thruway Bus Operator 1220"
    # Convert to Series, before stuffing the Series back into the DataFrame.
    # We have maintained alignment of revised_agency so it'll line up right.
    ser = pd.Series(data=agency_lookup_table)
    # Drop the old column
    revised_indexed_agency.drop(columns=["agency_name"], inplace=True)
    # Add the new
    revised_indexed_agency.insert(0, "agency_name", ser)
    # Mission accomplished.
    return revised_indexed_agency

### MAIN -- add testsuite
