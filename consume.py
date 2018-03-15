import glob
import os
import shutil
import subprocess

from parsexml import parse_posts, parse_comments, parse_usernames

# os.chdir("/mydir")
for file in glob.glob("downloads/**/*.7z"):
    if not "astronomy" in file:
        continue
    code = os.path.basename(os.path.splitext(file)[0])
    print(code)
    directory = "sites/" + code
    if not os.path.exists(directory):
        os.mkdir(directory)
    shutil.copy2(file, directory)
    os.chdir(directory)
    print("Start extracting")
    subprocess.check_output(["7z", "x", "-aoa", code + ".7z"])
    os.chdir("../../")
    print("Start parsing")
    parse_posts(directory)
    parse_comments(directory)
    parse_usernames(directory)
    print("DONE")
