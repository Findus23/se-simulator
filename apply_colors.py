#!/usr/bin/env python
import utils
from models import *
from extra_data import site_colors

for site in Site.select():
    if site.url in site_colors:
        site.primary_color = "#" + site_colors[site.url]["primary"]
        site.foreground_color = "#" + site_colors[site.url]["fg"]
        site.background_color = "#" + site_colors[site.url]["bg"]
        site.save()
