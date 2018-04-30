#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import glob
import models
import os
import parsexml
import shutil
import subprocess
import utils


def main():
    files = utils.get_files()

    # TODO: name sites/id after real url

    for file in glob.glob("downloads/**/*.7z", recursive=True):
        if "meta" in file:
            continue
        filename = os.path.basename(file)
        code = os.path.splitext(filename)[0]
        if filename not in files:
            print("{file} doesn't exist on archive.org".format(file=file))
            continue
        meta = files[filename]
        sha1 = utils.file_hash(file)
        if sha1 != meta["sha1"]:
            print("{file}: hashes don't match".format(file=filename))
            continue
        alias = models.Alias.select().where(models.Alias.url == code)
        if len(alias) != 0:
            site_id = alias[0].site_id
            print(site_id)
            site = models.Site.select().where(models.Site.id == site_id)[0]
        else:
            db_element = models.Site().select().where(models.Site.url == code)
            if len(db_element) == 0:
                print("{site} not found in database".format(site=code))
                continue
            site = db_element[0]
        mtime = datetime.datetime.fromtimestamp(int(meta["mtime"]))
        if site.last_download == mtime:
            print("{site} is up to date".format(site=filename))
            continue
        else:
            site.last_download = mtime
            site.save()
        print(code)
        currentdir = os.getcwd()
        rawdir = "raw/" + code
        chainsdir = "chains/" + code
        for dir in [rawdir, chainsdir]:
            if not os.path.exists(dir):
                os.mkdir(dir)

        shutil.copy2(file, rawdir)
        os.chdir(rawdir)
        print("Start extracting")
        subprocess.check_output(["7z", "x", "-aoa", code + ".7z"])
        os.chdir(currentdir)
        print("Start parsing")
        parsexml.parse_posts(rawdir, rawdir)
        parsexml.parse_comments(rawdir, rawdir)
        parsexml.parse_usernames(rawdir, rawdir)
        print("DONE")


if __name__ == "__main__":
    main()

