# via/route_names.py
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""Get the name for a route.

get_route_name()

VIA is... kind of terrible about route names in their GTFS, so we use some hand-coding.
"""
from timetable_kit.errors import GTFSError

remote_service_route_names = [
    "Montréal - Senneterre",
    "Montréal - Jonquière",
    "Sudbury - White River",
    "Winnipeg - Churchill",
    "The Pas - Churchill",
    "Jasper - Prince Rupert",
]

corridor_service_route_names = [
    "Toronto - London",
    "Toronto - Kingston",
    "Montréal - Toronto",
    "Toronto - Sarnia",
    "Ottawa - Québec",
    "Toronto - Windsor",
    "Ottawa - Montréal",
    "Ottawa - Toronto",
    "Québec - Fallowfield",
    "Québec - Montréal",
    "Montréal - Aldershot",
]


def get_route_name(today_feed, route_id):
    """Given today_feed and a route_id, produce a suitable name for a column
    subheading.

    This is very VIA-specific.  The route_long_names are mostly a pair
    of cities.
    """
    filtered_routes = today_feed.routes[today_feed.routes.route_id == route_id]
    num_rows = filtered_routes.shape[0]
    if num_rows == 0:
        raise GTFSError("Route not found")
    if num_rows > 1:
        print(filtered_routes)
        raise GTFSError("Too many routes")
    this_route = filtered_routes.iloc[0]

    route_name = this_route.route_long_name
    # NOTE, the portion above this is completely standard and should be pulled
    # out to "generic agency" code

    # Only a few trains still have proper names (Canadian, Ocean, Maple Leaf).
    # Use them where available.
    # Preserve remote service names.
    # Convert all other route names to "Corridor".
    match route_name:
        case "Toronto - Vancouver":
            route_name = "The Canadian"
        case "Toronto - New York":
            route_name = "Maple Leaf"
        case "Montréal - Halifax":
            # Note accented letter in original, make sure this works
            route_name = "The Ocean"
        case name if name in corridor_service_route_names:
            # The route names for the Corridor are problematic.
            # Trains are listed as "Quebec Fallowfield" which simply aren't.
            route_name = "Corridor"

    return route_name
