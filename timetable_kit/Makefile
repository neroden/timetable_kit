# This is mostly used for testing right now
.PHONY: default all

default: all

export TIMETABLE_KIT_OUTPUT_DIR = ./output
export TIMETABLE_KIT_INPUT_DIR = ./specs

all: cardinal cono cz pennsylvanian empire-w

cardinal:
	./timetable.py --spec cardinal

cono:
	./timetable.py --spec cono cono-short

cz:
	./timetable.py --date 20220415 --spec cz
# Arbitrary date

pennsylvanian:
	./timetable.py --date 20220415 --spec pennsylvanian
# Arbitrary date

empire-w:
	./timetable.py --spec empire-w
