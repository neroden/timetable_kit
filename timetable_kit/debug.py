# debug.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

"""
Debugging routines

debug_print()
"""

# Global variable controlling debugging status
# 1 is normal and should be on at all times.
# 0 means no debugging.
# 2 and 3 mean more extensive debugging.
debug = 1


def set_debug_level(level: int):
    global debug
    debug = level
    return


def debug_print(level: int, *args, **kwargs):
    if debug >= level:
        print(*args, **kwargs)
    return
