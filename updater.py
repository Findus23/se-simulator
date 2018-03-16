from internetarchive import get_item, download

from models import *
from utils import *

ignored_se_sites = ["cs50.stackexchange.com"]

files = get_files()
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
            file = {}
            break
        key = query[0].url + ".7z"
        offset += 1
    if file:
        sizeMB = int(file["size"]) / 1024 / 1024
        if sizeMB < 50:
            print(file)
            print(sizeMB)
            exit()
