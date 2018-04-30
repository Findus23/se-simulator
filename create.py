#!/usr/bin/env python
# -*- coding: utf-8 -*-

import html
import requests

from urllib.parse import urlparse

from models import Alias
from models import Answer
from models import Question
from models import Site
from models import Title
from models import User


def main():
    mdls = [Answer, Question, Title, User, Alias, Site]
    for i in mdls:
        i.drop_table()
    for i in reversed(mdls):
        print(i)
        i.create_table()

    r = requests.get("https://api.stackexchange.com/2.2/sites?pagesize=500")
    for site in r.json()["items"]:
        if site["site_type"] == "meta_site":
            continue
        element, created = Site.get_or_create(shortname=site["api_site_parameter"])
        print(created)
        element.name = html.unescape(site["name"])
        element.shortname = site["api_site_parameter"]
        element.url = urlparse(site["site_url"]).hostname
        element.icon_url = site["high_resolution_icon_url"] if "high_resolution_icon_url" in site else site["icon_url"]
        styling = site["styling"]
        element.tag_background_color = styling["tag_background_color"]
        element.tag_foreground_color = styling["tag_foreground_color"]
        element.link_color = styling["link_color"]
        element.save()
        if "aliases" in site:
            for al in site["aliases"]:
                domain = urlparse(al).hostname
                alias, created = Alias.get_or_create(url=domain, site=element)


if __name__ == "__main__":
    main()

