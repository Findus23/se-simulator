import hashlib
import random
import resource
import string
import sys
from datetime import datetime

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


def prettydate(d):
    diff = datetime.now() - d
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{} minutes ago'.format(int(s / 60))
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{} hours ago'.format(int(s / 3600))


def create_pagination(num_pages, page, padding=2):
    pages = ["1"]
    i = 2
    while i <= num_pages:
        if i < (page - padding - 1):
            pages.append("d")
            i = page - padding
        elif (i > (page + padding)) and (num_pages > (page + padding + 2)):
            pages.append("d")
            i = num_pages
        pages.append(str(i))
        i += 1
    return pages


def rand():
    return random.randint(-2 ** 31, 2 ** 31 - 1)


rating_sql = """
((upvotes + 1.9208) / (upvotes + downvotes) -
1.96 * SQRT((upvotes * downvotes) / (upvotes + downvotes) + 0.9604) /
(upvotes + downvotes)) / (1 + 3.8416 / (upvotes + downvotes))
AS ci_lower_bound
"""


def get_fallback_site():
    return {
        "name": "Stack Exchange",
        "url": "stackexchange.com/",
        "icon_url": "https://cdn.sstatic.net/Sites/stackexchange/img/apple-touch-icon.png",
        "fallback": True,
        "background_color": False,
        "foreground_color": False,
        "primary_color": False
    }


def hex_to_rgb(hex):
    """ https://stackoverflow.com/a/29643643 """
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))


def is_light_color(hex):
    """ https://stackoverflow.com/a/596241 """
    r, g, b = hex_to_rgb(hex[1:])
    brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return brightness > 245


def save_question_count(count):
    with open('count.txt', 'w') as f:
        f.write(str(count))


def load_question_count():
    with open('count.txt', 'r') as f:
        return int(f.readline())
