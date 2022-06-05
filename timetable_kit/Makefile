# This is mostly used for testing right now
.PHONY: default all

default: all

export TIMETABLE_KIT_OUTPUT_DIR = ./output
export TIMETABLE_KIT_INPUT_DIR = ./specs

all: cardinal cono cz pennsylvanian empire vermont

cardinal:
	./timetable.py --spec cardinal

cono:
	./timetable.py --spec city-of-new-orleans-illini-saluki city-of-new-orleans-illini-saluki-future

cz:
	./timetable.py --spec california-zephyr california-zephyr-future

pennsylvanian:
	./timetable.py --spec pennsylvanian

empire:
	./timetable.py --spec empire-w empire-e

empire-builder:
	./timetable.py --spec empire-builder empire-builder-future

vermont:
	./timetable.py --spec vermonter ethan-allen-express upstate-ny-to-western-vermont-services
