#! /bin/bash
# Part of timetable_kit
# Copyright 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
# Make all the timetables currently being prepared

# Get Amtrak stations DB (very slow, don't do normally)
# cd amtrak
# ./json_stations.py download
# cd ..

# Get new gtfs for every agency
cd amtrak
./get_gtfs.py
cd ..
cd via
./get_gtfs.py
cd ..
cd maple_leaf
./merge_gtfs.py
cd ..
cd hartford_line
./get_gtfs.py
./merge_gtfs.py
cd ..

# Amtrak timetables currently produceable (we think)
LD_WEST="empire-builder california-zephyr southwest-chief sunset-limited texas-eagle coast-starlight"
LOCAL_WEST="heartland-flyer grand-canyon"
# Omits winter-park-express due to seasonality
# Omits capitol-corridor.list, san-joaquin.list, pacific-surfliner.list, cascades.list
# due to official timetable existing (reconsider this)
MIDWEST="hiawatha.list illinois-missouri-services.list city-of-new-orleans-illini-saluki michigan-services.list"
LD_EAST="lake-shore-limited capitol-limited cardinal crescent silver-service.list auto-train"
LOCAL_NEW_ENGLAND="vermonter vermonter-valley-flyer ethan-allen-express adirondack"
# Omits berkshire-flyer due to seasonality
# Omitted due to bugs: vermont-to-upstate-ny -- FIXME
# Omits Downeaster because official timetable is MUCH better than mine (go Maine)
# Amtrak timetables omit Maple Leaf (see below)
LOCAL_NORTHEAST="empire-service.list pennsylvanian carolinian-piedmont.list"
# Omittted due to bugs: keystone-service.list (637) virginia-services.list (157) -- FIXME
LOCAL_SOUTHEAST=""
# Don't build NEC per default; it is too slow
NEC="nec-bos-was.list"

ALL_AMTRAK="$LD_WEST $LOCAL_WEST $MIDWEST $LD_EAST $LOCAL_NEW_ENGLAND $LOCAL_NORTHEAST $LOCAL_SOUTHEAST"
./timetable.py --agency amtrak --spec $ALL_AMTRAK

# VIA timetables omit Maple Leaf (see below)
ALL_VIA="canadian.list ocean remote-services.list corridor.list"
./timetable.py --agency via --spec $ALL_VIA

# Maple Leaf is best done as a VIA/Amtrak hybrid
./timetable.py --agency maple_leaf --spec maple-leaf

# Hartford Line is an Amtrak/Hartford Line hybrid
# Currently broken
# ./timetable.py --agency hartford --spec hartford-line-valley-flyer.list
