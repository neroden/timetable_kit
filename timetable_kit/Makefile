# This is mostly used for testing right now
.PHONY: default all

default: all

all: cardinal empire cono cz

cardinal:
	./timetable.py --author "$(AUTHOR)" --date 20220315 --spec cardinal # Last functional date
cono:
	./timetable.py --author "$(AUTHOR)" --date 20220530 --spec cono # Avoid the 12th.  Also, something wrong starting 14th, until May

empire:
	./timetable.py --author "$(AUTHOR)" --date 20220329 --spec empire # Arbitrary

cz:
	./timetable.py --author "$(AUTHOR)" --date 20220329 --spec cz # Arbitrary
