#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils
from models import *
from extra_data import site_colors


def main():
    for site in Site.select():
        if site.url in site_colors:
            site.primary_color = "#" + site_colors[site.url]["primary"]
            site.foreground_color = "#" + site_colors[site.url]["fg"]
            site.background_color = "#" + site_colors[site.url]["bg"]
            site.save()


if __name__ == "__main__":
    main()

