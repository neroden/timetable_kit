#! /bin/bash
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
# Make all the timetables currently being prepared


# Test all four functional submodules

./timetable.py --agency amtrak --spec empire-builder
./timetable.py --agency amtrak --spec vermont-to-upstate-ny

./timetable.py --agency via --spec ocean

./timetable.py --agency maple_leaf --spec maple-leaf

# ./timetable.py --agency hartford --spec hartford-line-valley-flyer.list
