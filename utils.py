import hashlib
import random
import resource
import string
import sys

from bs4 import BeautifulSoup
from internetarchive import get_item


def print_stats(i, skipped=None):
    print("{number} total entries".format(number=i))
    if skipped:
        print("{number} skipped".format(number=skipped))
    print_ram()


def print_ram():
    print("used {mb}MB".format(mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024))


def html2text(body):
    soup = BeautifulSoup(body, "lxml")
    for code in soup.find_all("code"):
        code.decompose()
    return soup.get_text()


def get_files():
    ia = get_item("stackexchange")
    return {x["name"]: x for x in ia.files}


def file_hash(filename):
    """from https://stackoverflow.com/a/44873382/4398037"""
    h = hashlib.sha1()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def get_settings(count):
    if len(sys.argv) != count + 1:
        if count == 1:
            return "sites/workplace"
        elif count == 2:
            return "sites/workplace", "Title"

        print("Please specify {x} parameters".format(x=count))
    if count == 1:
        return sys.argv[1]
    elif count == 2:
        return sys.argv[1], sys.argv[2]


def get_random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
