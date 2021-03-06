import jsonlines
from lxml import etree

from utils import *


def parse_posts(inputdir, outputdir):
    i = 0
    skipped = 0
    iterator = etree.iterparse(inputdir + "/Posts.xml", events=("start", "end"))
    _, root = next(iterator)
    with jsonlines.open(outputdir + "/Questions.jsonl", mode="w") as questions, \
            jsonlines.open(outputdir + "/Answers.jsonl", mode="w") as answers, \
            jsonlines.open(outputdir + "/Titles.jsonl", "w") as titles:
        for event, element in iterator:
            title = element.get("Title")
            # if element.get("Score") and int(element.get("Score")) <= 10:
            #     skipped += 1
            #     element.clear()
            #     continue
            if title:
                titles.write(title)
            body = element.get("Body")
            if body:
                text = html2text(body)
                if element.get("PostTypeId") == "1":
                    questions.write(text)
                else:
                    answers.write(text)
            element.clear()
            if i % 100 == 0:
                root.clear()
                print(i, skipped, i + skipped, end="\r")
            i += 1
    print_stats(i, skipped)


def parse_comments(inputdir, outputdir):
    i = 0
    iterator = etree.iterparse(inputdir + "/Comments.xml", events=("start", "end"))
    _, root = next(iterator)
    with jsonlines.open(outputdir + "/Comments.jsonl", mode="w") as comments:
        for event, element in iterator:
            text = element.get("Text")
            if text:
                comments.write(text)
            element.clear()
            if i % 100 == 0:
                root.clear()
                print(i, end="\r")
            i += 1
    print_stats(i)


def parse_usernames(inputdir, outputdir):
    i = 0
    iterator = etree.iterparse(inputdir + "/Users.xml", events=("start", "end"))
    _, root = next(iterator)
    with jsonlines.open(outputdir + "/Usernames.jsonl", mode="w") as usernames:
        for event, element in iterator:
            displayname = element.get("DisplayName")
            if displayname:
                usernames.write(displayname)
            element.clear()
            if i % 100 == 0:
                root.clear()
                print(i, end="\r")
            i += 1
    print_stats(i)


if __name__ == "__main__":
    settings = get_settings(1)
    # parse_posts(settings)
    # parse_comments(settings)
    # parse_comments(settings)
