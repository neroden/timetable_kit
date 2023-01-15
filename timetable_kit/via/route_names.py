# via/route_names.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""
Get the name for a route.

get_route_name()

VIA is... kind of terrible about route names in their GTFS, so we use some hand-coding.
"""


def get_route_name(today_feed, route_id):
    """
    Given today_feed and a route_id, produce a suitable name for a column subheading.

    This is very VIA-specific.  The route_long_names are mostly a pair of cities.
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

    # Only a few trains still have proper names.
    # Use them where available.
    match route_name:
        case "Toronto - Vancouver":
            route_name = "The Canadian"
        case "Toronto - New York":
            route_name = "Maple Leaf"
        case "Montréal - Halifax":
            # Note accented letter in original, make sure this works
            route_name = "The Ocean"

    return route_name
