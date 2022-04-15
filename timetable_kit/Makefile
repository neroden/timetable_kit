# This is mostly used for testing right now
.PHONY: default all

default: all

OUTPUT_DIR = "./output"
INPUT_DIR = "./specs"

all: cardinal cono cz pennsylvanian empire-w

cardinal:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --spec cardinal

cono:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --spec cono cono-short

cz:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --date 20220329 --spec cz
# Arbitrary date

pennsylvanian:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" --date 20220330 -i "$(INPUT_DIR)" --spec pennsylvanian
# Arbitrary date

empire-w:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)"  --spec empire-w
