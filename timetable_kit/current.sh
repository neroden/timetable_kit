#! /bin/bash
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
# Make all the timetables currently being prepared

# Get Amtrak stations DB (very slow, don't do normally)
# cd amtrak
# ./json_stations.py download
# cd ..

# Get new gtfs for every agency
# ./timetable.py --get-gtfs --agency amtrak
# ./timetable.py --get-gtfs --agency via
# ./timetable.py --get-gtfs --agency maple_leaf
# ./timetable.py --get-gtfs --agency hartford

# Amtrak timetables currently produceable (we think)
LD_WEST="empire-builder california-zephyr southwest-chief sunset-limited texas-eagle coast-starlight"
./timetable.py --agency amtrak --spec $LD_WEST
LOCAL_WEST="heartland-flyer grand-canyon"
./timetable.py --agency amtrak --spec $LOCAL_WEST
# Omits capitol-corridor.list, san-joaquin.list, pacific-surfliner.list, cascades.list
# due to official timetable existing (reconsider this)
MIDWEST="hiawatha.list illinois-missouri-services.list city-of-new-orleans-illini-saluki michigan-services.list"
./timetable.py --agency amtrak --spec $MIDWEST
LD_EAST="lake-shore-limited capitol-limited cardinal crescent silver-service.list auto-train"
./timetable.py --agency amtrak --spec $LD_EAST
LOCAL_NEW_ENGLAND="vermonter vermonter-valley-flyer ethan-allen-express adirondack vermont-to-upstate-ny"
./timetable.py --agency amtrak --spec $LOCAL_NEW_ENGLAND
# Omits Downeaster because official timetable is MUCH better than mine (go Maine)
# Amtrak timetables omit Maple Leaf (see below)
LOCAL_NORTHEAST="empire-service.list pennsylvanian keystone-service.list"
./timetable.py --agency amtrak --spec $LOCAL_NORTHEAST
LOCAL_SOUTHEAST="carolinian-piedmont.list virginia-services.list"
./timetable.py --agency amtrak --spec $LOCAL_SOUTHEAST
SEASONAL="winter-park-express"
# SEASONAL="berkshire-flyer"
./timetable.py --agency amtrak --spec $SEASONAL
# Don't build NEC per default; it is too slow
NEC="nec-bos-was.list"
# ./timetable.py --agency amtrak --spec $NEC

# VIA timetables omit Maple Leaf (see below)
ALL_VIA="canadian.list ocean remote-services.list corridor.list"
./timetable.py --agency via --spec $ALL_VIA

# Maple Leaf is best done as a VIA/Amtrak hybrid
./timetable.py --agency maple_leaf --spec maple-leaf

# Hartford Line is an Amtrak/Hartford Line hybrid
# Currently broken
# ./timetable.py --agency hartford --spec hartford-line-valley-flyer.list
