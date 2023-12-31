#! /bin/sh
mkdir timetables
cp output/*.html timetables/
cp -r output/icons timetables/icons
cp -r output/logos timetables/logos
cp -r output/fonts timetables/fonts
zip -r timetables.zip timetables
rm -r timetables
