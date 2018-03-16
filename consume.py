import glob
import os
import shutil
import subprocess
from datetime import datetime

from models import *
from parsexml import parse_posts, parse_comments, parse_usernames
from utils import *

files = get_files()
# os.chdir("/mydir")
for file in glob.glob("downloads/**/*.7z"):
    if "meta" in file:
        continue
    filename = os.path.basename(file)
    code = os.path.splitext(filename)[0]
    if filename not in files:
        print("{file} doesn't exist on archive.org".format(file=file))
        continue
    meta = files[filename]
    sha1 = file_hash(file)
    if sha1 != meta["sha1"]:
        print("{file}: hashes don't match".format(file=filename))
        continue
    alias = Alias.select().where(Alias.url == code)
    if len(alias) != 0:
        site_id = alias[0].site_id
        print(site_id)
        site = Site.select().where(Site.id == site_id)[0]
    else:
        db_element = Site().select().where(Site.url == code)
        if len(db_element) == 0:
            print("{site} not found in database".format(site=code))
            continue
        site = db_element[0]
    mtime = datetime.fromtimestamp(int(meta["mtime"]))
    if site.last_download == mtime:
        print("{site} is up to date".format(site=filename))
        continue
    else:
        site.last_download = mtime
        site.save()
    print(code)
    currentdir = os.getcwd()
    rawdir = "raw/" + code
    sitesdir = "sites/" + code
    for dir in [rawdir, sitesdir]:
        if not os.path.exists(dir):
            os.mkdir(dir)

    shutil.copy2(file, rawdir)
    os.chdir(rawdir)
    print("Start extracting")
    subprocess.check_output(["7z", "x", "-aoa", code + ".7z"])
    os.chdir(currentdir)
    print("Start parsing")
    parse_posts(rawdir, sitesdir)
    parse_comments(rawdir, sitesdir)
    parse_usernames(rawdir, sitesdir)
    print("DONE")
