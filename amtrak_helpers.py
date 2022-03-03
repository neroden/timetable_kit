#! /usr/bin/env python3
# amtrak_helpers.py
# Part of timetable_kit
#
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

'''
This module includes Amtrak *data* which isn't provided by Amtrak.
This includes the list of which stations are major,
which trains carry checked baggage (not implemented FIXME),
known problems with Amtrak's GTFS data, and similar.
(Functions for extracting data from Amtrak's JSON stations database is elsewhere.)
'''

# GLOBAL VARIABLES
#
# Known problems in Amtrak data
global_bad_service_ids = [2819372, # Cardinal one-day service when it doesn't run on that day
                         ]

# "Major stations".  This is for timetable styling: making them bigger and bolder.
# This should really be per-timetable but this is a start
# (Empire doesn't call out NEC stations on connecting trains)
# (Vermonter only callse out NY and DC on NEC)
major_stations_list = ( "BOS", # NEC timetable stations first
    "NHV",
    "NYP",
    "NYG", # Just in case there's a reroute
    "PHL",
    "WAS",
    "LYH", # Virginia service timetable
    "RVR",
    "NFK",
    "HAR", # Keystone timetable
    "PIT",
    "ALB", # Empire timetable
    "BFX",
    "TWO",
    "MTR", # Adirondack
    "ESX", # Vermonter
    "SPG",
    "RUD", # Ethan Allen -- will change to Burlington
    "RGH", # Carolinian/Piedmont
    "CLT",
    "ATL", # Crescent
    "BHM",
    "NOL",
#    "ALT", # Pennsylvanian -- I think I won't emphasize this one.
    "CVS", # Cardinal
    "CIN",
    "IND",
    "CHI",
    "CLE", # LSL / CL
    "TOL",
    "GRR", # Michigan services
    "PTH",
    "DET",
    "PNT",
    "CHM", # CONO/Illini/Saluki
    "CDL",
    "MEM",
    "JAN",
    "STL", # River Runner
    "KCY",
    "QCY", # Quincy service
    "MKE", # Hiawathas
    "SAN", # California Coastal
    "LAX",
    "SBA",
    "SLO",
    "SJC",
    "OKJ",
    "SAC",
    "SKN", # San Joaquins
    "BFD",
    )

def is_standard_major_station(station_code):
    '''
    Is a station on the list of standard 'major stations' for Amtrak
    '''
    return (station_code in major_stations_list)
