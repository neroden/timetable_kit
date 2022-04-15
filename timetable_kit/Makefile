# This is mostly used for testing right now
.PHONY: default all

default: all

OUTPUT_DIR = "./output"
INPUT_DIR = "./specs"

all: cardinal cono cz pennsylvanian empire-w

cardinal:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" -i "$(INPUT_DIR)" --spec cardinal

cono:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" -i "$(INPUT_DIR)" --spec cono cono-short

cz:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" -i "$(INPUT_DIR)" --date 20220415 --spec cz
# Arbitrary date

pennsylvanian:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" -i "$(INPUT_DIR)" --date 20220415 --spec pennsylvanian
# Arbitrary date

empire-w:
	./timetable.py --author "$(AUTHOR)" -o "$(OUTPUT_DIR)" -i "$(INPUT_DIR)" --spec empire-w
