import glob
import os
import shutil
import subprocess

from parsexml import parse_posts, parse_comments, parse_usernames
from utils import *
# os.chdir("/mydir")
for file in glob.glob("downloads/**/*.7z"):
    if not "worldbuilding" in file:
        continue
    code = os.path.basename(os.path.splitext(file)[0])
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
