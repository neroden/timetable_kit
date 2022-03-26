#! /usr/bin/env python3
# parse_wnn.py
"""
Test file to see if we can extract key info from Amtrak's station web pages
"""
from lxml import html

filename = "wnn.html"
with open(filename, "rb") as f:
   html_str = f.read()
html_tree = html.fromstring(html_str)
description = html_tree.xpath('//h5[@class="hero-banner-and-info__card_station-type"]/text()')
print(description)
