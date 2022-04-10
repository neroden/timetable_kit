# This is mostly used for testing right now
.PHONY: default all

default: all

OUTPUT_DIR = "./output"

all: cardinal empire cono cz pennsylvanian

# Last functional date
cardinal:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --date 20220315 --spec cardinal

# Avoid the 12th.  Also, something wrong starting 14th, until May
cono:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --date 20220530 --spec cono

empire:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --date 20220329 --spec empire # Arbitrary

cz:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --date 20220329 --spec cz # Arbitrary

pennsylvanian:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --date 20220330 --spec pennsylvanian # Arbitrary
