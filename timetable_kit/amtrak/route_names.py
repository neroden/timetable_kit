# amtrak/route_names.py
# Part of timetable_kit
# Copyright 2022 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

def get_route_name(today_feed, route_id):
    """
    Given today_feed and a route_id, produce a suitable name for a column subheading.

    This is somewhat Amtrak-specific.  The route_long_names are mostly fine but too long.
    The bus situation, however, is ugly.
    """
    filtered_routes = today_feed.routes[today_feed.routes.route_id == route_id]
    num_rows = filtered_routes.shape[0]
    if (num_rows == 0):
        raise GTFSError("Route not found")
    elif (num_rows > 1):
        print(filtered_routes)
        raise GTFSError("Too many routes")
    this_route = filtered_routes.iloc[0]

    route_name = this_route.route_long_name
    # my_route_type = this_route.route_type

    if (route_name == "Amtrak Thruway Connecting Service"):
        # This is an uninformative name, so dig deeper...
        filtered_agency = today_feed.agency[today_feed.agency.agency_id == this_route.agency_id]
        num_rows = filtered_agency.shape[0]
        if (num_rows == 0):
            raise GTFSError("Agency not found")
        elif (num_rows > 1):
            print(filtered_agency)
            raise GTFSError("Too many agencies")
        this_agency = filtered_agency.iloc[0]

        agency_name = this_agency.agency_name
        # Special case SEAT -- we don't want four-line names
        if agency_name == "Southeast Area Transit (SEAT)":
            agency_name == "SE Area Transit (SEAT)"
        # Use agency name instead of route name, please!
        route_name = agency_name

    # "Amtrak" prefix is unhelpful
    clean_route_name = route_name.removeprefix("Amtrak ")
    return clean_route_name
