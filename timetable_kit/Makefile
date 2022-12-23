# This is mostly used for testing right now
.PHONY: default all

default: all

export TIMETABLE_KIT_OUTPUT_DIR = ./output
export TIMETABLE_KIT_INPUT_DIR = ./specs_amtrak

all: empire

empire:
	./timetable.py --spec empire-service.list
