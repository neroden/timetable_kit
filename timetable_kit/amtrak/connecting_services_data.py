# amtrak/connecting_services_data.py
# Part of timetable_kit
#
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.
"""This module is a database of which Amtrak stations connect to which other transit
services.

Sadly, it must be maintained by hand.
"""

# key: amtrak station code
# value: list of services (strings matching the definitions in timetable_kit/connecting_services/*.py
# Order matters: it's the order the logos will be printed in
connecting_services_dict: dict[str, list[str]] = {
    # Downeaster
    "HHL": ["mbta"],  # Haverhill
    "WOB": ["mbta"],  # Woburn on Lowell Line
    "BON": ["mbta"],  # Boston North
    # NEC, from north to south
    "BOS": ["mbta"],
    "BBY": ["mbta"],
    "RTE": ["mbta"],
    "PVD": ["mbta"],
    "KIN": [],
    "WLY": [],
    "MYS": [],
    "NLC": ["shore_line_east"],
    "OSB": ["shore_line_east"],
    "NHV": ["shore_line_east", "hartford_line", "metro_north"],
    "BRP": ["metro_north"],
    "STM": ["metro_north"],
    "NRO": ["metro_north"],
    "NYP": ["njt", "nyc_subway", "lirr"],
    "NWK": ["njt", "path"],
    "EWR": ["njt"],
    "MET": ["njt"],
    "NBK": ["njt"],
    "PJC": ["njt"],
    "TRE": ["septa", "njt"],
    "CWH": ["septa"],
    "PHN": ["septa"],
    "PHL": ["septa", "njt"],
    "WIL": ["septa"],
    "NRK": ["septa"],
    # Note: Perryville MARC would go here
    "ABE": ["marc"],
    "BAL": ["marc", "baltimore_lrt"],
    "BWI": ["marc"],
    "NCR": ["marc", "wmata"],
    "WAS": ["marc", "wmata", "dc_streetcar", "vre"],
    #
    # Following Silver Service:
    # VRE Fredericksburg branch
    "ALX": ["wmata", "vre"],
    "WDB": ["vre"],
    "QAN": ["vre"],
    "FBG": ["vre"],
    "ASD": [],
    # Orlando, Florida
    "WPK": ["sunrail"],
    "ORL": ["sunrail"],
    "KIS": ["sunrail"],
    # Miami, Florida
    "WPB": ["tri_rail"],
    "DLB": ["tri_rail"],
    "DFB": ["tri_rail"],
    "FTL": ["tri_rail"],
    "HOL": ["tri_rail"],
    "MIA": ["tri_rail", "miami_metrorail"],
    #
    # Following Crescent:
    # VRE Manassas branch
    "BCV": ["vre"],
    "MSS": ["vre"],
    # Charlotte connections will go here eventually... FIXME
    #
    # Hartford Line
    "SPG": ["hartford_line"],
    "WNL": ["hartford_line"],
    "WND": ["hartford_line"],
    "HFD": ["hartford_line"],
    "BER": ["hartford_line"],
    "MDN": ["hartford_line"],
    "WFD": ["hartford_line"],
    "STS": ["shore_line_east", "hartford_line"],
    # NHV done under NEC, above
    #
    # Adirondack route to Canada
    "SLQ": ["via_rail", "exo"],
    "MTR": ["via_rail", "exo", "montreal_metro"],
    # FIXME add Montreal etc.
    #
    # East Coast to Chicago, from north to south (+ Maple Leaf):
    # Lake Shore Limited heading out of Boston
    "FRA": ["mbta"],
    "WOR": ["mbta"],
    # SPG done under Hartford Line
    # Empire Service / LSL heading out of NYC, plus Maple Leaf
    "CRT": ["metro_north"],
    "POU": ["metro_north"],
    "UCA": ["adirondack"],
    "BFX": ["nfta_metro"],
    # Maple Leaf.
    "NFS": ["via_rail", "go_transit"],
    "SCA": ["via_rail", "go_transit"],
    "GMS": ["via_rail"],
    "AST": ["via_rail", "go_transit"],
    "OKL": ["via_rail", "go_transit"],
    "TWO": ["via_rail", "go_transit", "union_pearson_express", "ttc"],
    # Keystone Service
    "ARD": ["septa"],
    "PAO": ["septa"],
    "EXT": ["septa"],
    "DOW": ["septa"],
    "COT": [],  # Future SEPTA service
    # Capitol Limited
    "RKV": ["marc"],
    "HFY": ["marc"],
    "MRB": ["marc"],
    #
    # Services out of Chicago, going clockwise:
    # Chicago
    "CHI": ["metra"],
    #
    # Detroit
    "DET": ["qline"],
    # Cardinal:
    # Dyer station misconnects with new South Shore Line station :-(
    #
    # Metra Electric (CONO/Illini/Saluki)
    "HMW": ["metra"],
    # CONO (also used in Crescent)
    # New Orleans
    "NOL": ["norta"],
    #
    #
    # Metra Heritage Corridor (Lincoln Service / Texas Eagle)
    "SMT": ["metra"],
    "JOL": ["metra"],
    # Lincoln Service
    "STL": ["stl_metrolink"],
    # Texas Eagle
    "DAL": ["tre", "dart"],
    "FTW": ["tre", "texrail"],
    # Heartland Flyer
    "OKC": ["okc_streetcar"],
    # Sunset Limited
    "TUS": ["tucson_sunlink_streetcar"],
    "ONA": ["metrolink"],
    "POS": ["metrolink"],
    # Remainder are in West Coast list below
    #
    # Metra BNSF Line (Quincy / CZ / SWC)
    "LAG": ["metra"],
    "NPV": ["metra"],
    # CZ: Denver
    "DEN": ["denver_rtd"],
    # CZ: Salt Lake area (UTA)
    "PRO": ["frontrunner"],
    "SLC": ["frontrunner", "uta_trax"],
    # SWC & Missouri River Runner
    "KCY": ["kc_streetcar"],
    # SWC
    "ABQ": ["nm_railrunner"],
    "SNB": ["metrolink"],
    "RIV": ["metrolink"],
    # Remainder are in West Coast list below
    #
    # Hiawatha / Empire Builder
    "GLN": ["metra"],
    "MKE": ["the_hop"],
    "MSP": ["twin_cities_metro_transit"],
    # Remainder are in West Coast list below
    #
    # West Coast, north to south
    # Vancouver, BC FIXME
    "VAC": ["via_rail", "skytrain"],
    # Seattle Area
    # Sound Transit's website is terrible.
    "EVR": ["sounder"],
    "EDM": ["sounder"],
    "SEA": ["sounder", "seattle_link"],
    "TUK": ["sounder"],
    "TAC": ["sounder", "tacoma_link"],
    # If we decide to list these all just as "Sound Transit"
    # "EVR": ["sound_transit"],
    # "EDM": ["sound_transit"],
    # "SEA": ["sound_transit"],
    # "TUK": ["sound_transit"],
    # "TAC": ["sound_transit"],
    # Portland
    "PDX": ["trimet", "portland_streetcar"],
    # Capitol Corridor
    "COX": [],
    "ARN": [],
    "RLN": [],
    "RSV": [],
    "SAC": ["sacramento_rt"],
    "DAV": [],
    "FFV": [],
    "SUI": [],
    "MTZ": [],
    "RIC": ["bart"],
    "BKY": [],
    "EMY": [],
    "OKJ": [],
    "OAC": ["bart"],
    "HAY": [],
    "FMT": ["ace"],  # ACE at Fremont
    "GAC": ["ace", "vta"],
    "SCC": ["caltrain", "ace"],
    "SJC": ["caltrain", "ace", "vta"],
    # San Joaquins
    # Cabral Station for ACE
    "SKT": ["ace"],
    # Los Angeles area
    # Pacific Surfliner:
    "VEC": [],  # Metrolink Ventura is not Amtrak Ventura
    "OXN": ["metrolink"],
    "CML": ["metrolink"],
    "MPK": ["metrolink"],
    "SIM": ["metrolink"],
    "CWT": ["metrolink"],
    "VNC": ["metrolink"],
    "BUR": ["metrolink"],
    "GDL": ["metrolink"],
    "LAX": ["metrolink", "la_metro"],
    "FUL": ["metrolink"],
    "ANA": ["metrolink"],
    "SNA": ["metrolink"],
    "IRV": ["metrolink"],
    "SNC": ["metrolink"],
    # San Clemente Pier?  Listed in schedule
    "OSD": ["metrolink", "coaster", "sprinter"],
    "SOL": ["coaster"],
    "OLT": ["coaster", "san_diego_trolley"],
    "SAN": ["coaster", "san_diego_trolley"],
}
