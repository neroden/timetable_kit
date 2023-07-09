# Amtrak timetables currently produceable (we think)
LD_WEST="empire-builder california-zephyr southwest-chief sunset-limited texas-eagle coast-starlight"
LOCAL_WEST="heartland-flyer grand-canyon"
# Omits Winter Park Express due to lack of data
# Omits capitol-corridor.list, san-joaquin.list, pacific-surfliner.list, cascades.list
# due to official timetable existing (reconsider this)
MIDWEST="hiawatha.list illinois-missouri-services.list city-of-new-orleans-illini-saluki michigan-services.list"
LD_EAST="lake-shore-limited capitol-limited cardinal crescent silver-service.list"
LOCAL_NEW_ENGLAND="vermonter vermonter-valley-flyer ethan-allen-express vermont-to-upstate-ny adirondack berkshire-flyer"
# Omits Downeaster because official timetable is MUCH better than mine (go Maine)
# Amtrak timetables omit Maple Leaf (see below)
LOCAL_NORTHEAST="empire-service.list keystone-service.list pennsylvanian"
LOCAL_SOUTHEAST="virginia-services.list carolinian-piedmont"
NEC="nec-bos-was.list"

ALL_AMTRAK="$LD_WEST $LOCAL_WEST $MIDWEST $LD_EAST $LOCAL_NEW_ENGLAND $LOCAL_NORTHEAST $LOCAL_SOUTHEAST"
./timetable.py --agency amtrak --spec $ALL_AMTRAK

# VIA timetables omit Maple Leaf (see below)
ALL_VIA="canadian.list ocean remote-services.list corridor.list"
./timetable.py --agency via --spec $ALL_VIA

# Maple Leaf is best done as a VIA/Amtrak hybrid
./timetable.py --agency maple_leaf --spec maple-leaf

# Hartford Line is an Amtrak/Hartford Line hybrid
./timetable.py --agency hartford --spec hartford-line-valley-flyer.list
