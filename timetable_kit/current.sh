# Amtrak timetables currently produceable (we think)
LD_WEST="empire-builder california-zephyr southwest-chief sunset-limited texas-eagle coast-starlight"
LOCAL_WEST="heartland-flyer grand-canyon"
# Omits Winter Park Express due to lack of data
# Omits capitol-corridor.list, san-joaquin.list, pacific-surfliner.list, cascades.list
# due to official timetable existing (reconsider this)
MIDWEST="hiawatha.list illinois-missouri-services.list city-of-new-orleans-illini-saluki michigan-services.list"
LD_EAST="lake-shore-limited capitol-limited cardinal crescent silver-service.list"
LOCAL_NEW_ENGLAND="vermonter ethan-allen-express-abbrev vermont-to-upstate-ny adirondack-short berkshire-flyer"
# Incomplete version of Ethan Allen due to missing bus data
# Omits Adirondack due to suspensions
# Omits Maple Leaf (long AND short version) due to Amtrak errors; get it from VIA
# Omits Downeaster due to official timetable existing, bus data issues (reconsider this)
# We have to actually make a spec for the Downeaster
LOCAL_NORTHEAST="empire-service.list keystone-service.list pennsylvanian"
LOCAL_SOUTHEAST="virginia-services.list carolinian-piedmont"
NEC="nec-bos-was.list"

ALL_AMTRAK="$LD_WEST $LOCAL_WEST $MIDWEST $LD_EAST $LOCAL_NEW_ENGLAND $LOCAL_NORTHEAST $LOCAL_SOUTHEAST"
./timetable.py --input-dir specs_amtrak --agency amtrak --spec $ALL_AMTRAK


ALL_VIA="canadian.list remote-services.list corridor.list maple-leaf"
./timetable.py --input-dir specs_via --agency via --spec $ALL_VIA
