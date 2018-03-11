import html
from pprint import pprint

import requests
from urllib.parse import urlparse
from models import *
from internetarchive import get_item

ignored_se_sites = ["cs50.stackexchange.com"]

ia = get_item("stackexchange")
files = {x["name"]: x for x in ia.files}
for site in Site.select()[1:]:
    if site.url in ignored_se_sites:
        continue
    key = site.url + ".7z"
    offset = 0
    while True:
        if key in files:
            file = files[key]
            break
        query = Alias.select(Alias.url).where(Alias.site == site).limit(1).offset(offset)
        if len(query) == 0:
            print("{site} ({url}) doesn't have a dump".format(site=site.name, url=site.url))
            break
        key = query[0].url + ".7z"
        offset += 1
