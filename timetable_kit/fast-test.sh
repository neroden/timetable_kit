#! /bin/bash
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
# Make all the timetables currently being prepared


# Test all four functional submodules

# Test a very long table to make sure there's no overflow
./timetable.py --agency amtrak --spec empire-builder
# Test noheader
./timetable.py --agency amtrak --spec vermont-to-upstate-ny
# Test landscape, and coloring, and some other stuff
./timetable.py --agency amtrak --spec grand-canyon

# Test VIA
./timetable.py --agency via --spec ocean

# Test Maple Leaf
./timetable.py --agency maple_leaf --spec maple-leaf

# ./timetable.py --agency hartford --spec hartford-line-valley-flyer.list
