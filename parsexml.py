import resource
from xml.etree import ElementTree

import jsonlines
from html2text import HTML2Text

import utils
from bs4 import BeautifulSoup

BASEDIR = utils.get_settings(1)

i = 0
iterator = ElementTree.iterparse(BASEDIR + "/Posts.xml")
with jsonlines.open(BASEDIR + '/Questions.jsonl', mode="w") as questions, \
        jsonlines.open(BASEDIR + '/Answers.jsonl', mode="w") as answers, \
        jsonlines.open(BASEDIR + "/Titles.jsonl", "w") as titles:
    for event, element in iterator:
        title = element.get('Title')
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
print("{number} total entries".format(number=i))
print("used {mb}MB".format(mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024))
