# This is mostly used for testing right now
.PHONY: default all

default: all

all: cardinal empire cono

cardinal:
	./timetable.py --author "Nathanael Nerode" --date 20220315 --spec cardinal # Last functional date
cono:
	./timetable.py --author "Nathanael Nerode" --date 20220530 --spec cono # Avoid the 12th.  Also, something wrong starting 14th, until May

empire:
	./timetable.py --author "Nathanael Nerode" --date 20220321 --spec empire # Arbitrary

cz:
	./timetable.py --author "Nathanael Nerode" --date 20220325 --spec cz # Arbitrary
