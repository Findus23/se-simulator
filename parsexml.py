import resource
from xml.etree import ElementTree

import jsonlines
from bs4 import BeautifulSoup

import utils


def print_stats(i, skipped=None):
    print("{number} total entries".format(number=i))
    if skipped:
        print("{number} skipped".format(number=skipped))
    print("used {mb}MB".format(mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024))


def parse_posts(basedir):
    i = 0
    skipped = 0
    iterator = ElementTree.iterparse(basedir + "/Posts.xml")
    with jsonlines.open(basedir + '/Questions.jsonl', mode="w") as questions, \
            jsonlines.open(basedir + '/Answers.jsonl', mode="w") as answers, \
            jsonlines.open(basedir + "/Titles.jsonl", "w") as titles:
        for event, element in iterator:
            title = element.get('Title')
            # if element.get('Score') and int(element.get('Score')) > 2:
            #     skipped += 1
            #     continue
            if title:
                titles.write(title)
            body = element.get('Body')
            if body:
                soup = BeautifulSoup(body, "lxml")
                text = soup.get_text()
                if element.get('PostTypeId') == "1":
                    questions.write(text)
                else:
                    answers.write(text)
            element.clear()
            if i % 100 == 0:
                print(i)
            i += 1
    print_stats(i, skipped)


def parse_comments(basedir):
    i = 0
    iterator = ElementTree.iterparse(basedir + "/Comments.xml")
    with jsonlines.open(basedir + '/Comments.jsonl', mode="w") as comments:
        for event, element in iterator:
            text = element.get('Text')
            if text:
                comments.write(text)
            element.clear()
            if i % 100 == 0:
                print(i)
            i += 1
    print_stats(i)


def parse_usernames(basedir):
    i = 0
    iterator = ElementTree.iterparse(basedir + "/Users.xml")
    with jsonlines.open(basedir + '/Usernames.jsonl', mode="w") as usernames:
        for event, element in iterator:
            displayname = element.get('DisplayName')
            if displayname:
                usernames.write(displayname)
            element.clear()
            if i % 100 == 0:
                print(i)
            i += 1
    print_stats(i)


if __name__ == "__main__":
    settings=utils.get_settings(1)
    parse_posts(settings)
    parse_comments(settings)
    parse_comments(settings)
